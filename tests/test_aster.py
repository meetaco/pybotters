import pybotters
import pybotters.helpers.aster


def test_aster_normalize_params():
    actual = pybotters.helpers.aster.normalize_params(
        {
            "symbol": "SANDUSDT",
            "batchOrders": [
                {"price": 0.5, "side": "BUY"},
                {"price": 0.4, "side": "SELL"},
            ],
        }
    )

    assert actual == {
        "symbol": "SANDUSDT",
        "batchOrders": '[{"price":"0.5","side":"BUY"},{"price":"0.4","side":"SELL"}]',
    }


def test_aster_get_nonce_us_monotonic(mocker, monkeypatch):
    mocker.patch("time.time_ns", return_value=1_000)
    monkeypatch.setattr(pybotters.helpers.aster, "_last_nonce", 1)

    actual = pybotters.helpers.aster.get_nonce_us()

    assert actual == 2


def test_aster_spot_datastore_endpoints():
    assert pybotters.AsterSpotDataStore._ORDERBOOK_INIT_ENDPOINT == "/api/v3/depth"
    assert pybotters.AsterSpotDataStore._ORDER_INIT_ENDPOINT == "/api/v3/openOrders"
    assert pybotters.AsterSpotDataStore._LISTENKEY_INIT_ENDPOINT == "/api/v3/listenKey"
    assert pybotters.AsterSpotDataStore._KLINE_INIT_ENDPOINT == "/api/v3/klines"
    assert pybotters.AsterSpotDataStore._ACCOUNT_INIT_ENDPOINT == "/api/v3/account"
    assert pybotters.AsterSpotDataStore._OCOORDER_INIT_ENDPOINT is None


def test_aster_usdsm_datastore_endpoints():
    assert pybotters.AsterUSDSMDataStore._ORDERBOOK_INIT_ENDPOINT == "/fapi/v3/depth"
    assert pybotters.AsterUSDSMDataStore._BALANCE_INIT_ENDPOINT == "/fapi/v3/balance"
    assert pybotters.AsterUSDSMDataStore._ORDER_INIT_ENDPOINT == "/fapi/v3/openOrders"
    assert (
        pybotters.AsterUSDSMDataStore._LISTENKEY_INIT_ENDPOINT == "/fapi/v3/listenKey"
    )
    assert pybotters.AsterUSDSMDataStore._KLINE_INIT_ENDPOINT == "/fapi/v3/klines"
    assert (
        pybotters.AsterUSDSMDataStore._POSITION_INIT_ENDPOINT == "/fapi/v3/positionRisk"
    )
    assert pybotters.AsterUSDSMDataStore._COMPOSITEINDEX_INIT_ENDPOINT is None
