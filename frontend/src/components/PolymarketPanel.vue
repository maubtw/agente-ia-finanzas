<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, type Mercado } from '../api'

const mercados = ref<Mercado[]>([])
const busqueda = ref('')
const cargando = ref(false)
const error = ref('')
const actualizado = ref<Date | null>(null)

const usd = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'USD', notation: 'compact' })
const pct = (p: number) => `${(p * 100).toFixed(1)} %`

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    mercados.value = (await api.mercados(15, busqueda.value.trim())).mercados
    actualizado.value = new Date()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <section class="panel">
    <div class="panel-cab">
      <h2>Polymarket · mercados cripto abiertos</h2>
      <form class="acciones" @submit.prevent="cargar">
        <input v-model="busqueda" type="search" placeholder="Buscar (p. ej. ethereum)" aria-label="Buscar mercado cripto" />
        <button :disabled="cargando" type="submit">{{ cargando ? 'Cargando…' : 'Buscar' }}</button>
      </form>
    </div>

    <p v-if="error" class="aviso">Polymarket: {{ error }}</p>
    <p v-else-if="!cargando && actualizado && !mercados.length" class="nota">Sin mercados cripto abiertos que coincidan.</p>

    <ul class="mercados">
      <li v-for="m in mercados" :key="m.id" class="mercado">
        <a :href="m.url" target="_blank" rel="noopener noreferrer" class="pregunta">{{ m.pregunta }}</a>
        <div class="resultados">
          <div v-for="r in m.resultados" :key="r.nombre" class="resultado">
            <span class="r-nombre">{{ r.nombre }}</span>
            <span class="barra-prob"><span :style="{ width: `${Math.min(100, Math.max(0, r.probabilidad * 100))}%` }" /></span>
            <span class="r-prob">{{ pct(r.probabilidad) }}</span>
          </div>
        </div>
        <span class="nota">Volumen {{ usd.format(m.volumen) }} · Liquidez {{ usd.format(m.liquidez) }}
          <template v-if="m.fecha_fin"> · cierra {{ m.fecha_fin.slice(0, 10) }}</template></span>
      </li>
    </ul>
    <p v-if="actualizado" class="nota">Fuente: Polymarket Gamma API · solo etiqueta Crypto · precios = probabilidad implícita · consultado {{ actualizado.toLocaleString('es-MX') }}</p>
  </section>
</template>
