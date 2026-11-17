"""Configuración del backend. Los secretos solo viven en variables de entorno del servidor."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _leer_version() -> str:
    try:
        return (RAIZ / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0-desconocida"


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


@dataclass(frozen=True)
class Config:
    nombre: str = "Agente IA Finanzas"
    version: str = field(default_factory=_leer_version)
    mexc_url: str = field(default_factory=lambda: os.getenv("MEXC_BASE_URL", "https://api.mexc.com"))
    polymarket_url: str = field(
        default_factory=lambda: os.getenv("POLYMARKET_GAMMA_URL", "https://gamma-api.polymarket.com"))
    simbolos_permitidos: list[str] = field(
        default_factory=lambda: _lista(os.getenv("MEXC_SIMBOLOS_PERMITIDOS", "BTCUSDT,ETHUSDT")))
    origenes_cors: list[str] = field(
        default_factory=lambda: _lista(os.getenv("CORS_ORIGINS", "http://localhost:5173")))
    api_key: str = field(default_factory=lambda: os.getenv("BACKEND_API_KEY", ""))
    timeout_s: float = field(default_factory=lambda: float(os.getenv("HTTP_TIMEOUT_S", "10")))
    # Regla del protocolo: nunca se envían órdenes reales. No es configurable.
    trading_real: bool = False


config = Config()
