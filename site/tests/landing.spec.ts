import { expect, test } from "@playwright/test";

test("homepage keeps the primary download path visible", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /learn the market\./i })).toBeVisible();
  await expect(page.getByText(/open-source prediction-market bot/i)).toBeVisible();
  await expect(
    page.getByText(/local-first desktop bot os for recording public market books/i)
  ).toBeVisible();
  const downloadLink = page.getByRole("link", { name: /download/i }).first();
  await expect(downloadLink).toBeVisible();
  await expect(downloadLink).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe"
  );
});

test("download page explains the guided setup path", async ({ page }) => {
  await page.goto("/download/");

  await expect(page.getByRole("heading", { name: /install the windows build and start in paper mode\./i })).toBeVisible();
  await expect(page.getByText(/keep the guided template/i)).toBeVisible();
  await expect(page.getByText(/record books, inspect routes, paper them/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /download sha256sums/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/SHA256SUMS.txt"
  );
});

test("variant lab exposes both control and focus routes", async ({ page }) => {
  await page.goto("/lab/");

  await expect(page.locator("h1")).toContainText("Compare the homepage");
  await expect(page.getByRole("link", { name: /open variant/i })).toHaveCount(2);
  await expect(page.getByRole("link", { name: /open variant/i }).nth(0)).toHaveAttribute("href", "/lab/control");
  await expect(page.getByRole("link", { name: /open variant/i }).nth(1)).toHaveAttribute("href", "/lab/focus");
});

test("control and focus variants stay intentionally different", async ({ page }) => {
  await page.goto("/lab/control/");
  await expect(page.getByRole("heading", { name: /learn the market\./i })).toBeVisible();
  await expect(
    page.getByText(/local-first desktop bot os for recording public market books/i)
  ).toBeVisible();

  await page.goto("/lab/focus/");
  await expect(page.getByRole("heading", { name: /track the books\./i })).toBeVisible();
  await expect(page.getByText(/keeps the bot feed and paper score honest/i)).toBeVisible();
});
