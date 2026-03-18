export type UserRole = "admin" | "sre" | "viewer";
export type ServiceEnvironment = "production" | "staging" | "development";
export type ServicePriority = "p0" | "p1" | "p2" | "p3";
export type SeverityLevel = "info" | "warning" | "error" | "critical";
export type IncidentStatus = "open" | "acknowledged" | "investigating" | "resolved";
export type AlertStatus = "open" | "acknowledged" | "suppressed" | "escalated" | "resolved";
export type AlertMetric = "error_rate" | "critical_logs" | "anomaly_score" | "incident_count";

export interface ListResponse<T> {
  items: T[];
  total: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Service {
  id: string;
  name: string;
  slug: string;
  owner: string;
  environment: ServiceEnvironment;
  priority: ServicePriority;
  sla_target: number;
  description: string;
  created_at: string;
  updated_at: string;
  health_score: number;
  open_incidents: number;
  open_alerts: number;
}

export interface LogEvent {
  id: string;
  occurred_at: string;
  severity: SeverityLevel;
  message: string;
  source: string;
  tags: string[];
  metadata: Record<string, string>;
  fingerprint: string;
  anomaly_score: number;
  is_anomalous: boolean;
  service: Service;
}

export interface IncidentNote {
  id: string;
  content: string;
  is_system: boolean;
  created_at: string;
  author: User | null;
}

export interface Incident {
  id: string;
  title: string;
  summary: string;
  root_cause_hint: string;
  status: IncidentStatus;
  severity: SeverityLevel;
  environment: ServiceEnvironment;
  group_key: string;
  first_seen_at: string;
  last_seen_at: string;
  resolved_at: string | null;
  occurrence_count: number;
  affected_logs: number;
  current_error_rate: number;
  health_impact: number;
  service: Service;
  assignee: User | null;
  notes: IncidentNote[];
}

export interface AlertRule {
  id: string;
  name: string;
  description: string;
  metric: AlertMetric;
  threshold: number;
  window_minutes: number;
  severity: SeverityLevel;
  enabled: boolean;
  suppression_minutes: number;
  escalate_after_minutes: number;
  service: Service | null;
}

export interface Alert {
  id: string;
  status: AlertStatus;
  message: string;
  current_value: number;
  threshold: number;
  triggered_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  suppressed_until: string | null;
  escalation_level: number;
  service: Service;
  rule: AlertRule;
  incident: Incident | null;
}

export interface AuditEntry {
  id: string;
  actor_id: string | null;
  actor_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, string>;
  created_at: string;
  message: string;
}

export interface MetricCard {
  label: string;
  value: number;
  delta: number;
  suffix: string;
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface DashboardOverview {
  metrics: MetricCard[];
  incident_trend: TimeSeriesPoint[];
  error_rate_trend: TimeSeriesPoint[];
  alert_volume_trend: TimeSeriesPoint[];
  services: Service[];
  recent_incidents: Incident[];
  active_alerts: Alert[];
}

