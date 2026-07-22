import { expect, test } from "@playwright/test";

test("login exposes accessible credential validation", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
  await page.getByRole("button", { name: /^sign in/i }).click();
  await expect(page.getByText("Enter your username")).toBeVisible();
  await expect(page.getByText("Enter your password")).toBeVisible();
});

test("authenticated workspace creates and sends an analysis", async ({ context, page }) => {
  await context.addCookies([{ name: "agent_session", value: "test-token", domain: "127.0.0.1", path: "/", httpOnly: true, sameSite: "Strict" }]);
  await page.route("**/api/auth/me", (route) => route.fulfill({ json: { user: { sub: "test", role: "analyst", display_name: "Test Analyst" } } }));
  await page.route("**/api/bff/chat", (route) => route.fulfill({ json: { session_id: "e2e", workflow_status: "complete", message: "Analysis complete.", steps: [{ id: "1", label: "Plan analysis", status: "complete" }] } }));
  await page.goto("/");
  await expect(page.getByText("What would you like to understand?")).toBeVisible();
  await page.getByLabel("Message").fill("Summarize performance");
  await page.getByRole("button", { name: "Send" }).click();
  await expect(page.getByText("Analysis complete.")).toBeVisible();
});
