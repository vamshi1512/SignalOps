import type {
  AuditEntry,
  AuthSession,
  DashboardOverview,
  Environment,
  FixtureSet,
  ListResponse,
  NotificationEvent,
  Project,
  Schedule,
  Suite,
  TestRun,
  TestRunDetail,
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
  headers.set("Accept", "application/json");
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
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
      message = body.error?.message ?? body.detail ?? body.message ?? message;
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

export function getErrorMessage(error: unknown, fallback = "Unable to load data from TestForge.") {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string" && error.trim()) {
    return error;
  }
  return fallback;
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
  projects(token: string) {
    return request<ListResponse<Project>>("/projects", { method: "GET" }, token);
  },
  environments(token: string) {
    return request<ListResponse<Environment>>("/environments", { method: "GET" }, token);
  },
  fixtures(token: string) {
    return request<ListResponse<FixtureSet>>("/fixtures", { method: "GET" }, token);
  },
  suites(token: string) {
    return request<ListResponse<Suite>>("/suites", { method: "GET" }, token);
  },
  schedules(token: string) {
    return request<ListResponse<Schedule>>("/schedules", { method: "GET" }, token);
  },
  updateSchedule(token: string, scheduleId: string, payload: Record<string, unknown>) {
    return request<Schedule>(`/schedules/${scheduleId}`, { method: "PATCH", body: JSON.stringify(payload) }, token);
  },
  runs(token: string, params: URLSearchParams) {
    return request<ListResponse<TestRun>>(`/runs?${params.toString()}`, { method: "GET" }, token);
  },
  run(token: string, runId: string) {
    return request<TestRunDetail>(`/runs/${runId}`, { method: "GET" }, token);
  },
  launchSuiteRun(token: string, suiteId: string, payload: Record<string, unknown>) {
    return request<TestRun>(`/suites/${suiteId}/runs`, { method: "POST", body: JSON.stringify(payload) }, token);
  },
  notifications(token: string) {
    return request<ListResponse<NotificationEvent>>("/notifications", { method: "GET" }, token);
  },
  audit(token: string) {
    return request<ListResponse<AuditEntry>>("/audit", { method: "GET" }, token);
  },
};
