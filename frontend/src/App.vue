<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, type Version } from './api'
import MexcPanel from './components/MexcPanel.vue'
import PolymarketPanel from './components/PolymarketPanel.vue'
import TechStack from './components/TechStack.vue'

type Fuente = 'mexc' | 'polymarket'

const versionUi = __APP_VERSION__
const backend = ref<Version | null>(null)
const backendError = ref('')
const fuente = ref<Fuente>('mexc')

onMounted(async () => {
  try {
    backend.value = await api.version()
  } catch (e) {
    backendError.value = (e as Error).message
  }
})
</script>

<template>
  <header class="barra">
    <div class="marca">
      <span class="logo" aria-hidden="true">◆</span>
      <div>
        <h1>Agente IA Finanzas</h1>
        <p class="sub">Datos de mercado · modo Paper (sin órdenes reales)</p>
      </div>
    </div>
    <div class="versiones">
      <span class="chip">UI v{{ versionUi }}</span>
      <span v-if="backend" class="chip">API v{{ backend.version }}</span>
      <span v-else class="chip chip-alerta" :title="backendError">API sin conexión</span>
      <span class="chip chip-ok">trading real: desactivado</span>
    </div>
  </header>

  <main class="contenido">
    <nav class="selector" role="tablist" aria-label="Fuente de datos">
      <button role="tab" :aria-selected="fuente === 'mexc'" :class="{ activo: fuente === 'mexc' }"
              @click="fuente = 'mexc'">MEXC · cripto spot</button>
      <button role="tab" :aria-selected="fuente === 'polymarket'" :class="{ activo: fuente === 'polymarket' }"
              @click="fuente = 'polymarket'">Polymarket · cripto</button>
    </nav>

    <p v-if="backendError" class="aviso">{{ backendError }}</p>

    <MexcPanel v-if="fuente === 'mexc'" />
    <PolymarketPanel v-else />

    <TechStack :tecnologias="backend?.tecnologias" />
  </main>

  <footer class="pie">
    v{{ versionUi }} · Proyecto académico de Deep Learning para Finanzas · Los datos no son recomendación de inversión.
  </footer>
</template>
