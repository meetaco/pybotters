from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from ..store import DataStore, DataStoreCollection

if TYPE_CHECKING:
    from ..typedefs import Item
    from ..ws import ClientWebSocketResponse

logger = logging.getLogger(__name__)


def _split_channel(channel: str) -> tuple[str, str]:
    prefix, sep, suffix = channel.partition(":")
    if sep:
        return prefix, suffix

    prefix, sep, suffix = channel.partition("/")
    if sep:
        return prefix, suffix

    return channel, ""


def _channel_parts(channel: str) -> list[str]:
    return [part for part in _split_channel(channel)[1].split("/") if part]


def _channel_int(channel: str, index: int = 0) -> int | None:
    parts = _channel_parts(channel)
    if len(parts) <= index:
        return None
    try:
        return int(parts[index])
    except ValueError:
        return None


def _is_snapshot(msg: Item) -> bool:
    return str(msg.get("type", "")).startswith("subscribed/")


class LighterDataStore(DataStoreCollection):
    """DataStoreCollection for Lighter.

    https://apidocs.lighter.xyz/docs/websocket-reference
    """

    def _init(self) -> None:
        self._create("orderbook", datastore_class=OrderBook)
        self._create("ticker", datastore_class=Ticker)
        self._create("market_stats", datastore_class=MarketStats)
        self._create("trades", datastore_class=Trades)
        self._create("account_all", datastore_class=AccountAll)
        self._create("account_market", datastore_class=AccountMarket)
        self._create("account_stats", datastore_class=AccountStats)
        self._create("account_tx", datastore_class=AccountTx)
        self._create("account_all_orders", datastore_class=AccountAllOrders)
        self._create("height", datastore_class=Height)
        self._create("pool_data", datastore_class=PoolData)
        self._create("pool_info", datastore_class=PoolInfo)
        self._create("notification", datastore_class=Notification)
        self._create("account_orders", datastore_class=AccountOrders)
        self._create("account_all_trades", datastore_class=AccountAllTrades)
        self._create("account_all_positions", datastore_class=AccountAllPositions)
        self._create("spot_market_stats", datastore_class=SpotMarketStats)
        self._create("account_all_assets", datastore_class=AccountAllAssets)
        self._create(
            "account_spot_avg_entry_prices",
            datastore_class=AccountSpotAvgEntryPrices,
        )

    def _onmessage(self, msg: Item, ws: ClientWebSocketResponse | None = None) -> None:
        if not isinstance(msg, dict):
            return

        type_ = msg.get("type")
        if type_ in {"connected", "ping", "pong"}:
            return
        if type_ == "error":
            logger.warning(msg)
            return

        channel = msg.get("channel")
        if not isinstance(channel, str):
            return

        prefix, _ = _split_channel(channel)

        if prefix == "order_book":
            self.orderbook._onmessage(msg)
        elif prefix == "ticker":
            self.ticker._onmessage(msg)
        elif prefix == "market_stats":
            self.market_stats._onmessage(msg)
        elif prefix == "trade":
            self.trades._onmessage(msg)
        elif prefix == "account_all":
            self.account_all._onmessage(msg)
        elif prefix == "account_market":
            self.account_market._onmessage(msg)
        elif prefix == "user_stats":
            self.account_stats._onmessage(msg)
        elif prefix == "account_tx":
            self.account_tx._onmessage(msg)
        elif prefix == "account_all_orders":
            self.account_all_orders._onmessage(msg)
        elif prefix == "height":
            self.height._onmessage(msg)
        elif prefix == "pool_data":
            self.pool_data._onmessage(msg)
        elif prefix == "pool_info":
            self.pool_info._onmessage(msg)
        elif prefix == "notification":
            self.notification._onmessage(msg)
        elif prefix == "account_orders":
            self.account_orders._onmessage(msg)
        elif prefix == "account_all_trades":
            self.account_all_trades._onmessage(msg)
        elif prefix == "account_all_positions":
            self.account_all_positions._onmessage(msg)
        elif prefix == "spot_market_stats":
            self.spot_market_stats._onmessage(msg)
        elif prefix == "account_all_assets":
            self.account_all_assets._onmessage(msg)
        elif prefix == "account_spot_avg_entry_prices":
            self.account_spot_avg_entry_prices._onmessage(msg)

    @property
    def orderbook(self) -> OrderBook:
        return self._get("orderbook", OrderBook)

    @property
    def ticker(self) -> Ticker:
        return self._get("ticker", Ticker)

    @property
    def market_stats(self) -> MarketStats:
        return self._get("market_stats", MarketStats)

    @property
    def trades(self) -> Trades:
        return self._get("trades", Trades)

    @property
    def account_all(self) -> AccountAll:
        return self._get("account_all", AccountAll)

    @property
    def account_market(self) -> AccountMarket:
        return self._get("account_market", AccountMarket)

    @property
    def account_stats(self) -> AccountStats:
        return self._get("account_stats", AccountStats)

    @property
    def account_tx(self) -> AccountTx:
        return self._get("account_tx", AccountTx)

    @property
    def account_all_orders(self) -> AccountAllOrders:
        return self._get("account_all_orders", AccountAllOrders)

    @property
    def height(self) -> Height:
        return self._get("height", Height)

    @property
    def pool_data(self) -> PoolData:
        return self._get("pool_data", PoolData)

    @property
    def pool_info(self) -> PoolInfo:
        return self._get("pool_info", PoolInfo)

    @property
    def notification(self) -> Notification:
        return self._get("notification", Notification)

    @property
    def account_orders(self) -> AccountOrders:
        return self._get("account_orders", AccountOrders)

    @property
    def account_all_trades(self) -> AccountAllTrades:
        return self._get("account_all_trades", AccountAllTrades)

    @property
    def account_all_positions(self) -> AccountAllPositions:
        return self._get("account_all_positions", AccountAllPositions)

    @property
    def spot_market_stats(self) -> SpotMarketStats:
        return self._get("spot_market_stats", SpotMarketStats)

    @property
    def account_all_assets(self) -> AccountAllAssets:
        return self._get("account_all_assets", AccountAllAssets)

    @property
    def account_spot_avg_entry_prices(self) -> AccountSpotAvgEntryPrices:
        return self._get(
            "account_spot_avg_entry_prices",
            AccountSpotAvgEntryPrices,
        )


