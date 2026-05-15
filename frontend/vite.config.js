import { defineConfig, loadEnv } from "vite";
import react, { reactCompilerPreset } from "@vitejs/plugin-react";
import babel from "@rolldown/plugin-babel";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  // process.env picks up OS-level vars (Docker env_file / CI); loadEnv picks up .env files (local dev)
  const apiTarget = process.env.VITE_API_BASE_URL || env.VITE_API_BASE_URL || "http://localhost:8000";
  const wsTarget = process.env.VITE_WS_BASE_URL || env.VITE_WS_BASE_URL || "ws://localhost:8000";

  return {
    plugins: [
      react(),
      babel({ presets: [reactCompilerPreset()] }),
      tailwindcss(),
    ],
    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: {
        "/api": { target: apiTarget, changeOrigin: true },
        "/ws": { target: wsTarget, ws: true, changeOrigin: true },
      },
    },
  };
});
