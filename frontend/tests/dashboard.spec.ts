import { test, expect } from "@playwright/test";

const authSession = {
  access_token: "demo-token",
  token_type: "bearer",
  user: {
    id: "user-1",
    email: "sre@signalops.dev",
    full_name: "SRE Commander",
    role: "sre",
  },
};

const service = {
  id: "svc-1",
  name: "Payment API",
  slug: "payment-api",
  owner: "Team Atlas",
  environment: "production",
  priority: "p0",
  sla_target: 99.95,
  description: "Payments",
  created_at: "2026-03-18T10:00:00Z",
  updated_at: "2026-03-18T10:00:00Z",
  health_score: 92,
  open_incidents: 2,
  open_alerts: 1,
};

test("renders dashboard with mocked API", async ({ page }) => {
  await page.addInitScript(([key, value]) => {
    window.localStorage.setItem(key, JSON.stringify(value));
  }, ["signalops-session", authSession]);

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({ json: authSession.user });
  });

  await page.route("**/api/v1/dashboard/overview", async (route) => {
    await route.fulfill({
      json: {
        metrics: [
          { label: "Open incidents", value: 3, delta: 2, suffix: "" },
          { label: "MTTR", value: 1.8, delta: -0.3, suffix: "h" },
          { label: "Error rate", value: 4.4, delta: 1.1, suffix: "%" },
          { label: "Service health", value: 91, delta: 0.5, suffix: "%" },
          { label: "Open alerts", value: 2, delta: 0.2, suffix: "" },
        ],
        incident_trend: [{ timestamp: "2026-03-18T09:00:00Z", value: 2 }],
        error_rate_trend: [{ timestamp: "2026-03-18T09:00:00Z", value: 4.4 }],
        alert_volume_trend: [{ timestamp: "2026-03-18T09:00:00Z", value: 1 }],
        services: [service],
        recent_incidents: [
          {
            id: "inc-1",
            title: "Payment API timeout burst",
            summary: "Grouped failures",
            root_cause_hint: "Database",
            status: "open",
            severity: "critical",
            environment: "production",
            group_key: "g1",
            first_seen_at: "2026-03-18T08:45:00Z",
            last_seen_at: "2026-03-18T09:00:00Z",
            resolved_at: null,
            occurrence_count: 10,
            affected_logs: 10,
            current_error_rate: 14,
            health_impact: 58,
            service,
            assignee: null,
            notes: [],
          },
        ],
        active_alerts: [
          {
            id: "alert-1",
            status: "open",
            message: "Payment error rate spike",
            current_value: 14,
            threshold: 8,
            triggered_at: "2026-03-18T09:00:00Z",
            acknowledged_at: null,
            resolved_at: null,
            suppressed_until: null,
            escalation_level: 0,
            service,
            rule: {
              id: "rule-1",
              name: "Payment error rate spike",
              description: "demo",
              metric: "error_rate",
              threshold: 8,
              window_minutes: 15,
              severity: "critical",
              enabled: true,
              suppression_minutes: 20,
              escalate_after_minutes: 20,
              service,
            },
            incident: null,
          },
        ],
      },
    });
  });

  await page.goto("/");
  await expect(page.getByRole("heading", { name: /reliability posture/i })).toBeVisible();
  await expect(page.getByText("Reliability trendline")).toBeVisible();
  await expect(page.locator("text=Payment API").first()).toBeVisible();
});
