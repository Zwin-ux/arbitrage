import { fileURLToPath } from "node:url";
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  integrations: [react()],
  site: process.env.SITE_URL,
  output: "static",
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        "@shared": fileURLToPath(new URL("../shared", import.meta.url)),
      },
    },
    server: {
      fs: {
        allow: [".."],
      },
    },
  }
});
