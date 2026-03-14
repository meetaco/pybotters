"""Signing helpers for Aster API v3."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Mapping, Sequence
from typing import Any

from pybotters._static_dependencies import keccak
from pybotters._static_dependencies.ecdsa import SECP256k1, SigningKey
from pybotters._static_dependencies.ecdsa.util import sigencode_strings_canonize
from pybotters._static_dependencies.ethereum.abi import encode as abi_encode

__all__ = (
    "build_signed_params",
    "get_nonce_us",
    "get_timestamp_ms",
    "normalize_params",
    "sign_params",
)

_DEFAULT_RECV_WINDOW = "50000"
_nonce_lock = threading.Lock()
_last_nonce = 0


def get_timestamp_ms() -> int:
    return int(time.time() * 1000)


def get_nonce_us() -> int:
    global _last_nonce

    now = time.time_ns() // 1_000
    with _nonce_lock:
        if now <= _last_nonce:
            now = _last_nonce + 1
        _last_nonce = now

    return now


def _normalize_scalar(value: Any) -> str:
    return str(value)


def _normalize_nested(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _normalize_nested(item)
            for key, item in sorted(value.items())
            if item is not None
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_nested(item) for item in value]
    return _normalize_scalar(value)


def _normalize_top_level_value(value: Any) -> str:
    normalized = _normalize_nested(value)
    if isinstance(normalized, (dict, list)):
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return normalized


def normalize_params(params: Mapping[str, Any]) -> dict[str, str]:
    return {
        key: _normalize_top_level_value(value)
        for key, value in params.items()
        if value is not None
    }


def sign_params(
    normalized_params: Mapping[str, str],
    user: str,
    signer: str,
    private_key: str,
    nonce: int,
) -> str:
    payload = json.dumps(dict(normalized_params), sort_keys=True, separators=(",", ":"))
    message = abi_encode(
        ["string", "address", "address", "uint256"],
        [payload, user, signer, nonce],
    )
    request_hash = keccak.SHA3(message)
    sign_hash = keccak.SHA3(
        f"\x19Ethereum Signed Message:\n{len(request_hash)}".encode() + request_hash
    )
    signing_key = SigningKey.from_secret_exponent(int(private_key, 16), SECP256k1)
    r_binary, s_binary, v = signing_key.sign_digest_deterministic(
        sign_hash, hashlib.sha256, sigencode_strings_canonize
    )
    return "0x" + (r_binary + s_binary + bytes([27 + v])).hex()


def build_signed_params(
    params: Mapping[str, Any],
    user: str,
    signer: str,
    private_key: str,
    *,
    nonce: int | None = None,
    timestamp: int | None = None,
    recv_window: str = _DEFAULT_RECV_WINDOW,
) -> dict[str, str]:
    signed = normalize_params(params)
    signed.setdefault("recvWindow", recv_window)
    if timestamp is None:
        timestamp = get_timestamp_ms()
    signed.setdefault("timestamp", str(timestamp))

    if nonce is None:
        nonce = get_nonce_us()

    signed["nonce"] = str(nonce)
    signed["user"] = user
    signed["signer"] = signer
    signed["signature"] = sign_params(signed, user, signer, private_key, nonce)

    return signed
