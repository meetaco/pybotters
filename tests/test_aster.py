import pybotters
import pybotters.auth
import pybotters.helpers.aster
import pytest
from yarl import URL


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


def test_aster_encode_signing_message_preserves_param_order():
    actual = pybotters.helpers.aster.encode_signing_message(
        {
            "symbol": "ASTERUSDT",
            "type": "LIMIT",
            "side": "BUY",
            "timeInForce": "GTC",
            "quantity": "100",
            "price": "0.4",
            "nonce": "123456",
            "user": "0xuser",
            "signer": "0xsigner",
        }
    )

    assert (
        actual
        == "symbol=ASTERUSDT&type=LIMIT&side=BUY&timeInForce=GTC&quantity=100&price=0.4&nonce=123456&user=0xuser&signer=0xsigner"
    )


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


@pytest.mark.asyncio
async def test_aster_listenkey_keepalive_omits_listenkey_param(monkeypatch):
    class DummyResponse:
        async def text(self):
            return "{}"

        def raise_for_status(self):
            return None

    class DummyContextManager:
        async def __aenter__(self):
            return DummyResponse()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class DummySession:
        def __init__(self):
            self.closed = False
            self.calls = []

        def put(self, url, **kwargs):
            self.calls.append((url, kwargs))
            return DummyContextManager()

    session = DummySession()
    datastore = pybotters.AsterSpotDataStore()
    datastore.listenkey = "existing"

    async def fake_sleep(_):
        session.closed = True

    monkeypatch.setattr("asyncio.sleep", fake_sleep)

    await datastore._listenkey(URL("https://sapi.asterdex.com/api/v3/listenKey"), session)

    assert len(session.calls) == 1
    _, kwargs = session.calls[0]
    assert kwargs["params"] is None
    assert kwargs["auth"] is pybotters.auth.Auth
