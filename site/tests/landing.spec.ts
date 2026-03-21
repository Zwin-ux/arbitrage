import { expect, test } from "@playwright/test";

test("homepage renders one canonical machine screen", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__header")).toHaveCount(1);
  await expect(page.locator(".superior-screen__playfield")).toHaveCount(1);
  await expect(page.locator(".superior-screen__controls")).toHaveCount(1);
  await expect(page.getByRole("img", { name: "Superior", exact: true })).toBeVisible();
  await expect(page.getByAltText("Superior mascot")).toBeVisible();
  await expect(page.locator(".superior-screen__status-text")).toContainText(/windows \/ local \/ auto/i);
  await expect(page.locator(".superior-promo__badge")).toContainText(/engine prediction bot/i);
  await expect(page.getByText(/windows bot for kalshi\./i)).toBeVisible();
  await expect(page.getByText(/local setup\. auto after checks\./i)).toBeVisible();
  await expect(page.getByRole("link", { name: /download exe/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe"
  );

  await expect(page.locator(".state-strip-frame")).toHaveCount(0);
  await expect(page.locator(".product-frame")).toHaveCount(0);
  await expect(page.locator(".download-frame")).toHaveCount(0);
});

test("homepage keeps the controls minimal", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(3);
  await expect(page.getByRole("link", { name: /portable zip/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-app-portable.zip"
  );
  await expect(page.getByRole("link", { name: /^docs$/i })).toHaveAttribute("href", "/docs/");
});

test("download page uses the same restrained machine screen", async ({ page }) => {
  await page.goto("/download/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Download");
  await expect(page.getByText(/get the setup exe/i)).toBeVisible();
  await expect(page.getByText(/learn first, then clear one shadow run before you arm auto\./i)).toBeVisible();
  await expect(page.getByText(/they teach the timing loop before you turn on the kalshi starter bot\./i)).toBeVisible();
  await expect(page.getByRole("link", { name: /sha256sums/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/SHA256SUMS.txt"
  );
});

test("docs page keeps repo guidance inside one machine screen", async ({ page }) => {
  await page.goto("/docs/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Docs");
  await expect(page.getByText(/clear the learn ladder and one shadow run before you arm the starter bot\./i)).toBeVisible();
  await expect(page.getByRole("link", { name: /first shadow run/i })).toBeVisible();
  await expect(page.getByText(/npm --prefix desktop-v1 run dev/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /release checklist/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/tree/main/docs/release-checklist.md"
  );
});

test("roadmap page uses the same machine shell and release ladder", async ({ page }) => {
  await page.goto("/roadmap/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Roadmap");
  await expect(page.getByText(/starter bot \/ release ladder/i)).toBeVisible();
  await expect(page.getByText(/trust ramp/i)).toBeVisible();
  await expect(page.getByText(/kalshi starter bot/i)).toBeVisible();
  await expect(page.locator(".machine-page__strip-body strong", { hasText: /no multi-venue live bot/i })).toBeVisible();
});

test("variant lab exposes both control and focus routes inside the same machine shell", async ({ page }) => {
  await page.goto("/lab/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Lab");
  await expect(page.getByRole("link", { name: /^Open$/ }).nth(0)).toHaveAttribute("href", "/lab/control");
  await expect(page.getByRole("link", { name: /^Open$/ }).nth(1)).toHaveAttribute("href", "/lab/focus");
  await expect(page.getByText(/does the download feel safe enough to click\?/i)).toBeVisible();
});

test("control and focus variants share the same canonical screen", async ({ page }) => {
  await page.goto("/lab/control/");
  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__status-text")).toContainText(/windows \/ local \/ auto/i);
  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(3);

  await page.goto("/lab/focus/");
  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__status-text")).toContainText(/windows \/ local \/ auto/i);
  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(3);
});
