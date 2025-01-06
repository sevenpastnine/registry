import { resolve } from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    root: resolve('./frontend'),
    base: '/static/frontend/',
    css: { preprocessorOptions: { sass: { api: 'modern' } } },
    build: {
        manifest: "manifest.json",
        assetsDir: '',
        outDir: resolve('./backend/static/frontend'),
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: resolve('./frontend/main.js'),
                studyDesignMaps: resolve('./frontend/studyDesignMaps/main.tsx'),
            },
            output: {
                manualChunks: {
                    vendor: ['react', 'react-dom'],
                }
            }
        }
    }
})
