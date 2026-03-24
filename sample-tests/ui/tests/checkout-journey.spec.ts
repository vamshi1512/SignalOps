import { expect, test } from "@playwright/test";

const baseUrl = process.env.TARGET_UI_BASE_URL ?? "http://localhost:8000/api/v1/target-ui";

test("checkout summary is visible", async ({ page }) => {
  await page.goto(`${baseUrl}/checkout`);
  await expect(page.getByTestId("checkout-title")).toBeVisible();
  await expect(page.getByTestId("checkout-summary")).toContainText("SEK 99.00");
  await expect(page.getByTestId("payment-status")).toContainText("Authorized");
});