class OrderBook(DataStore):
    _KEYS = ["market_id", "side", "price"]

    def _init(self) -> None:
        self.offsets: dict[int, int] = {}
        self.nonces: dict[int, int] = {}
        self.begin_nonces: dict[int, int] = {}
        self.timestamps: dict[int, int] = {}

    def sorted(
        self,
        market_id: int | None = None,
        limit: int | None = None,
    ) -> dict[str, list[Item]]:
        query = {"market_id": market_id} if market_id is not None else None
        return self._sorted(
            item_key="side",
            item_asc_key="asks",
            item_desc_key="bids",
            sort_key="price",
            query=query,
            limit=limit,
        )

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        market_id = _channel_int(channel)
        payload = msg.get("order_book")
        if market_id is None or not isinstance(payload, dict):
            return

        self.offsets[market_id] = cast(
            "int", payload.get("offset", msg.get("offset", 0))
        )
        self.nonces[market_id] = cast("int", payload.get("nonce", 0))
        self.begin_nonces[market_id] = cast("int", payload.get("begin_nonce", 0))
        self.timestamps[market_id] = cast("int", msg.get("timestamp", 0))

        if _is_snapshot(msg):
            self._find_and_delete({"market_id": market_id})

        for side_name in ("asks", "bids"):
            side = cast("list[dict[str, Any]]", payload.get(side_name, []))
            for level in side:
                item = {
                    "market_id": market_id,
                    "side": side_name,
                    "price": level["price"],
                    "size": level["size"],
                }
                if str(level["size"]) == "0":
                    self._delete([item])
                else:
                    self._update([item])


class Ticker(DataStore):
    _KEYS = ["market_id"]

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        payload = msg.get("ticker")
        if not isinstance(payload, dict):
            return

        market_id = _channel_int(channel)
        if market_id is None:
            market_id = cast("int | None", payload.get("market_id"))
        if market_id is None:
            return

        item = dict(payload)
        item["market_id"] = market_id
        item["channel"] = channel
        item["nonce"] = msg.get("nonce")
        item["timestamp"] = msg.get("timestamp")
        self._update([item])


