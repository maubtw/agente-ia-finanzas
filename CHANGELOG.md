# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [SemVer](https://semver.org/lang/es/).

## [0.1.0] - 2026-11-17

### Añadido
- UI en Vue 3 + TypeScript + Vite con selector de fuente (MEXC / Polymarket), versión visible de UI y API, y panel de tecnologías.
- Panel MEXC: ticker de 24 h, mini gráfica de cierres y tabla de las últimas 10 velas diarias cerradas (BTCUSDT, ETHUSDT).
- Panel Polymarket: mercados abiertos ordenados por volumen con probabilidad implícita por resultado y búsqueda por texto.
- Backend FastAPI con `/api/health`, `/api/version`, `/api/mexc/ticker`, `/api/mexc/velas`, `/api/polymarket/mercados`.
- Reintentos limitados con espera creciente, manejo de límite de solicitudes (429) y errores claros por fuente.
- Ruta de control protegida con API key (`/api/control/estado`).
- Pruebas pytest con transportes HTTP simulados (7 pruebas).
- `VERSION` como fuente única de la versión; `.env.example` sin secretos; `CLAUDE.md` para Claude Code.

### Seguridad
- Sin rutas de órdenes reales; `trading_real` fijo en `false`.
- El frontend no contiene claves ni llama directamente a las APIs externas.
