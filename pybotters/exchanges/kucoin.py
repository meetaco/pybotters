from __future__ import annotations

import uuid
from typing import Any

import aiohttp

KUCOIN_WS_HOSTS = {
    "ws-api-spot.kucoin.com",
    "ws-api-futures.kucoin.com",
}


def is_kucoin_ws_host(host: str | None) -> bool:
    return host in KUCOIN_WS_HOSTS


def base_url_from_ws_host(ws_host: str | None) -> str | None:
    if ws_host == "ws-api-spot.kucoin.com":
        return "https://api.kucoin.com"
    if ws_host == "ws-api-futures.kucoin.com":
        return "https://api-futures.kucoin.com"
    return None


def build_ws_endpoint(
    data: dict[str, Any], *, heartbeat_hosts: set[str] | None = None
) -> str:
    token = data["token"]
    servers = data["instanceServers"]
    connect_id = str(uuid.uuid4())
    endpoint = None

    if heartbeat_hosts:
        for server in servers:
            host = aiohttp.typedefs.URL(server["endpoint"]).host
            if host in heartbeat_hosts:
                endpoint = server["endpoint"]
                break

    if endpoint is None:
        endpoint = servers[0]["endpoint"]

    return f"{endpoint}?token={token}&acceptUserMessage=true&connectId={connect_id}"


async def refresh_ws_endpoint(
    session: aiohttp.ClientSession,
    ws_url: str,
    *,
    auth_class: type | None,
    heartbeat_hosts: set[str] | None = None,
) -> str:
    host = aiohttp.typedefs.URL(ws_url).host
    base_url = base_url_from_ws_host(host)
    if base_url is None:
        raise RuntimeError(f"Unexpected KuCoin WS host: {host}")

    has_creds = "kucoin" in session.__dict__.get("_apis", {})
    path = "/api/v1/bullet-private" if has_creds else "/api/v1/bullet-public"
    auth = auth_class if has_creds else None
    url = f"{base_url}{path}"

    async with session.post(url, auth=auth) as resp:
        data = await resp.json()
        if resp.status != 200:
            raise RuntimeError(f"KuCoin token refresh failed: {data}")

    return build_ws_endpoint(data["data"], heartbeat_hosts=heartbeat_hosts)
