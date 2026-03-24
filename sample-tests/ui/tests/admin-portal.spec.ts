import { expect, test } from "@playwright/test";

const baseUrl = process.env.TARGET_UI_BASE_URL ?? "http://localhost:8000/api/v1/target-ui";

test("admin portal roles table renders", async ({ page }) => {
  await page.goto(`${baseUrl}/admin`);
  await expect(page.getByTestId("admin-title")).toBeVisible();
  await expect(page.getByTestId("roles-table")).toContainText("auditor");
});
