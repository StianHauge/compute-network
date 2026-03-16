import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({ plugins: [react()], server: { proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true }, '/auth': { target: 'http://localhost:8000', changeOrigin: true }, '/v1': { target: 'http://localhost:8000', changeOrigin: true }, '/nodes': { target: 'http://localhost:8000', changeOrigin: true }, '/jobs': { target: 'http://localhost:8000', changeOrigin: true }, '/admin': { target: 'http://localhost:8000', changeOrigin: true } } } })
