"""Errores controlados y cliente HTTP con reintentos limitados y espera creciente."""
from __future__ import annotations

import asyncio
import logging

import httpx

log = logging.getLogger("agente")


class ProveedorError(Exception):
    """Falla de una fuente externa (MEXC o Polymarket)."""

    def __init__(self, fuente: str, mensaje: str, status: int = 502):
        super().__init__(f"{fuente}: {mensaje}")
        self.fuente, self.mensaje, self.status = fuente, mensaje, status


class EntradaInvalidaError(Exception):
    """Parámetro rechazado por validación (símbolo o intervalo no permitido)."""


async def get_json(cliente: httpx.AsyncClient, fuente: str, url: str, params: dict | None = None,
                   intentos: int = 3, espera_base: float = 0.5):
    ultimo = "sin respuesta"
    for i in range(intentos):
        try:
            r = await cliente.get(url, params=params)
            if r.status_code == 200:
                return r.json()
            ultimo = f"HTTP {r.status_code}"
            if r.status_code == 429:
                ultimo += " (límite de solicitudes)"
            elif r.status_code < 500:
                break  # error del cliente: reintentar no ayuda
        except httpx.TimeoutException:
            ultimo = "tiempo de espera agotado"
        except httpx.HTTPError as e:
            ultimo = f"{type(e).__name__}: {e}"
        log.warning("%s intento %d/%d falló: %s", fuente, i + 1, intentos, ultimo)
        if i < intentos - 1:
            await asyncio.sleep(espera_base * 2 ** i)
    raise ProveedorError(fuente, f"no disponible después de {intentos} intentos ({ultimo})")
