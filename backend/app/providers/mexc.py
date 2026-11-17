"""Datos públicos de MEXC Spot (solo lectura; sin claves de trading)."""
from __future__ import annotations

import time

import httpx

from ..config import config
from ..errors import EntradaInvalidaError, get_json

FUENTE = "MEXC"
INTERVALOS = {"1d", "4h", "60m"}


def validar_simbolo(simbolo: str) -> str:
    s = simbolo.upper()
    if s not in config.simbolos_permitidos:
        raise EntradaInvalidaError(
            f"Símbolo '{simbolo}' no permitido. Permitidos: {', '.join(config.simbolos_permitidos)}")
    return s


async def ticker_24h(cliente: httpx.AsyncClient, simbolo: str) -> dict:
    s = validar_simbolo(simbolo)
    d = await get_json(cliente, FUENTE, f"{config.mexc_url}/api/v3/ticker/24hr", {"symbol": s})
    return {
        "simbolo": s,
        "ultimo": float(d["lastPrice"]),
        # Se calcula con apertura y último precio para no depender de la escala de priceChangePercent.
        "cambio_pct": (float(d["lastPrice"]) / float(d["openPrice"]) - 1) * 100 if float(d.get("openPrice") or 0) else None,
        "maximo": float(d["highPrice"]),
        "minimo": float(d["lowPrice"]),
        "volumen": float(d["volume"]),
        "fuente": FUENTE,
    }


async def velas(cliente: httpx.AsyncClient, simbolo: str, intervalo: str = "1d", limite: int = 30) -> dict:
    s = validar_simbolo(simbolo)
    if intervalo not in INTERVALOS:
        raise EntradaInvalidaError(f"Intervalo '{intervalo}' no permitido. Use: {', '.join(sorted(INTERVALOS))}")
    limite = max(1, min(limite, 1000))
    crudo = await get_json(cliente, FUENTE, f"{config.mexc_url}/api/v3/klines",
                           {"symbol": s, "interval": intervalo, "limit": limite})
    ahora_ms = int(time.time() * 1000)
    filas = [{
        "apertura_ms": int(k[0]),
        "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4]),
        "volumen": float(k[5]),
        "cierre_ms": int(k[6]),
        "cerrada": int(k[6]) < ahora_ms,  # una vela abierta no es definitiva
    } for k in crudo]
    filas.sort(key=lambda f: f["apertura_ms"])
    return {"simbolo": s, "intervalo": intervalo, "velas": filas, "fuente": FUENTE}
