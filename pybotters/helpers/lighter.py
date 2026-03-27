"""Authentication helpers for the Lighter API."""

from __future__ import annotations

import asyncio
import importlib
import inspect
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import aiohttp

_DEFAULT_AUTH_TOKEN_EXPIRY = 10 * 60
_AUTH_TOKEN_REFRESH_MARGIN = 30

HOSTS = frozenset(
    {
        "mainnet.zklighter.elliot.ai",
        "testnet.zklighter.elliot.ai",
    }
)

PROTECTED_WS_CHANNELS = frozenset(
    {
        "account_market",
        "account_tx",
        "account_all_orders",
        "pool_data",
        "pool_info",
        "notification",
        "account_orders",
        "account_all_trades",
        "account_all_positions",
        "account_all_assets",
        "account_spot_avg_entry_prices",
    }
)


class LighterAuthError(RuntimeError):
    """Raised when pybotters cannot create a Lighter auth token."""


def is_protected_channel(channel: str) -> bool:
    return channel.split(":", 1)[0].split("/", 1)[0] in PROTECTED_WS_CHANNELS


def _coerce_str(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode()
    return str(value)


def _coerce_int(value: Any) -> int:
    if isinstance(value, bytes):
        value = value.decode()
    return int(value)


def _base_url_from_host(host: str | None) -> str:
    if host not in HOSTS:
        raise LighterAuthError(f"Unsupported Lighter host: {host!r}")
    return f"https://{host}"


def _build_signer_client(
    session: "aiohttp.ClientSession",
    api_name: str,
    host: str | None,
) -> tuple[object, int]:
    try:
        lighter_sdk = importlib.import_module("lighter")
    except ImportError as e:
        raise LighterAuthError(
            "lighter-sdk is required for automatic Lighter auth token generation. "
            "Install lighter-sdk or pass a pre-generated auth token instead."
        ) from e

    credentials = session.__dict__["_apis"][api_name]
    account_index = _coerce_int(credentials[0])
    api_key_index = _coerce_int(credentials[1])
    private_key = _coerce_str(credentials[2])

    client = lighter_sdk.SignerClient(
        url=_base_url_from_host(host),
        account_index=account_index,
        api_private_keys={api_key_index: private_key},
    )
    return client, api_key_index


def get_auth_token(
    session: "aiohttp.ClientSession",
    api_name: str,
    host: str | None,
    *,
    deadline: int = _DEFAULT_AUTH_TOKEN_EXPIRY,
) -> str:
    credentials = session.__dict__["_apis"][api_name]

    # Pre-generated auth token or read-only token.
    if len(credentials) == 1 or (
        len(credentials) >= 3 and credentials[1] == b"" and credentials[2] == ""
    ):
        return _coerce_str(credentials[0])

    cache_key = (api_name, host)
    cache = session.__dict__.setdefault("_lighter_auth_tokens", {})
    now = time.time()
    cached = cache.get(cache_key)
    if cached and cached["expires_at"] - _AUTH_TOKEN_REFRESH_MARGIN > now:
        return cached["token"]

    clients = session.__dict__.setdefault("_lighter_sdk_clients", {})
    signer_client = clients.get(cache_key)
    api_key_index = _coerce_int(credentials[1])
    if signer_client is None:
        signer_client, api_key_index = _build_signer_client(session, api_name, host)
        clients[cache_key] = signer_client

    token, error = signer_client.create_auth_token_with_expiry(  # type: ignore[attr-defined]
        deadline=deadline,
        api_key_index=api_key_index,
    )
    if error:
        raise LighterAuthError(f"Failed to create Lighter auth token: {error}")
    if not token:
        raise LighterAuthError("Failed to create Lighter auth token: empty token")

    cache[cache_key] = {
        "token": token,
        "expires_at": now + deadline,
    }
    return token


async def close_sdk_clients(session: "aiohttp.ClientSession") -> None:
    clients = session.__dict__.pop("_lighter_sdk_clients", {})
    if not clients:
        return

    closers = []
    for client in clients.values():
        close = getattr(client, "close", None)
        if close is None:
            continue
        result = close()
        if inspect.isawaitable(result):
            closers.append(result)

    if closers:
        await asyncio.gather(*closers, return_exceptions=True)
