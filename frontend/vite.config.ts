export default defineConfig({ plugins: [react()], server: { proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } } } })
