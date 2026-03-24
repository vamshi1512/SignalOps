export type UserRole = "admin" | "qa_engineer" | "viewer";
export type EnvironmentKind = "qa" | "staging" | "prod_like" | "mock";
export type EnvironmentStatus = "healthy" | "degraded" | "offline";
export type SuiteType = "api" | "ui";
export type SuiteStatus = "active" | "draft" | "paused";
export type RunStatus = "queued" | "running" | "passed" | "failed" | "partial" | "cancelled";
export type ResultStatus = "passed" | "failed" | "skipped" | "flaky";
export type TriggerType = "manual" | "scheduled" | "demo";
export type NotificationChannel = "slack" | "email" | "webhook";
export type NotificationStatus = "pending" | "sent" | "skipped";

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

export interface Project {
  id: string;
  name: string;
  slug: string;
  owner: string;
  repository_url: string;
  default_branch: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Environment {
  id: string;
  project_id: string;
  name: string;
  slug: string;
  kind: EnvironmentKind;
  status: EnvironmentStatus;
  api_base_url: string;
  ui_base_url: string;
  health_summary: string;
  variables: Record<string, string>;
  is_default: boolean;
  last_checked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface FixtureSet {
  id: string;
  project_id: string;
  name: string;
  description: string;
  payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SuiteCase {
  id: string;
  key: string;
  name: string;
  module_name: string;
  order_index: number;
  automation_ref: string;
  expected_outcome: string;
  deterministic_profile: string;
  baseline_duration_ms: number;
  tags: string[];
  fixture_overrides: Record<string, unknown>;
}

export interface Schedule {
  id: string;
  suite_id: string;
  environment_id: string;
  name: string;
  cadence_minutes: number;
  next_run_at: string;
  last_run_at: string | null;
  parallel_workers: number;
  timezone: string;
  active: boolean;
  environment_name: string;
}

export interface SuiteSummary {
  id: string;
  name: string;
  slug: string;
  suite_type: SuiteType;
  owner: string;
  tags: string[];
  status: SuiteStatus;
}

export interface Suite extends SuiteSummary {
  description: string;
  repo_path: string;
  command: string;
  parallel_workers: number;
  is_flaky_watch: boolean;
  created_at: string;
  updated_at: string;
  project: Project;
  default_environment: Environment | null;
  default_fixture_set: FixtureSet | null;
  test_cases: SuiteCase[];
  schedules: Schedule[];
  latest_run_status: RunStatus | null;
  last_run_at: string | null;
  pass_rate_14d: number;
  flaky_cases: number;
}

export interface Attachment {
  label: string;
  type: string;
  url: string;
}

export interface TestResult {
  id: string;
  test_case_id: string | null;
  name: string;
  module_name: string;
  status: ResultStatus;
  retry_count: number;
  is_flaky: boolean;
  duration_ms: number;
  started_at: string;
  finished_at: string;
  error_message: string;
  stack_trace: string;
  logs: string;
  request_details: Record<string, unknown>;
  response_details: Record<string, unknown>;
  attachments: Attachment[];
}

export interface NotificationEvent {
  id: string;
  channel: NotificationChannel;
  status: NotificationStatus;
  recipient: string;
  subject: string;
  message: string;
  delivered_at: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface TestRun {
  id: string;
  trigger_type: TriggerType;
  status: RunStatus;
  requested_parallel_workers: number;
  total_count: number;
  pass_count: number;
  fail_count: number;
  skip_count: number;
  flaky_count: number;
  duration_ms: number;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  summary: Record<string, unknown>;
  metadata: Record<string, unknown>;
  project: Project;
  suite: SuiteSummary;
  environment: Environment;
  fixture_set: FixtureSet | null;
  schedule: Schedule | null;
  triggered_by: User | null;
}

export interface TestRunDetail extends TestRun {
  results: TestResult[];
  notifications: NotificationEvent[];
}

export interface AuditEntry {
  id: string;
  actor_id: string | null;
  actor_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
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

export interface FailureBreakdown {
  module_name: string;
  failures: number;
}

export interface SuiteRisk {
  id: string;
  name: string;
  suite_type: SuiteType;
  owner: string;
  latest_status: RunStatus | null;
  pass_rate_14d: number;
  flaky_cases: number;
  failing_results: number;
  environment_name: string | null;
}

export interface EnvironmentBadge {
  id: string;
  name: string;
  kind: EnvironmentKind;
  status: EnvironmentStatus;
  project_name: string;
  last_checked_at: string | null;
}

export interface DashboardOverview {
  metrics: MetricCard[];
  pass_rate_trend: TimeSeriesPoint[];
  duration_trend: TimeSeriesPoint[];
  flaky_trend: TimeSeriesPoint[];
  failures_by_module: FailureBreakdown[];
  recent_runs: TestRun[];
  suites_at_risk: SuiteRisk[];
  environments: EnvironmentBadge[];
}
