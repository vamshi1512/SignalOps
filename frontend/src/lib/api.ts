import type {
  Alert,
  AuditEntry,
  AuthSession,
  DashboardOverview,
  DemoAccount,
  ListResponse,
  Mission,
  MissionReplay,
  PlatformConfig,
  Robot,
  RobotDetail,
  RobotHistory,
  User,
  Zone,
} from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = (await response.json()) as { error?: { message?: string }; detail?: string };
      message = body.error?.message ?? body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function withQuery(path: string, params?: Record<string, string | number | boolean | undefined | null>) {
  const search = new URLSearchParams();
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

export const api = {
  login(email: string, password: string) {
    return request<AuthSession>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },
  me(token: string) {
    return request<User>("/auth/me", { method: "GET" }, token);
  },
  users(token: string) {
    return request<ListResponse<User>>("/auth/users", { method: "GET" }, token);
  },
  overview(token: string) {
    return request<DashboardOverview>("/dashboard/overview", { method: "GET" }, token);
  },
  robots(token: string, params?: Record<string, string | number | boolean | undefined>) {
    return request<ListResponse<Robot>>(withQuery("/fleet/robots", params), { method: "GET" }, token);
  },
  robot(token: string, robotId: string) {
    return request<RobotDetail>(`/fleet/robots/${robotId}`, { method: "GET" }, token);
  },
  zones(token: string) {
    return request<ListResponse<Zone>>("/fleet/zones", { method: "GET" }, token);
  },
  createRobot(token: string, payload: Record<string, unknown>) {
    return request<Robot>("/fleet/robots", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  updateRobot(token: string, robotId: string, payload: Record<string, unknown>) {
    return request<Robot>(`/fleet/robots/${robotId}`, { method: "PATCH", body: JSON.stringify(payload) }, token);
  },
  deleteRobot(token: string, robotId: string) {
    return request<{ message: string }>(`/fleet/robots/${robotId}`, { method: "DELETE" }, token);
  },
  missions(token: string, params?: Record<string, string | number | boolean | undefined>) {
    return request<ListResponse<Mission>>(withQuery("/missions", params), { method: "GET" }, token);
  },
  mission(token: string, missionId: string) {
    return request<Mission>(`/missions/${missionId}`, { method: "GET" }, token);
  },
  createMission(token: string, payload: Record<string, unknown>) {
    return request<Mission>("/missions", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  commandRobot(token: string, robotId: string, payload: { command: string; note?: string }) {
    return request<Mission>(`/missions/robots/${robotId}/commands`, { method: "POST", body: JSON.stringify(payload) }, token);
  },
  alerts(token: string, params?: Record<string, string | number | boolean | undefined>) {
    return request<ListResponse<Alert>>(withQuery("/alerts", params), { method: "GET" }, token);
  },
  acknowledgeAlert(token: string, alertId: string, notes: string) {
    return request<Alert>(`/alerts/${alertId}/acknowledge`, {
      method: "POST",
      body: JSON.stringify({ notes }),
    }, token);
  },
  robotHistory(token: string, robotId: string) {
    return request<RobotHistory>(`/history/robots/${robotId}`, { method: "GET" }, token);
  },
  missionReplay(token: string, missionId: string) {
    return request<MissionReplay>(`/history/missions/${missionId}/replay`, { method: "GET" }, token);
  },
  config(token: string) {
    return request<PlatformConfig>("/config", { method: "GET" }, token);
  },
  updateConfig(token: string, payload: Record<string, unknown>) {
    return request<PlatformConfig>("/config", { method: "PATCH", body: JSON.stringify(payload) }, token);
  },
  audit(token: string) {
    return request<ListResponse<AuditEntry>>("/audit", { method: "GET" }, token);
  },
  demoAccounts() {
    return request<DemoAccount[]>("/system/demo-accounts", { method: "GET" });
  },
  websocketUrl(token: string) {
    const configured = import.meta.env.VITE_WS_BASE_URL;
    if (configured) {
      return `${configured}?token=${encodeURIComponent(token)}`;
    }
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    return `${protocol}://${window.location.host}/api/v1/simulator/stream?token=${encodeURIComponent(token)}`;
  },
};
