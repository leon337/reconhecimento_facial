import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: '/static/copilot/',
  publicDir: 'public',
  build: {
    outDir: '../../static/copilot',
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      input: 'src/main.js',
      output: {
        entryFileNames: 'app.js',
        chunkFileNames: 'chunk-[name].js',
        assetFileNames: ({ names }) => names?.some((n) => n.endsWith('.css')) ? 'style.css' : 'asset-[name][extname]',
      },
    },
  },
});
