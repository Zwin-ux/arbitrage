import { expect, test } from "@playwright/test";

test("homepage keeps the primary download path visible", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /scan markets\./i })).toBeVisible();
  const downloadLink = page.getByRole("link", { name: /download for windows/i }).first();
  await expect(downloadLink).toBeVisible();
  await expect(downloadLink).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe"
  );
  await expect(page.getByRole("link", { name: /open the draft route/i })).toHaveAttribute("href", "/lab/draft");
});

test("variant lab exposes control, focus, and draft routes", async ({ page }) => {
  await page.goto("/lab/");

  await expect(page.locator("h1")).toContainText("Compare the homepage");
  await expect(page.getByRole("link", { name: /open variant/i })).toHaveCount(3);
  await expect(page.getByRole("link", { name: /open variant/i }).nth(0)).toHaveAttribute("href", "/lab/control");
  await expect(page.getByRole("link", { name: /open variant/i }).nth(1)).toHaveAttribute("href", "/lab/focus");
  await expect(page.getByRole("link", { name: /open variant/i }).nth(2)).toHaveAttribute("href", "/lab/draft");
});

test("control, focus, and draft variants stay intentionally different", async ({ page }) => {
  await page.goto("/lab/control/");
  await expect(page.getByRole("heading", { name: /scan markets\./i })).toBeVisible();
  await expect(page.getByText(/surface signal, preserve context/i)).toBeVisible();

  await page.goto("/lab/focus/");
  await expect(page.getByRole("heading", { name: /see the edge/i })).toBeVisible();
  await expect(page.getByText(/release tooling in one disciplined surface/i)).toBeVisible();

  await page.goto("/lab/draft/");
  await expect(page.getByRole("heading", { name: /review the build/i })).toBeVisible();
  await expect(page.getByText(/a stronger front end draft designed for review/i)).toBeVisible();
});
