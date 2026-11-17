"""API del Agente IA Finanzas — v0.1 (solo lectura de datos de mercado)."""
from __future__ import annotations

import logging
import secrets
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import config
from .errors import EntradaInvalidaError, ProveedorError
from .providers import mexc, polymarket

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

TECNOLOGIAS = {
    "frontend": ["Vue 3", "TypeScript", "Vite"],
    "backend": ["Python 3.11+", "FastAPI", "httpx", "Uvicorn"],
    "fuentes": ["MEXC Spot API v3 (pública)", "Polymarket Gamma API (pública)"],
    "pruebas": ["pytest", "vue-tsc"],
}


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=config.timeout_s, headers={"User-Agent": f"agente-ia-finanzas/{config.version}"})
    yield
    await app.state.http.aclose()


app = FastAPI(title=config.nombre, version=config.version, lifespan=ciclo_de_vida,
              description="Backend del agente. v0.1: datos de MEXC y Polymarket en modo solo lectura.")
app.add_middleware(CORSMiddleware, allow_origins=config.origenes_cors, allow_methods=["GET"],
                   allow_headers=["X-API-Key"])


async def cliente_http(request: Request) -> AsyncIterator[httpx.AsyncClient]:
    yield request.app.state.http


def requiere_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Protege rutas de control. La clave vive solo en el servidor (BACKEND_API_KEY)."""
    if not config.api_key:
        raise HTTPException(503, "BACKEND_API_KEY no configurada en el servidor")
    if not x_api_key or not secrets.compare_digest(x_api_key, config.api_key):
        raise HTTPException(401, "API key ausente o incorrecta")


@app.exception_handler(ProveedorError)
async def _proveedor(_: Request, e: ProveedorError):
    return JSONResponse(status_code=e.status, content={"error": e.mensaje, "fuente": e.fuente})


@app.exception_handler(EntradaInvalidaError)
async def _entrada(_: Request, e: EntradaInvalidaError):
    return JSONResponse(status_code=422, content={"error": str(e)})


@app.get("/api/health")
async def health():
    return {"estado": "ok", "version": config.version}


@app.get("/api/version")
async def version():
    return {"nombre": config.nombre, "version": config.version, "modo": "paper",
            "trading_real": config.trading_real, "tecnologias": TECNOLOGIAS}


@app.get("/api/mexc/ticker")
async def mexc_ticker(simbolo: str = "BTCUSDT", c: httpx.AsyncClient = Depends(cliente_http)):
    return await mexc.ticker_24h(c, simbolo)


@app.get("/api/mexc/velas")
async def mexc_velas(simbolo: str = "BTCUSDT", intervalo: str = "1d",
                     limite: int = Query(30, ge=1, le=1000), c: httpx.AsyncClient = Depends(cliente_http)):
    return await mexc.velas(c, simbolo, intervalo, limite)


@app.get("/api/polymarket/mercados")
async def polymarket_mercados(limite: int = Query(20, ge=1, le=100), busqueda: str = "",
                              c: httpx.AsyncClient = Depends(cliente_http)):
    """Mercados abiertos de Polymarket, solo de la categoría cripto, ordenados por volumen."""
    return await polymarket.mercados(c, limite, busqueda)


@app.get("/api/control/estado", dependencies=[Depends(requiere_api_key)])
async def control_estado():
    """Ruta protegida de ejemplo; en versiones siguientes iniciar/pausar/detener vivirán aquí."""
    return {"agente": "detenido", "trading_real": config.trading_real}
