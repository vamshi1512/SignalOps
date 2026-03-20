import { expect, test, type Page } from "@playwright/test";

const session = {
  access_token: "demo-token",
  token_type: "bearer",
  user: {
    id: "user-1",
    email: "ops@roboyard.dev",
    full_name: "Noah Vega",
    title: "Fleet operator",
    role: "operator",
    theme_preference: "dark",
    settings: { density: "comfortable" },
    is_active: true,
  },
};

function buildFixtures() {
  const zones = [
    {
      id: "zone-1",
      name: "North Course",
      slug: "north-course",
      description: "Primary mowing sector",
      zone_type: "primary",
      color: "#22c55e",
      boundary: [{ x: 24, y: 24 }, { x: 420, y: 24 }, { x: 420, y: 220 }, { x: 24, y: 220 }],
      charging_station: { x: 40, y: 40 },
      task_areas: [{ x: 80, y: 60, width: 130, height: 90 }],
      weather_exposure: 1,
      is_active: true,
    },
    {
      id: "zone-2",
      name: "Service Yard",
      slug: "service-yard",
      description: "Utility sector",
      zone_type: "primary",
      color: "#38bdf8",
      boundary: [{ x: 450, y: 30 }, { x: 780, y: 30 }, { x: 780, y: 240 }, { x: 450, y: 240 }],
      charging_station: { x: 470, y: 50 },
      task_areas: [{ x: 520, y: 80, width: 120, height: 70 }],
      weather_exposure: 0.8,
      is_active: true,
    },
  ];

  const robots = [
    {
      id: "robot-1",
      name: "RY-MOW-01",
      slug: "ry-mow-01",
      robot_type: "lawn_mower",
      model: "Atlas Trim 900",
      serial: "MOW-900-A1",
      firmware_version: "v3.4.1",
      status: "operating",
      operating_mode: "autonomous",
      connectivity_state: "online",
      position_x: 130,
      position_y: 130,
      heading_deg: 80,
      speed_mps: 1.4,
      battery_level: 74,
      signal_strength: 91,
      tool_state: "cutting",
      status_reason: "Executing North Course Live Pass",
      total_runtime_minutes: 182,
      total_distance_m: 7340,
      charging_cycles: 11,
      health_score: 97,
      deterministic_seed: 11,
      last_seen_at: "2026-03-19T16:20:00Z",
      created_at: "2026-03-18T09:00:00Z",
      updated_at: "2026-03-19T16:20:00Z",
      zone: { id: "zone-1", name: "North Course", slug: "north-course", color: "#22c55e" },
      active_mission: {
        id: "mission-1",
        name: "North Course Live Pass",
        mission_type: "mow",
        status: "active",
        progress_pct: 47,
        scheduled_start: "2026-03-19T16:00:00Z",
        scheduled_end: "2026-03-19T17:00:00Z",
      },
    },
    {
      id: "robot-2",
      name: "RY-UTIL-03",
      slug: "ry-util-03",
      robot_type: "utility",
      model: "Cargo Mule X",
      serial: "UTIL-X3",
      firmware_version: "v2.8.9",
      status: "charging",
      operating_mode: "autonomous",
      connectivity_state: "degraded",
      position_x: 470,
      position_y: 50,
      heading_deg: 0,
      speed_mps: 0,
      battery_level: 39,
      signal_strength: 52,
      tool_state: "standby",
      status_reason: "Charging before next dispatch window",
      total_runtime_minutes: 144,
      total_distance_m: 5210,
      charging_cycles: 8,
      health_score: 93,
      deterministic_seed: 23,
      last_seen_at: "2026-03-19T16:20:00Z",
      created_at: "2026-03-18T09:00:00Z",
      updated_at: "2026-03-19T16:20:00Z",
      zone: { id: "zone-2", name: "Service Yard", slug: "service-yard", color: "#38bdf8" },
      active_mission: {
        id: "mission-2",
        name: "Service Yard Live Pass",
        mission_type: "haul",
        status: "scheduled",
        progress_pct: 0,
        scheduled_start: "2026-03-19T17:00:00Z",
        scheduled_end: "2026-03-19T18:00:00Z",
      },
    },
  ];

  const missions = [
    {
      id: "mission-1",
      name: "North Course Live Pass",
      mission_type: "mow",
      status: "active",
      scheduled_start: "2026-03-19T16:00:00Z",
      scheduled_end: "2026-03-19T17:00:00Z",
      started_at: "2026-03-19T16:05:00Z",
      completed_at: null,
      estimated_duration_minutes: 62,
      progress_pct: 47,
      target_area_sqm: 860,
      completed_area_sqm: 404,
      command_queue: [],
      route_points: [
        { x: 40, y: 40 },
        { x: 80, y: 40 },
        { x: 80, y: 180 },
        { x: 150, y: 180 },
        { x: 150, y: 40 },
      ],
      replay_seed: 11,
      operator_notes: "Seeded active mission",
      created_at: "2026-03-19T15:55:00Z",
      updated_at: "2026-03-19T16:20:00Z",
      robot: { id: "robot-1", name: "RY-MOW-01", status: "operating", battery_level: 74 },
      zone: { id: "zone-1", name: "North Course", slug: "north-course", color: "#22c55e" },
    },
    {
      id: "mission-2",
      name: "Service Yard Live Pass",
      mission_type: "haul",
      status: "scheduled",
      scheduled_start: "2026-03-19T17:00:00Z",
      scheduled_end: "2026-03-19T18:00:00Z",
      started_at: null,
      completed_at: null,
      estimated_duration_minutes: 54,
      progress_pct: 0,
      target_area_sqm: 640,
      completed_area_sqm: 0,
      command_queue: [],
      route_points: [
        { x: 470, y: 50 },
        { x: 520, y: 50 },
        { x: 520, y: 180 },
      ],
      replay_seed: 23,
      operator_notes: "Seeded scheduled mission",
      created_at: "2026-03-19T15:50:00Z",
      updated_at: "2026-03-19T16:20:00Z",
      robot: { id: "robot-2", name: "RY-UTIL-03", status: "charging", battery_level: 39 },
      zone: { id: "zone-2", name: "Service Yard", slug: "service-yard", color: "#38bdf8" },
    },
  ];

  const alerts = [
    {
      id: "alert-1",
      type: "obstacle_detected",
      severity: "warning",
      status: "open",
      title: "Obstacle cluster in mowing lane",
      message: "Front lidar picked up an obstacle cluster near Fairway A.",
      notes: "",
      metadata: { zone: "Fairway A" },
      occurred_at: "2026-03-19T16:15:00Z",
      acknowledged_at: null,
      resolved_at: null,
      robot: { id: "robot-1", name: "RY-MOW-01", status: "operating", battery_level: 74 },
      mission: robots[0].active_mission,
    },
    {
      id: "alert-2",
      type: "lost_connectivity",
      severity: "warning",
      status: "acknowledged",
      title: "Telemetry signal degraded",
      message: "Mesh signal dropped below the degraded threshold for 12 seconds.",
      notes: "Acknowledged from test",
      metadata: { rssi: "-85" },
      occurred_at: "2026-03-19T16:10:00Z",
      acknowledged_at: "2026-03-19T16:14:00Z",
      resolved_at: null,
      robot: { id: "robot-2", name: "RY-UTIL-03", status: "charging", battery_level: 39 },
      mission: robots[1].active_mission,
    },
  ];

  const overview = {
    generated_at: "2026-03-19T16:20:00Z",
    metrics: [
      { label: "Live Robots", value: 1, delta: 1, suffix: "" },
      { label: "Fleet Utilization", value: 50, delta: 4.6, suffix: "%" },
      { label: "Completed Area", value: 404, delta: 18.4, suffix: " sqm" },
      { label: "Open Alerts", value: 1, delta: -2, suffix: "" },
      { label: "Charging Cycles", value: 19, delta: 6, suffix: "" },
      { label: "Avg Mission", value: 58, delta: -1.2, suffix: " min" },
    ],
    fleet_status_distribution: [
      { label: "operating", value: 1, color: "#22c55e" },
      { label: "charging", value: 1, color: "#38bdf8" },
    ],
    battery_trend: [
      { label: "16:00", value: 82 },
      { label: "16:10", value: 77 },
      { label: "16:20", value: 74 },
    ],
    utilization_trend: [
      { label: "16:00", value: 48 },
      { label: "16:10", value: 51 },
      { label: "16:20", value: 50 },
    ],
    mission_area_trend: [
      { label: "Tue", value: 680 },
      { label: "Wed", value: 720 },
      { label: "Thu", value: 860 },
    ],
    alert_frequency_trend: [
      { label: "16:00", value: 1 },
      { label: "16:10", value: 2 },
      { label: "16:20", value: 1 },
    ],
    downtime_by_robot: [
      { label: "RY-MOW-01", value: 18, color: "#22c55e" },
      { label: "RY-UTIL-03", value: 62, color: "#f59e0b" },
    ],
    robots,
    zones,
    active_alerts: alerts,
    active_missions: missions,
    activity: [
      {
        id: "evt-1",
        timestamp: "2026-03-19T16:18:00Z",
        category: "mission",
        title: "coverage sweep",
        detail: "North Course Live Pass continues under drizzle.",
        robot_name: "RY-MOW-01",
      },
    ],
    weather: { state: "drizzle", intensity: 0.18, updated_at: "2026-03-19T16:20:00Z" },
  };

  const robotHistory = {
    robot: robots[0],
    telemetry: [
      {
        id: "t-1",
        recorded_at: "2026-03-19T16:00:00Z",
        position_x: 60,
        position_y: 60,
        battery_level: 82,
        speed_mps: 1.4,
        mission_progress_pct: 10,
        connectivity_state: "online",
        robot_status: "operating",
        operating_mode: "autonomous",
        weather_state: "drizzle",
        payload: { heading_deg: 45 },
      },
      {
        id: "t-2",
        recorded_at: "2026-03-19T16:20:00Z",
        position_x: 130,
        position_y: 130,
        battery_level: 74,
        speed_mps: 1.4,
        mission_progress_pct: 47,
        connectivity_state: "online",
        robot_status: "operating",
        operating_mode: "autonomous",
        weather_state: "drizzle",
        payload: { heading_deg: 80 },
      },
    ],
    events: [
      {
        id: "e-1",
        occurred_at: "2026-03-19T16:10:00Z",
        category: "mission",
        event_type: "mission_started",
        message: "North Course Live Pass started",
        payload: {},
      },
    ],
    missions,
    alerts,
  };

  const missionReplay = {
    mission: missions[0],
    telemetry: robotHistory.telemetry,
    events: robotHistory.events,
  };

  return { zones, robots, missions, alerts, overview, robotHistory, missionReplay };
}

