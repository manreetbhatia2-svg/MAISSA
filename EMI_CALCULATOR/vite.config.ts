import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './', // Use relative paths so any subfolder can read assets safely
  build: {
    outDir: '../dist', // Build straight to a shared root dist folder
    emptyOutDir: true,
  }
})