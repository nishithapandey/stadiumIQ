import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: [],
  },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  build: {
    // Optimize chunk splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          i18n: ["i18next", "react-i18next"],
          icons: ["lucide-react"],
        },
      },
    },
    // Enable source maps for production debugging
    sourcemap: false,
    // Target modern browsers for smaller bundles
    target: "es2020",
  },
});
