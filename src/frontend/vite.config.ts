import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:7653',
      },
      '/socket.io': {
        target: 'http://localhost:7653',
        ws: true,
      },
    },
  },
})
