import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // maplibre-gl loads a web worker via a relative `new URL(..., import.meta.url)`;
  // pre-bundling it into node_modules/.vite/deps breaks that resolution.
  optimizeDeps: {
    exclude: ['maplibre-gl'],
  },
})
