import { readFileSync } from 'node:fs'
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// La versión se lee del archivo VERSION en la raíz del repositorio (fuente única de verdad).
const version = readFileSync(fileURLToPath(new URL('../VERSION', import.meta.url)), 'utf-8').trim()

export default defineConfig({
  plugins: [vue()],
  define: { __APP_VERSION__: JSON.stringify(version) },
  server: {
    port: 5173,
    // El navegador solo habla con nuestro backend; el backend consulta MEXC y Polymarket.
    proxy: { '/api': { target: process.env.VITE_BACKEND_URL ?? 'http://localhost:8000', changeOrigin: true } },
  },
})
