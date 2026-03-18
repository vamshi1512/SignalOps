import type {
  Alert,
  AlertRule,
  AuditEntry,
  AuthSession,
  DashboardOverview,
  Incident,
  ListResponse,
  LogEvent,
  Service,
  User,
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
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const body = await response.json();
      message = body.error?.message ?? message;
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
  incidents(token: string, params: URLSearchParams) {
    return request<ListResponse<Incident>>(`/incidents?${params.toString()}`, { method: "GET" }, token);
  },
  incident(token: string, incidentId: string) {
    return request<Incident>(`/incidents/${incidentId}`, { method: "GET" }, token);
  },
  updateIncident(token: string, incidentId: string, payload: Record<string, unknown>) {
    return request<Incident>(
      `/incidents/${incidentId}`,
      { method: "PATCH", body: JSON.stringify(payload) },
      token,
    );
  },
  addIncidentNote(token: string, incidentId: string, content: string) {
    return request(`/incidents/${incidentId}/notes`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }, token);
  },
  logs(token: string, params: URLSearchParams) {
    return request<ListResponse<LogEvent>>(`/logs?${params.toString()}`, { method: "GET" }, token);
  },
  services(token: string) {
    return request<ListResponse<Service>>("/services", { method: "GET" }, token);
  },
  createService(token: string, payload: Record<string, unknown>) {
    return request<Service>("/services", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  alerts(token: string, params: URLSearchParams) {
    return request<ListResponse<Alert>>(`/alerts?${params.toString()}`, { method: "GET" }, token);
  },
  rules(token: string) {
    return request<ListResponse<AlertRule>>("/alerts/rules", { method: "GET" }, token);
  },
  createRule(token: string, payload: Record<string, unknown>) {
    return request<AlertRule>("/alerts/rules", { method: "POST", body: JSON.stringify(payload) }, token);
  },
  acknowledgeAlert(token: string, alertId: string) {
    return request<Alert>(`/alerts/${alertId}/acknowledge`, { method: "POST" }, token);
  },
  suppressAlert(token: string, alertId: string, minutes: number) {
    return request<Alert>(
      `/alerts/${alertId}/suppress`,
      { method: "POST", body: JSON.stringify({ minutes }) },
      token,
    );
  },
  audit(token: string) {
    return request<ListResponse<AuditEntry>>("/audit", { method: "GET" }, token);
  },
};
