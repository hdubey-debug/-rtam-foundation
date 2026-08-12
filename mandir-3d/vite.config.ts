/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "/" standalone; VITE_BASE=/mandir/ for a subpath deploy next to the
// website. Both paths are build-verified at M12; neither is deployed until
// the founder decides.
export default defineConfig({
  base: process.env.VITE_BASE ?? "/",
  plugins: [react()],
  build: {
    // three/webgpu is one large module; splitting it is deferred until M12.
    chunkSizeWarningLimit: 2000,
  },
  test: {
    environment: "node",
    include: ["src/**/__tests__/**/*.test.ts"],
    // geometry tests arrive with the lib primitives at M3
    passWithNoTests: true,
  },
});
