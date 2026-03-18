import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: {
    timeout: 10_000
  },
  use: {
    baseURL: "http://127.0.0.1:4381",
    trace: "retain-on-failure",
    screenshot: "only-on-failure"
  },
  webServer: {
    command: "npm run build && npx astro preview --host 127.0.0.1 --port 4381",
    url: "http://127.0.0.1:4381",
    reuseExistingServer: false,
    timeout: 120_000
  }
});
