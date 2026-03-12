import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  integrations: [react()],
  site: process.env.SITE_URL,
  output: "static",
  vite: {
    plugins: [tailwindcss()]
  }
});