class MarketStats(DataStore):
    _KEYS = ["market_id"]

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        payload = msg.get("market_stats")
        if not isinstance(payload, dict):
            return

        items: list[Item] = []
        if payload and all(isinstance(v, dict) for v in payload.values()):
            for market_id, stats in cast("dict[str, dict[str, Any]]", payload).items():
                item = dict(stats)
                item["market_id"] = int(market_id)
                item["channel"] = channel
                item["timestamp"] = msg.get("timestamp")
                items.append(item)
        else:
            item = dict(payload)
            market_id_val = cast("int | None", payload.get("market_id"))
            if market_id_val is None:
                market_id_val = _channel_int(channel)
            if market_id_val is None:
                return
            item["market_id"] = market_id_val
            item["channel"] = channel
            item["timestamp"] = msg.get("timestamp")
            items.append(item)

        self._update(items)


class SpotMarketStats(DataStore):
    _KEYS = ["market_id"]

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        payload = msg.get("spot_market_stats")
        if not isinstance(payload, dict):
            return

        items: list[Item] = []
        if payload and all(isinstance(v, dict) for v in payload.values()):
            for market_id, stats in cast("dict[str, dict[str, Any]]", payload).items():
                item = dict(stats)
                item["market_id"] = int(market_id)
                item["channel"] = channel
                item["timestamp"] = msg.get("timestamp")
                items.append(item)
        else:
            item = dict(payload)
            market_id_val = cast("int | None", payload.get("market_id"))
            if market_id_val is None:
                market_id_val = _channel_int(channel)
            if market_id_val is None:
                return
            item["market_id"] = market_id_val
            item["channel"] = channel
            item["timestamp"] = msg.get("timestamp")
            items.append(item)

        self._update(items)


