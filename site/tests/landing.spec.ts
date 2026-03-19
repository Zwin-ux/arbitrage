import { expect, test } from "@playwright/test";

test("homepage renders one canonical machine screen", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__header")).toHaveCount(1);
  await expect(page.locator(".superior-screen__playfield")).toHaveCount(1);
  await expect(page.locator(".superior-screen__controls")).toHaveCount(1);
  await expect(page.getByAltText("Superior")).toBeVisible();
  await expect(page.locator(".superior-screen__status")).toContainText("PRACTICE MONEY");
  await expect(page.getByText("$100.00")).toBeVisible();
  await expect(page.getByRole("button", { name: /^START$/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /HOLD TO BUY \$25\.00/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /^DOWNLOAD$/ })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/market-data-recorder-setup.exe"
  );

  await expect(page.locator(".state-strip-frame")).toHaveCount(0);
  await expect(page.locator(".product-frame")).toHaveCount(0);
  await expect(page.locator(".download-frame")).toHaveCount(0);
});

test("homepage resolves a practice-money run and resets cleanly", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: /^START$/ }).click();
  await page.waitForTimeout(2100);

  const commitButton = page.locator(".machine-control--commit");
  await commitButton.dispatchEvent("mousedown");
  await page.waitForTimeout(430);
  await commitButton.dispatchEvent("mouseup");

  const result = page.locator(".decision-lane__result");
  await expect(result).toBeVisible();
  await expect(result).toContainText("BANKROLL $");
  await expect(result).toContainText(/BUY \d+c -> SELL \d+c|NO POSITION OPENED/i);

  await page.getByRole("button", { name: /^RESET$/ }).click();
  await expect(page.getByText("$100.00")).toBeVisible();
  await expect(page.locator(".decision-lane__result")).toHaveCount(0);
});

test("download page uses the same restrained machine screen", async ({ page }) => {
  await page.goto("/download/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Download");
  await expect(page.getByText(/market-data-recorder-setup\.exe/i)).toBeVisible();
  await expect(page.getByText(/start with \$100\. practice money is the default loop\./i)).toBeVisible();
  await expect(page.getByText(/start\. hold to buy\. see the bankroll move\. reset\./i)).toBeVisible();
  await expect(page.getByRole("link", { name: /sha256sums/i })).toHaveAttribute(
    "href",
    "https://github.com/Zwin-ux/arbitrage/releases/latest/download/SHA256SUMS.txt"
  );
});

test("docs page keeps repo guidance inside one machine screen", async ({ page }) => {
  await page.goto("/docs/");

  await expect(page.locator(".machine-page")).toHaveCount(1);
  await expect(page.locator(".machine-page__label")).toContainText("Docs");
  await expect(page.getByText(/start with fake money\. keep live off until local progress passes\./i)).toBeVisible();
  await expect(page.getByText(/npm --prefix desktop-v1 run dev/i)).toBeVisible();
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
  await expect(page.locator(".superior-screen__status")).toContainText("PRACTICE MONEY");
  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(4);

  await page.goto("/lab/focus/");
  await expect(page.locator(".superior-screen")).toHaveCount(1);
  await expect(page.locator(".superior-screen__status")).toContainText("PRACTICE MONEY");
  await expect(page.locator(".superior-screen__controls .machine-control")).toHaveCount(4);
});
