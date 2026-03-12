import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  integrations: [react()],
  site: "https://market-data-recorder.up.railway.app",
  output: "static",
  vite: {
    plugins: [tailwindcss()]
  }
});
