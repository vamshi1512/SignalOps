export type UserRole = "admin" | "operator" | "viewer";
export type ZoneType = "primary" | "task" | "charging" | "no_go";
export type RobotType = "lawn_mower" | "utility" | "inspection";
export type RobotStatus =
  | "idle"
  | "operating"
  | "paused"
  | "charging"
  | "returning_home"
  | "fault"
  | "manual_override"
  | "weather_paused";
export type OperatingMode = "autonomous" | "manual" | "emergency_stop";
export type ConnectivityState = "online" | "degraded" | "offline";
export type MissionType = "mow" | "inspect" | "patrol" | "haul";
export type MissionStatus = "scheduled" | "active" | "paused" | "returning_home" | "completed" | "aborted";
export type AlertSeverity = "info" | "warning" | "critical";
export type AlertStatus = "open" | "acknowledged" | "resolved";
export type AlertType =
  | "low_battery"
  | "stuck_robot"
  | "collision_risk"
  | "obstacle_detected"
  | "weather_safety"
  | "lost_connectivity"
  | "geofence_breach"
  | "operator_override"
  | "charging_cycle";
export type WeatherState = "clear" | "drizzle" | "rain" | "wind_gust" | "storm";

export interface ListResponse<T> {
  items: T[];
  total: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  title: string;
  role: UserRole;
  theme_preference: string;
  settings: Record<string, unknown>;
  is_active: boolean;
}

export interface AuthSession {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Zone {
  id: string;
  name: string;
  slug: string;
  description: string;
  zone_type: ZoneType;
  color: string;
  boundary: Array<{ x: number; y: number }>;
  charging_station: { x: number; y: number };
  task_areas: Array<Record<string, unknown>>;
  weather_exposure: number;
  is_active: boolean;
}

export interface MissionSummary {
  id: string;
  name: string;
  mission_type: MissionType;
  status: MissionStatus;
  progress_pct: number;
  scheduled_start: string | null;
  scheduled_end: string | null;
}

export interface Robot {
  id: string;
  name: string;
  slug: string;
  robot_type: RobotType;
  model: string;
  serial: string;
  firmware_version: string;
  status: RobotStatus;
  operating_mode: OperatingMode;
  connectivity_state: ConnectivityState;
  position_x: number;
  position_y: number;
  heading_deg: number;
  speed_mps: number;
  battery_level: number;
  signal_strength: number;
  tool_state: string;
  status_reason: string;
  total_runtime_minutes: number;
  total_distance_m: number;
  charging_cycles: number;
  health_score: number;
  deterministic_seed: number;
  last_seen_at: string;
  created_at: string;
  updated_at: string;
  zone: Pick<Zone, "id" | "name" | "slug" | "color">;
}

export interface RobotDetail extends Robot {
  active_mission: MissionSummary | null;
}

export interface Mission {
  id: string;
  name: string;
  mission_type: MissionType;
  status: MissionStatus;
  scheduled_start: string | null;
  scheduled_end: string | null;
  started_at: string | null;
  completed_at: string | null;
  estimated_duration_minutes: number;
  progress_pct: number;
  target_area_sqm: number;
  completed_area_sqm: number;
  command_queue: Array<Record<string, string>>;
  route_points: Array<{ x: number; y: number }>;
  replay_seed: number;
  operator_notes: string;
  created_at: string;
  updated_at: string;
  robot: {
    id: string;
    name: string;
    status: RobotStatus;
    battery_level: number;
  };
  zone: Pick<Zone, "id" | "name" | "slug" | "color">;
}

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  message: string;
  notes: string;
  metadata: Record<string, string>;
  occurred_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  robot: {
    id: string;
    name: string;
    status: RobotStatus;
    battery_level: number;
  };
  mission: MissionSummary | null;
}

export interface AuditEntry {
  id: string;
  actor_id: string | null;
  actor_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  message: string;
  details: Record<string, string>;
  created_at: string;
}

export interface TelemetryPoint {
  id: string;
  recorded_at: string;
  position_x: number;
  position_y: number;
  battery_level: number;
  speed_mps: number;
  mission_progress_pct: number;
  connectivity_state: ConnectivityState;
  robot_status: RobotStatus;
  operating_mode: OperatingMode;
  weather_state: WeatherState;
  payload: Record<string, unknown>;
}

export interface MissionEvent {
  id: string;
  occurred_at: string;
  category: string;
  event_type: string;
  message: string;
  payload: Record<string, unknown>;
}

export interface RobotHistory {
  robot: RobotDetail;
  telemetry: TelemetryPoint[];
  events: MissionEvent[];
  missions: Mission[];
  alerts: Alert[];
}

export interface MissionReplay {
  mission: Mission;
  telemetry: TelemetryPoint[];
  events: MissionEvent[];
}

export interface MetricCard {
  label: string;
  value: number;
  delta: number;
  suffix: string;
}

export interface TrendPoint {
  label: string;
  value: number;
}

export interface DistributionPoint {
  label: string;
  value: number;
  color: string;
}

export interface ActivityItem {
  id: string;
  timestamp: string;
  category: string;
  title: string;
  detail: string;
  robot_name: string | null;
}

export interface WeatherSnapshot {
  state: WeatherState;
  intensity: number;
  updated_at: string;
}

export interface DashboardOverview {
  generated_at: string;
  metrics: MetricCard[];
  fleet_status_distribution: DistributionPoint[];
  battery_trend: TrendPoint[];
  utilization_trend: TrendPoint[];
  mission_area_trend: TrendPoint[];
  alert_frequency_trend: TrendPoint[];
  downtime_by_robot: DistributionPoint[];
  robots: RobotDetail[];
  zones: Zone[];
  active_alerts: Alert[];
  active_missions: Mission[];
  activity: ActivityItem[];
  weather: WeatherSnapshot;
}

export interface PlatformConfig {
  id: string;
  name: string;
  weather_enabled: boolean;
  demo_mode: boolean;
  deterministic_mode: boolean;
  rain_pause_enabled: boolean;
  low_battery_threshold: number;
  collision_threshold: number;
  geofence_tolerance_m: number;
  simulator_tick_seconds: number;
  current_weather: WeatherState;
  weather_intensity: number;
}

export interface DemoAccount {
  email: string;
  full_name: string;
  title: string;
  password: string;
  role: UserRole;
}

export interface LiveFleetMessage {
  type: "fleet_tick" | "connected";
  timestamp?: string;
  weather?: { state: WeatherState; intensity: number };
  robots?: RobotDetail[];
  alerts?: Alert[];
}