class Trades(DataStore):
    _KEYS = ["market_id", "trade_id_str", "liquidation"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        market_id = _channel_int(channel)
        if market_id is None:
            return

        items: list[Item] = []
        for key, liquidation in (("trades", False), ("liquidation_trades", True)):
            for trade in cast("list[dict[str, Any]]", msg.get(key, [])):
                item = dict(trade)
                item.setdefault("market_id", market_id)
                item.setdefault("trade_id_str", str(item.get("trade_id", "")))
                item["channel"] = channel
                item["liquidation"] = liquidation
                items.append(item)

        self._insert(items)


class AccountAll(DataStore):
    _KEYS = ["account"]

    def _onmessage(self, msg: Item) -> None:
        if "account" in msg:
            self._update([msg])


class AccountMarket(DataStore):
    _KEYS = ["account", "market_id"]

    def _onmessage(self, msg: Item) -> None:
        if "account" not in msg:
            return
        item = dict(msg)
        market_id = _channel_int(cast("str", msg["channel"]), 0)
        if market_id is not None:
            item["market_id"] = market_id
        self._update([item])


class AccountStats(DataStore):
    _KEYS = ["account_index"]

    def _onmessage(self, msg: Item) -> None:
        item = dict(msg)
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return
        item["account_index"] = account_index
        self._update([item])


class AccountTx(DataStore):
    _KEYS = ["hash"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        account_index = _channel_int(channel)
        items: list[Item] = []

        for tx in cast("list[dict[str, Any]]", msg.get("txs", [])):
            item = dict(tx)
            item.setdefault("hash", item.get("tx_hash"))
            item["channel"] = channel
            if account_index is not None:
                item.setdefault("account_index", account_index)
            items.append(item)

        self._update(items)


class AccountAllOrders(DataStore):
    _KEYS = ["account_index", "market_id", "order_index"]

    def _onmessage(self, msg: Item) -> None:
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return

        orders_by_market = msg.get("orders", {})
        if not isinstance(orders_by_market, dict):
            return

        # Full replacement: each message contains the complete current state
        self._find_and_delete({"account_index": account_index})

        items: list[Item] = []
        for market_id_str, orders in cast(
            "dict[str, list[dict[str, Any]]]", orders_by_market
        ).items():
            market_id = int(market_id_str)
            for order in orders:
                item = dict(order)
                item["account_index"] = account_index
                item["market_id"] = market_id
                items.append(item)

        self._update(items)


class Height(DataStore):
    _KEYS = ["channel"]

    def _onmessage(self, msg: Item) -> None:
        self._update([msg])


class PoolData(DataStore):
    _KEYS = ["account"]

    def _onmessage(self, msg: Item) -> None:
        if "account" in msg:
            self._update([msg])


class PoolInfo(DataStore):
    _KEYS = ["account_index"]

    def _onmessage(self, msg: Item) -> None:
        item = dict(msg)
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return
        item["account_index"] = account_index
        self._update([item])


class Notification(DataStore):
    _KEYS = ["account_index", "id"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        channel = cast("str", msg["channel"])
        account_index = _channel_int(channel)
        if account_index is None:
            return

        if _is_snapshot(msg):
            self._find_and_delete({"account_index": account_index})

        items: list[Item] = []
        for notif in cast("list[dict[str, Any]]", msg.get("notifs", [])):
            item = dict(notif)
            item["account_index"] = account_index
            item["channel"] = channel
            items.append(item)

        self._update(items)


class AccountOrders(DataStore):
    _KEYS = ["account_index", "market_id"]

    def _onmessage(self, msg: Item) -> None:
        item = dict(msg)
        channel = cast("str", msg["channel"])
        item["market_id"] = _channel_int(channel, 0)
        account_index = cast("int | None", msg.get("account"))
        if account_index is None:
            account_index = _channel_int(channel, 1)
        if account_index is None:
            return
        item["account_index"] = account_index
        self._update([item])


class AccountAllTrades(DataStore):
    _KEYS = ["account_index", "market_id", "trade_id"]
    _MAXLEN = 99999

    def _onmessage(self, msg: Item) -> None:
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return

        trades_by_market = msg.get("trades", {})
        if not isinstance(trades_by_market, dict):
            return  # initial subscription may send an empty list

        items: list[Item] = []
        for market_id_str, trades in cast(
            "dict[str, list[dict[str, Any]]]", trades_by_market
        ).items():
            market_id = int(market_id_str)
            for trade in trades:
                item = dict(trade)
                item["account_index"] = account_index
                item["market_id"] = market_id
                items.append(item)

        self._insert(items)


class AccountAllPositions(DataStore):
    _KEYS = ["account_index", "market_id"]

    def _onmessage(self, msg: Item) -> None:
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return

        positions_by_market = msg.get("positions", {})
        if not isinstance(positions_by_market, dict):
            return

        # Full replacement: each message contains the complete current state
        self._find_and_delete({"account_index": account_index})

        items: list[Item] = []
        for market_id_str, position in cast(
            "dict[str, dict[str, Any]]", positions_by_market
        ).items():
            item = dict(position)
            item["account_index"] = account_index
            item["market_id"] = int(market_id_str)
            items.append(item)

        self._update(items)


class AccountAllAssets(DataStore):
    _KEYS = ["account_index", "asset_id"]

    def _onmessage(self, msg: Item) -> None:
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return

        assets_by_index = msg.get("assets", {})
        if not isinstance(assets_by_index, dict):
            return

        # Full replacement: each message contains the complete current state
        self._find_and_delete({"account_index": account_index})

        items: list[Item] = []
        for asset_index_str, asset in cast(
            "dict[str, dict[str, Any]]", assets_by_index
        ).items():
            item = dict(asset)
            item["account_index"] = account_index
            item.setdefault("asset_id", int(asset_index_str))
            items.append(item)

        self._update(items)


class AccountSpotAvgEntryPrices(DataStore):
    _KEYS = ["account_index", "asset_id"]

    def _onmessage(self, msg: Item) -> None:
        account_index = _channel_int(cast("str", msg["channel"]))
        if account_index is None:
            return

        prices_by_index = msg.get("avg_entry_prices", {})
        if not isinstance(prices_by_index, dict):
            return

        items: list[Item] = []
        for asset_index_str, price_data in cast(
            "dict[str, dict[str, Any]]", prices_by_index
        ).items():
            item = dict(price_data)
            item["account_index"] = account_index
            item.setdefault("asset_id", int(asset_index_str))
            items.append(item)

        self._update(items)
