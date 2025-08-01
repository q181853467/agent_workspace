import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue()
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // rollupOptions: {
    //   output: {
    //     manualChunks: {
    //       'element-plus': ['element-plus'],
    //       'vue-vendor': ['vue', 'vue-router', 'pinia'],
    //       'charts': ['echarts', 'vue-echarts']
    //     }
    //   }
    // }
  }
})