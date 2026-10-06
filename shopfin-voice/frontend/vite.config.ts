import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The browser talks to /api on the Vite server, which forwards to FastAPI.
// This avoids CORS problems and keeps one URL for everything in development.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
})
