import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    allowedHosts: ['flowershop.swifttest.ru'],
    proxy: {
      '/api': {
        target: 'https://flowershop.swifttest.ru',
        changeOrigin: true,
      },
      '/media': {
        target: 'https://flowershop.swifttest.ru',
        changeOrigin: true,
      },
    },
    watch: {
      usePolling: true,
      interval: 100,
    },
  },
})
