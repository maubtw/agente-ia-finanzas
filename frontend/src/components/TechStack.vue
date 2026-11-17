<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ tecnologias?: Record<string, string[]> }>()

// Respaldo local por si el backend no responde.
const local: Record<string, string[]> = {
  frontend: ['Vue 3', 'TypeScript', 'Vite'],
  backend: ['Python 3.11+', 'FastAPI', 'httpx', 'Uvicorn'],
  fuentes: ['MEXC Spot API v3 (pública)', 'Polymarket Gamma API (pública)'],
}
const lista = computed(() => props.tecnologias ?? local)
</script>

<template>
  <section class="panel">
    <h2>Tecnologías aplicadas</h2>
    <dl class="tecnologias">
      <template v-for="(items, capa) in lista" :key="capa">
        <dt>{{ capa }}</dt>
        <dd><span v-for="t in items" :key="t" class="chip">{{ t }}</span></dd>
      </template>
    </dl>
  </section>
</template>