async function mockRoboYard(page: Page, options?: { persistSession?: boolean }) {
  const fixtures = buildFixtures();

  await page.addInitScript(({ sessionValue, withSession }) => {
    if (withSession) {
      window.localStorage.setItem("roboyard-session", JSON.stringify(sessionValue));
    }
    class MockWebSocket {
      onopen: (() => void) | null = null;
      onmessage: ((event: { data: string }) => void) | null = null;
      onclose: (() => void) | null = null;
      constructor() {
        setTimeout(() => {
          this.onopen?.();
          this.onmessage?.({ data: JSON.stringify({ type: "connected" }) });
        }, 30);
      }
      send() {}
      close() {
        this.onclose?.();
      }
    }
    // @ts-expect-error test stub
    window.WebSocket = MockWebSocket;
  }, { sessionValue: session, withSession: options?.persistSession ?? false });

  await page.route("**/api/v1/**", async (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();

    if (path.endsWith("/system/demo-accounts")) {
      return route.fulfill({
        json: [
          { email: "admin@roboyard.dev", full_name: "Avery Stone", title: "Mission lead", password: "Admin123!", role: "admin" },
          { email: "ops@roboyard.dev", full_name: "Noah Vega", title: "Fleet operator", password: "Ops123!", role: "operator" },
          { email: "viewer@roboyard.dev", full_name: "Mila Hart", title: "Operations analyst", password: "Viewer123!", role: "viewer" },
        ],
      });
    }
    if (path.endsWith("/auth/login") && method === "POST") {
      return route.fulfill({ json: session });
    }
    if (path.endsWith("/auth/me")) {
      return route.fulfill({ json: session.user });
    }
    if (path.endsWith("/dashboard/overview")) {
      return route.fulfill({ json: fixtures.overview });
    }
    if (path.endsWith("/fleet/zones")) {
      return route.fulfill({ json: { items: fixtures.zones, total: fixtures.zones.length } });
    }
    if (path.endsWith("/fleet/robots")) {
      return route.fulfill({ json: { items: fixtures.robots, total: fixtures.robots.length } });
    }
    if (path.includes("/fleet/robots/")) {
      return route.fulfill({ json: fixtures.robots[0] });
    }
    if (path.endsWith("/missions")) {
      return route.fulfill({ json: { items: fixtures.missions, total: fixtures.missions.length } });
    }
    if (path.includes("/missions/robots/") && path.endsWith("/commands") && method === "POST") {
      fixtures.missions[0].status = "paused";
      fixtures.robots[0].status = "paused";
      return route.fulfill({ json: fixtures.missions[0] });
    }
    if (path.endsWith("/alerts")) {
      return route.fulfill({ json: { items: fixtures.alerts, total: fixtures.alerts.length } });
    }
    if (path.includes("/alerts/") && path.endsWith("/acknowledge")) {
      fixtures.alerts[0].status = "acknowledged";
      fixtures.alerts[0].notes = "Acknowledged from alert center";
      return route.fulfill({ json: fixtures.alerts[0] });
    }
    if (path.includes("/history/robots/")) {
      return route.fulfill({ json: fixtures.robotHistory });
    }
    if (path.includes("/history/missions/")) {
      return route.fulfill({ json: fixtures.missionReplay });
    }
    if (path.endsWith("/config")) {
      return route.fulfill({
        json: {
          id: "cfg-1",
          name: "default",
          weather_enabled: true,
          demo_mode: true,
          deterministic_mode: true,
          rain_pause_enabled: true,
          low_battery_threshold: 24,
          collision_threshold: 0.65,
          geofence_tolerance_m: 4,
          simulator_tick_seconds: 1,
          current_weather: "drizzle",
          weather_intensity: 0.18,
        },
      });
    }
    if (path.endsWith("/auth/users")) {
      return route.fulfill({ json: { items: [session.user], total: 1 } });
    }
    if (path.endsWith("/audit")) {
      return route.fulfill({
        json: {
          items: [
            {
              id: "audit-1",
              actor_id: session.user.id,
              actor_email: session.user.email,
              action: "mission.command.pause",
              resource_type: "mission",
              resource_id: "mission-1",
              message: "Issued pause to RY-MOW-01",
              details: {},
              created_at: "2026-03-19T16:20:00Z",
            },
          ],
          total: 1,
        },
      });
    }

    return route.fulfill({ json: {} });
  });
}

