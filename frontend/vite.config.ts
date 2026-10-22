import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
  },
  build: {
    rollupOptions: {
      input: {
        commandCenter: resolve(root, 'index.html'),
        readyAtHome: resolve(root, 'ready-at-home.html'),
      },
    },
  },
});
