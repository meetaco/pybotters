from __future__ import annotations

from .binance import (
    BinanceCOINMDataStore,
    BinanceDataStoreBase,
    BinanceFuturesDataStoreBase,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
)


class AsterDataStoreBase(BinanceDataStoreBase):
    """Aster の DataStoreCollection ベースクラス

    Note: Aster は WebSocket フォーマットが Binance 系に近いため、
    BinanceDataStoreBase をベースに Aster 固有の REST エンドポイントを上書きする。
    """

    pass


class AsterFuturesDataStoreBase(BinanceFuturesDataStoreBase):
    """Aster 先物の DataStoreCollection ベースクラス

    Note: Aster v3 は WebSocket フォーマットが Binance 系に近いため、
    BinanceFuturesDataStoreBase をベースに REST エンドポイントを上書きする。
    """

    pass


class AsterSpotDataStore(BinanceSpotDataStore):
    """Aster Spot の DataStoreCollection クラス

    Note: Spot v3 の REST エンドポイントに合わせて初期化先を上書きする。
    """

    _ORDERBOOK_INIT_ENDPOINT = "/api/v3/depth"
    _ORDER_INIT_ENDPOINT = "/api/v3/openOrders"
    _LISTENKEY_INIT_ENDPOINT = "/api/v3/listenKey"
    _KLINE_INIT_ENDPOINT = "/api/v3/klines"
    _ACCOUNT_INIT_ENDPOINT = "/api/v3/account"
    _OCOORDER_INIT_ENDPOINT = None


class AsterUSDSMDataStore(BinanceUSDSMDataStore):
    """Aster USDⓈ-M の DataStoreCollection クラス

    Note: Futures v3 の REST エンドポイントに合わせて初期化先を上書きする。
    """

    _ORDERBOOK_INIT_ENDPOINT = "/fapi/v3/depth"
    _BALANCE_INIT_ENDPOINT = "/fapi/v3/balance"
    _ORDER_INIT_ENDPOINT = "/fapi/v3/openOrders"
    _LISTENKEY_INIT_ENDPOINT = "/fapi/v3/listenKey"
    _KLINE_INIT_ENDPOINT = "/fapi/v3/klines"
    _POSITION_INIT_ENDPOINT = "/fapi/v3/positionRisk"
    _COMPOSITEINDEX_INIT_ENDPOINT = None


class AsterCOINMDataStore(BinanceCOINMDataStore):
    """Aster COIN-M の DataStoreCollection クラス

    Note: 公開されている Aster v3 docs には COIN-M 用の初期化 endpoint が
    ないため、現時点では BinanceCOINMDataStore の既定値をそのまま使う。
    """

    pass
