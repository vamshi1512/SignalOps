import { expect, test } from "@playwright/test";

const authSession = {
  access_token: "demo-token",
  token_type: "bearer",
  user: {
    id: "user-1",
    email: "qa.lead@testforge.dev",
    full_name: "QA Lead",
    role: "qa_engineer",
  },
};

test("renders TestForge dashboard with mocked API", async ({ page }) => {
  await page.addInitScript(([key, value]) => {
    window.localStorage.setItem(key, JSON.stringify(value));
  }, ["testforge-session", authSession]);

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({ json: authSession.user });
  });

  await page.route("**/api/v1/dashboard/overview", async (route) => {
    await route.fulfill({
      json: {
        metrics: [
          { label: "Pass rate", value: 96.4, delta: 1.7, suffix: "%" },
          { label: "Failures", value: 4, delta: -2, suffix: "" },
          { label: "Avg duration", value: 3.8, delta: 0.2, suffix: "m" },
          { label: "Flaky hits", value: 3, delta: 1, suffix: "" },
          { label: "Schedule coverage", value: 100, delta: 0, suffix: "%" },
        ],
        pass_rate_trend: [{ timestamp: "2026-03-18T09:00:00Z", value: 96.4 }],
        duration_trend: [{ timestamp: "2026-03-18T09:00:00Z", value: 3.8 }],
        flaky_trend: [{ timestamp: "2026-03-18T09:00:00Z", value: 3 }],
        failures_by_module: [{ module_name: "payment.authorize", failures: 4 }],
        recent_runs: [
          {
            id: "run-1",
            trigger_type: "scheduled",
            status: "failed",
            requested_parallel_workers: 2,
            total_count: 4,
            pass_count: 3,
            fail_count: 1,
            skip_count: 0,
            flaky_count: 1,
            duration_ms: 72000,
            started_at: "2026-03-18T09:00:00Z",
            finished_at: "2026-03-18T09:01:12Z",
            created_at: "2026-03-18T08:58:00Z",
            summary: { source_command: "npx playwright test sample-tests/ui/tests/checkout-journey.spec.ts" },
            metadata: { environment_kind: "staging" },
            project: {
              id: "project-1",
              name: "Checkout Core",
              slug: "checkout-core",
              owner: "Team Helix",
              repository_url: "https://github.com/example/checkout-core",
              default_branch: "main",
              description: "Checkout automation",
              created_at: "2026-03-18T08:00:00Z",
              updated_at: "2026-03-18T08:00:00Z",
            },
            suite: {
              id: "suite-1",
              name: "Checkout UI Journeys",
              slug: "checkout-ui-journeys",
              suite_type: "ui",
              owner: "Team Helix",
              tags: ["ui", "checkout"],
              status: "active",
            },
            environment: {
              id: "env-1",
              project_id: "project-1",
              name: "Checkout Staging",
              slug: "checkout-staging",
              kind: "staging",
              status: "degraded",
              api_base_url: "http://backend:8000/api/v1",
              ui_base_url: "http://backend:8000/api/v1",
              health_summary: "1 failing result in latest run",
              variables: { browser: "chromium" },
              is_default: false,
              last_checked_at: "2026-03-18T09:01:12Z",
              created_at: "2026-03-18T08:00:00Z",
              updated_at: "2026-03-18T08:00:00Z",
            },
            fixture_set: null,
            schedule: null,
            triggered_by: null,
          },
        ],
        suites_at_risk: [
          {
            id: "suite-1",
            name: "Checkout UI Journeys",
            suite_type: "ui",
            owner: "Team Helix",
            latest_status: "failed",
            pass_rate_14d: 96.4,
            flaky_cases: 1,
            failing_results: 1,
            environment_name: "Checkout Staging",
          },
        ],
        environments: [
          {
            id: "env-1",
            name: "Checkout Staging",
            kind: "staging",
            status: "degraded",
            project_name: "Checkout Core",
            last_checked_at: "2026-03-18T09:01:12Z",
          },
        ],
      },
    });
  });

  await page.goto("/");
  await expect(page.getByText("Pass-rate trend")).toBeVisible();
  await expect(page.getByText("Checkout UI Journeys").first()).toBeVisible();
});
