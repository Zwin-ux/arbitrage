import { expect, test } from "@playwright/test";

test("homepage renders one canonical machine screen", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__header")).toHaveCount(1);
  await expect(page.locator(".superior-screen__playfield")).toHaveCount(1);
  await expect(page.locator(".superior-screen__controls")).toHaveCount(1);
  await expect(page.locator(".superior-screen__brand")).toContainText("SUPERIOR");
  await expect(page.locator(".decision-lane__anchor-label")).toContainText("YOU");
  await expect(page.locator(".decision-lane__marker")).toHaveCount(3);

  await expect(page.getByRole("link", { name: /^START$/ })).toHaveAttribute("href", "/download/");
  await expect(page.getByRole("link", { name: /^HOLD TO COMMIT$/ })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe"
  );

  await expect(page.locator(".state-strip-frame")).toHaveCount(0);
  await expect(page.locator(".product-frame")).toHaveCount(0);
  await expect(page.locator(".download-frame")).toHaveCount(0);
});

test("download page uses the same restrained machine screen", async ({ page }) => {
  await page.goto("/download/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Download");
  await expect(page.getByText(/market-data-recorder-setup\.exe/i)).toBeVisible();
  await expect(page.getByText(/leave credentials blank if recorder plus practice mode is enough/i)).toBeVisible();
  await expect(page.getByText(/record first\. inspect the route\. keep live locked\./i)).toBeVisible();
  await expect(page.getByRole("link", { name: /sha256sums/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/SHA256SUMS.txt"
  );
});

test("docs page keeps repo guidance inside one machine screen", async ({ page }) => {
  await page.goto("/docs/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Docs");
  await expect(page.getByText(/github repo docs are the source of truth/i)).toBeVisible();
  await expect(page.getByText(/market-data-recorder-app/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /release checklist/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/tree/main/docs/release-checklist.md"
  );
});

test("variant lab exposes both control and focus routes", async ({ page }) => {
  await page.goto("/lab/");

  await expect(page.locator("h1")).toContainText("Compare the homepage");
  await expect(page.getByRole("link", { name: /open variant/i })).toHaveCount(2);
  await expect(page.getByRole("link", { name: /open variant/i }).nth(0)).toHaveAttribute("href", "/lab/control");
  await expect(page.getByRole("link", { name: /open variant/i }).nth(1)).toHaveAttribute("href", "/lab/focus");
});

test("control and focus variants share the same canonical screen", async ({ page }) => {
  await page.goto("/lab/control/");
  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__status")).toContainText("CONTROL");
  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(4);

  await page.goto("/lab/focus/");
  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__status")).toContainText("FOCUS");
  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(4);
});
