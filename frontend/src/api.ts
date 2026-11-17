// Tipos y cliente del backend. El frontend nunca contiene claves.

export interface Version {
  nombre: string
  version: string
  modo: string
  trading_real: boolean
  tecnologias: Record<string, string[]>
}

export interface Ticker {
  simbolo: string
  ultimo: number
  cambio_pct: number | null
  maximo: number
  minimo: number
  volumen: number
  fuente: string
}

export interface Vela {
  apertura_ms: number
  open: number
  high: number
  low: number
  close: number
  volumen: number
  cierre_ms: number
  cerrada: boolean
}

export interface Velas {
  simbolo: string
  intervalo: string
  velas: Vela[]
  fuente: string
}

export interface Resultado {
  nombre: string
  probabilidad: number
}

export interface Mercado {
  id: string
  pregunta: string
  slug: string
  resultados: Resultado[]
  volumen: number
  liquidez: number
  fecha_fin: string | null
  url: string
}

export class ApiError extends Error {}

async function get<T>(ruta: string, params: Record<string, string | number> = {}): Promise<T> {
  const qs = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))
  const url = qs.size ? `${ruta}?${qs}` : ruta
  let r: Response
  try {
    r = await fetch(url)
  } catch {
    throw new ApiError('No hay conexión con el backend. ¿Está corriendo en el puerto 8000?')
  }
  const cuerpo = await r.json().catch(() => ({}))
  if (!r.ok) throw new ApiError(cuerpo.error ?? cuerpo.detail ?? `Error HTTP ${r.status}`)
  return cuerpo as T
}

export const api = {
  version: () => get<Version>('/api/version'),
  ticker: (simbolo: string) => get<Ticker>('/api/mexc/ticker', { simbolo }),
  velas: (simbolo: string, intervalo = '1d', limite = 30) =>
    get<Velas>('/api/mexc/velas', { simbolo, intervalo, limite }),
  mercados: (limite = 20, busqueda = '') =>
    get<{ mercados: Mercado[]; fuente: string }>('/api/polymarket/mercados', { limite, busqueda }),
}
