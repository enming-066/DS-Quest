import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发时前端跑在 5173，接口请求转发到后端的 8000
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 4000
  }
})
