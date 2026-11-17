"""Pruebas con transportes simulados: no salen a internet."""
import json
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main
from app.config import config


def cliente_con(handler):
    mock = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def _dep():
        yield mock

    main.app.dependency_overrides[main.cliente_http] = _dep
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def limpiar():
    yield
    main.app.dependency_overrides.clear()


def test_version_y_tecnologias():
    with TestClient(main.app) as c:
        r = c.get("/api/version").json()
    assert r["version"] == config.version == open(config_path()).read().strip()
    assert r["trading_real"] is False
    assert "Vue 3" in r["tecnologias"]["frontend"]


def config_path():
    from app.config import RAIZ
    return RAIZ / "VERSION"


def test_mexc_velas_marca_vela_abierta():
    ahora = int(time.time() * 1000)
    dia = 86_400_000

    def handler(req: httpx.Request):
        assert req.url.path == "/api/v3/klines"
        assert req.url.params["symbol"] == "BTCUSDT"
        return httpx.Response(200, json=[
            [ahora - dia, "90000", "91000", "89000", "90500", "10", ahora - 1, "900000"],
            [ahora - 2 * dia, "88000", "90100", "87900", "90000", "12", ahora - dia - 1, "1000000"],
            [ahora, "90500", "90600", "90400", "90550", "1", ahora + dia, "90000"],
        ])

    r = cliente_con(handler).get("/api/mexc/velas?simbolo=btcusdt&limite=3")
    assert r.status_code == 200
    velas = r.json()["velas"]
    assert [v["apertura_ms"] for v in velas] == sorted(v["apertura_ms"] for v in velas)
    assert [v["cerrada"] for v in velas] == [True, True, False]


def test_mexc_ticker():
    def handler(req):
        return httpx.Response(200, json={"symbol": "BTCUSDT", "lastPrice": "101", "openPrice": "100",
                                         "priceChangePercent": "0.01", "highPrice": "102",
                                         "lowPrice": "99", "volume": "5"})

    r = cliente_con(handler).get("/api/mexc/ticker").json()
    assert r["ultimo"] == 101 and round(r["cambio_pct"], 6) == 1.0


def test_simbolo_no_permitido():
    r = cliente_con(lambda req: httpx.Response(200, json=[])).get("/api/mexc/velas?simbolo=DOGEUSDT")
    assert r.status_code == 422 and "no permitido" in r.json()["error"]


def test_mexc_limite_de_solicitudes_responde_502():
    llamadas = []

    def handler(req):
        llamadas.append(1)
        return httpx.Response(429)

    r = cliente_con(handler).get("/api/mexc/ticker")
    assert r.status_code == 502
    assert "límite de solicitudes" in r.json()["error"] and len(llamadas) == 3


def test_polymarket_normaliza_y_ordena():
    def handler(req):
        assert req.url.params["active"] == "true" and req.url.params["closed"] == "false"
        return httpx.Response(200, json=[
            {"id": 1, "question": "¿A?", "slug": "a", "outcomes": json.dumps(["Yes", "No"]),
             "outcomePrices": json.dumps(["0.2", "0.8"]), "volumeNum": 10},
            {"id": 2, "question": "¿B?", "slug": "b", "outcomes": json.dumps(["Yes", "No"]),
             "outcomePrices": json.dumps(["0.6", "0.4"]), "volume": "500"},
        ])

    r = cliente_con(handler).get("/api/polymarket/mercados?limite=5").json()
    assert [m["id"] for m in r["mercados"]] == ["2", "1"]
    assert r["mercados"][0]["resultados"][0] == {"nombre": "Yes", "probabilidad": 0.6}


def test_ruta_protegida_rechaza_clave(monkeypatch):
    monkeypatch.setattr(main, "config", type(config)(api_key="secreta"))
    with TestClient(main.app) as c:
        assert c.get("/api/control/estado").status_code == 401
        assert c.get("/api/control/estado", headers={"X-API-Key": "mala"}).status_code == 401
        assert c.get("/api/control/estado", headers={"X-API-Key": "secreta"}).status_code == 200
