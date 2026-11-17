<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api, type Ticker, type Vela } from '../api'

const simbolos = ['BTCUSDT', 'ETHUSDT']
const simbolo = ref('BTCUSDT')
const ticker = ref<Ticker | null>(null)
const velas = ref<Vela[]>([])
const cargando = ref(false)
const error = ref('')
const actualizado = ref<Date | null>(null)

const usd = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 })
const num = new Intl.NumberFormat('es-MX', { maximumFractionDigits: 2 })
const fecha = (ms: number) => new Date(ms).toISOString().slice(0, 10)

const cerradas = computed(() => velas.value.filter((v) => v.cerrada))
const ultimas = computed(() => [...cerradas.value].reverse().slice(0, 10))

// Mini gráfica SVG de cierres (sin dependencias)
const ruta = computed(() => {
  const c = cerradas.value.map((v) => v.close)
  if (c.length < 2) return ''
  const min = Math.min(...c), max = Math.max(...c), rango = max - min || 1
  return c.map((v, i) => `${i ? 'L' : 'M'}${(i / (c.length - 1)) * 600},${110 - ((v - min) / rango) * 100}`).join(' ')
})

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const [t, v] = await Promise.all([api.ticker(simbolo.value), api.velas(simbolo.value, '1d', 60)])
    ticker.value = t
    velas.value = v.velas
    actualizado.value = new Date()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
watch(simbolo, cargar)
</script>

<template>
  <section class="panel">
    <div class="panel-cab">
      <h2>MEXC Spot</h2>
      <div class="acciones">
        <select v-model="simbolo" aria-label="Símbolo">
          <option v-for="s in simbolos" :key="s" :value="s">{{ s }}</option>
        </select>
        <button :disabled="cargando" @click="cargar">{{ cargando ? 'Cargando…' : 'Actualizar' }}</button>
      </div>
    </div>

    <p v-if="error" class="aviso">MEXC: {{ error }}</p>

    <div v-if="ticker" class="tarjetas">
      <div class="tarjeta"><span>Último</span><strong>{{ usd.format(ticker.ultimo) }}</strong></div>
      <div class="tarjeta">
        <span>Cambio 24 h</span>
        <strong :class="(ticker.cambio_pct ?? 0) >= 0 ? 'sube' : 'baja'">
          {{ ticker.cambio_pct === null ? '—' : `${num.format(ticker.cambio_pct)} %` }}
        </strong>
      </div>
      <div class="tarjeta"><span>Máx / mín 24 h</span><strong>{{ usd.format(ticker.maximo) }} / {{ usd.format(ticker.minimo) }}</strong></div>
      <div class="tarjeta"><span>Volumen 24 h</span><strong>{{ num.format(ticker.volumen) }}</strong></div>
    </div>

    <figure v-if="ruta" class="grafica">
      <svg viewBox="0 0 600 120" preserveAspectRatio="none" role="img" :aria-label="`Cierres diarios de ${simbolo}`">
        <path :d="ruta" fill="none" stroke="currentColor" stroke-width="2" vector-effect="non-scaling-stroke" />
      </svg>
      <figcaption>Cierres diarios de las últimas {{ cerradas.length }} velas cerradas (la vela del día en curso se excluye)</figcaption>
    </figure>

    <table v-if="ultimas.length" class="tabla">
      <thead>
        <tr><th>Fecha (UTC)</th><th>Apertura</th><th>Máximo</th><th>Mínimo</th><th>Cierre</th><th>Volumen</th></tr>
      </thead>
      <tbody>
        <tr v-for="v in ultimas" :key="v.apertura_ms">
          <td>{{ fecha(v.apertura_ms) }}</td><td>{{ num.format(v.open) }}</td><td>{{ num.format(v.high) }}</td>
          <td>{{ num.format(v.low) }}</td><td>{{ num.format(v.close) }}</td><td>{{ num.format(v.volumen) }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="actualizado" class="nota">Fuente: MEXC Spot API v3 · consultado {{ actualizado.toLocaleString('es-MX') }}</p>
  </section>
</template>
