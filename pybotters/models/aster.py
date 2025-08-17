from __future__ import annotations

from .binance import (
    BinanceDataStoreBase,
    BinanceSpotDataStore,
    BinanceUSDSMDataStore,
    BinanceCOINMDataStore,
    BinanceFuturesDataStoreBase,
)


class AsterDataStoreBase(BinanceDataStoreBase):
    """Aster の DataStoreCollection ベースクラス

    Note: Aster APIはBinance API完全互換のため、BinanceDataStoreBaseを継承
    """

    pass


class AsterFuturesDataStoreBase(BinanceFuturesDataStoreBase):
    """Aster 先物の DataStoreCollection ベースクラス

    Note: Aster APIはBinance API完全互換のため、BinanceFuturesDataStoreBaseを継承
    """

    pass


class AsterSpotDataStore(BinanceSpotDataStore):
    """Aster Spot の DataStoreCollection クラス

    Note: Aster APIはBinance API完全互換のため、BinanceSpotDataStoreを継承
    """

    pass


class AsterUSDSMDataStore(BinanceUSDSMDataStore):
    """Aster USDⓈ-M の DataStoreCollection クラス

    Note: Aster APIはBinance API完全互換のため、BinanceUSDSMDataStoreを継承
    """

    pass


class AsterCOINMDataStore(BinanceCOINMDataStore):
    """Aster COIN-M の DataStoreCollection クラス

    Note: Aster APIはBinance API完全互換のため、BinanceCOINMDataStoreを継承
    """

    pass