test("login flow reaches the control console", async ({ page }) => {
  await mockRoboYard(page);
  await page.goto("/login");
  await page.getByRole("button", { name: /enter roboyard control/i }).click();
  await expect(page.getByText(/operational map/i)).toBeVisible();
});

test("dashboard live view renders the map and mission console", async ({ page }) => {
  await mockRoboYard(page, { persistSession: true });
  await page.goto("/console");
  await expect(page.getByText(/fleet geofence, routing, and live robot position/i)).toBeVisible();
  await expect(page.getByRole("heading", { name: "RY-MOW-01" })).toBeVisible();
  await expect(page.getByText("North Course Live Pass", { exact: true }).first()).toBeVisible();
});

test("robot detail inspection opens from fleet page", async ({ page }) => {
  await mockRoboYard(page, { persistSession: true });
  await page.goto("/fleet");
  await page.getByRole("button", { name: /RY-MOW-01/i }).click();
  await expect(page.getByText(/Battery and progress replay/i)).toBeVisible();
  await expect(page.getByText(/Atlas Trim 900/i).last()).toBeVisible();
});

test("issue command from missions page", async ({ page }) => {
  await mockRoboYard(page, { persistSession: true });
  await page.goto("/missions");
  await page.getByRole("button", { name: /^pause$/i }).first().click();
  await expect(page.getByText(/paused/i)).toBeVisible();
});

test("alert acknowledgment flow updates the alert", async ({ page }) => {
  await mockRoboYard(page, { persistSession: true });
  await page.goto("/alerts");
  await page.getByRole("button", { name: /Obstacle cluster in mowing lane/i }).click();
  await page.getByRole("button", { name: /Acknowledge alert/i }).click();
  await expect(page.locator('[role="dialog"]').getByText("acknowledged", { exact: true })).toBeVisible();
});

test("replay session page renders mission replay", async ({ page }) => {
  await mockRoboYard(page, { persistSession: true });
  await page.goto("/history");
  await expect(page.getByText(/Mission replay/i)).toBeVisible();
  await expect(page.getByText(/mission started/i).first()).toBeVisible();
});
