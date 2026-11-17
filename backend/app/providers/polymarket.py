"""Mercados de predicción de Polymarket vía Gamma API pública (solo lectura)."""
from __future__ import annotations

import json

import httpx

from ..config import config
from ..errors import get_json

FUENTE = "Polymarket"


def _lista_json(valor) -> list:
    """Gamma devuelve outcomes/outcomePrices como cadenas JSON."""
    if isinstance(valor, list):
        return valor
    if isinstance(valor, str) and valor:
        try:
            v = json.loads(valor)
            return v if isinstance(v, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _num(valor) -> float:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def normalizar(m: dict) -> dict:
    nombres = _lista_json(m.get("outcomes"))
    precios = [_num(p) for p in _lista_json(m.get("outcomePrices"))]
    return {
        "id": str(m.get("id", "")),
        "pregunta": m.get("question", ""),
        "slug": m.get("slug", ""),
        "resultados": [{"nombre": n, "probabilidad": p} for n, p in zip(nombres, precios)],
        "volumen": _num(m.get("volumeNum", m.get("volume"))),
        "liquidez": _num(m.get("liquidityNum", m.get("liquidity"))),
        "fecha_fin": m.get("endDate"),
        "url": f"https://polymarket.com/market/{m.get('slug', '')}",
    }


async def mercados(cliente: httpx.AsyncClient, limite: int = 20, busqueda: str = "") -> dict:
    limite = max(1, min(limite, 100))
    # active=true&closed=false filtra mercados abiertos; se piden más para ordenar por volumen aquí.
    crudo = await get_json(cliente, FUENTE, f"{config.polymarket_url}/markets",
                           {"active": "true", "closed": "false", "limit": 200})
    filas = [normalizar(m) for m in crudo if isinstance(m, dict)]
    if busqueda:
        b = busqueda.lower()
        filas = [f for f in filas if b in f["pregunta"].lower()]
    filas.sort(key=lambda f: f["volumen"], reverse=True)
    return {"mercados": filas[:limite], "fuente": FUENTE}
