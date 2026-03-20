import { useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { YardMap } from "@/components/dashboard/yard-map";
import { RobotDrawer } from "@/components/fleet/robot-drawer";
import { Button } from "@/components/ui/button";
import { useOverviewQuery } from "@/hooks/use-roboyard";
import { formatDateTime, formatRelative } from "@/lib/format";

const axisStyle = { stroke: "#64748b", fontSize: 12 };

export function ConsolePage() {
  const overview = useOverviewQuery();
  const [selectedRobotId, setSelectedRobotId] = useState<string | null>(null);

  if (overview.isLoading) {
    return <LoadingState title="Loading command center" description="Building the live fleet map, telemetry summaries, and active mission lanes." />;
  }

  if (overview.isError) {
    return (
      <ErrorState
        title="Control console unavailable"
        description={overview.error instanceof Error ? overview.error.message : "The overview endpoint did not return a valid fleet snapshot."}
        action={<RetryButton onRetry={() => void overview.refetch()} />}
      />
    );
  }

  if (!overview.data || overview.data.robots.length === 0) {
    return (
      <EmptyState
        title="No robots in the yard"
        description="Seed the fleet or provision robots before opening the live mission control surface."
      />
    );
  }

  const activeRobotId = selectedRobotId ?? overview.data.robots[0]?.id ?? null;

  return (
    <>
      <PageHeader
        eyebrow="Realtime mission control"
        title="Autonomous fleet visibility with live telemetry, command issuance, and safety context."
        description="RoboYard Control streams operational state across mapped zones, mission lanes, charging stations, incident alerts, and operator interventions."
        actions={
          <div className="flex flex-wrap gap-3">
            <Button variant="outline">Weather {overview.data.weather.state}</Button>
            <Button>Dispatch window live</Button>
          </div>
        }
      />

      <div className="grid gap-4 lg:grid-cols-3 xl:grid-cols-6">
        {overview.data.metrics.map((metric) => (
          <MetricCard key={metric.label} metric={metric} />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.55fr_0.95fr]">
        <YardMap
          zones={overview.data.zones}
          robots={overview.data.robots}
          missions={overview.data.active_missions}
          alerts={overview.data.active_alerts}
          selectedRobotId={activeRobotId}
          onSelectRobot={setSelectedRobotId}
        />

        <div className="grid gap-4">
          <Panel title="Weather and safety cell" description="Realtime safety posture across the active demo zones.">
            <div className="grid gap-3">
              <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Current weather</div>
                    <div className="mt-2 font-display text-3xl text-white">{overview.data.weather.state}</div>
                  </div>
                  <StatusPill value={overview.data.weather.state} />
                </div>
                <div className="mt-4 text-sm text-slate-300">Intensity {overview.data.weather.intensity.toFixed(2)} • updated {formatRelative(overview.data.weather.updated_at)}</div>
              </div>

              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-1">
                {overview.data.active_alerts.length === 0 ? (
                  <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 text-sm text-muted-foreground">
                    No open alerts across the seeded fleet. The yard is currently operating within thresholds.
                  </div>
                ) : (
                  overview.data.active_alerts.slice(0, 4).map((alert) => (
                    <div key={alert.id} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="font-medium text-white">{alert.title}</div>
                          <div className="mt-1 text-sm text-muted-foreground">{alert.robot.name}</div>
                        </div>
                        <StatusPill value={alert.severity} />
                      </div>
                      <div className="mt-3 text-sm text-slate-300">{alert.message}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </Panel>

          <Panel title="Active missions" description="Mission windows currently running or staged for dispatch.">
        <div className="space-y-3">
              {overview.data.active_missions.length === 0 ? (
                <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 text-sm text-muted-foreground">
                  No mission windows are currently active or staged for dispatch.
                </div>
              ) : (
                overview.data.active_missions.slice(0, 5).map((mission) => (
                  <div key={mission.id} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="font-medium text-white">{mission.name}</div>
                        <div className="mt-1 text-sm text-muted-foreground">{mission.robot.name} • {mission.zone.name}</div>
                      </div>
                      <StatusPill value={mission.status} />
                    </div>
                    <div className="mt-4 h-2 rounded-full bg-white/5">
                      <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${mission.progress_pct}%` }} />
                    </div>
                    <div className="mt-2 text-sm text-muted-foreground">{mission.progress_pct.toFixed(1)}% complete • {mission.completed_area_sqm.toFixed(0)} sqm finished</div>
                  </div>
                ))
              )}
            </div>
          </Panel>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel title="Battery trend" description="Fleet-average battery trajectory from recent telemetry.">
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={overview.data.battery_trend}>
                <defs>
                  <linearGradient id="batteryGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.04} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="label" {...axisStyle} />
                <YAxis {...axisStyle} />
                <Tooltip contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }} />
                <Area type="monotone" dataKey="value" stroke="#38bdf8" fill="url(#batteryGradient)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Utilization" description="Operating share of the fleet over recent ticks.">
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={overview.data.utilization_trend}>
                <defs>
                  <linearGradient id="utilizationGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#34d399" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="#34d399" stopOpacity={0.03} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="label" {...axisStyle} />
                <YAxis {...axisStyle} />
                <Tooltip contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }} />
                <Area type="monotone" dataKey="value" stroke="#34d399" fill="url(#utilizationGradient)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Status distribution" description="Current spread of fleet operational states.">
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overview.data.fleet_status_distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="label" {...axisStyle} />
                <YAxis {...axisStyle} />
                <Tooltip contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }} />
                <Bar dataKey="value" radius={[12, 12, 0, 0]}>
                  {overview.data.fleet_status_distribution.map((entry) => (
                    <Cell key={entry.label} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Activity timeline" description="Operator-visible feed of mission events and recent alert bursts.">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {overview.data.activity.length === 0 ? (
            <div className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 text-sm text-muted-foreground">
              No mission or alert activity has been recorded yet.
            </div>
          ) : (
            overview.data.activity.map((item) => (
              <div key={item.id} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
                <div className="flex items-center justify-between gap-3">
                  <StatusPill value={item.category} />
                  <div className="text-xs text-muted-foreground">{formatDateTime(item.timestamp)}</div>
                </div>
                <div className="mt-3 font-medium text-white">{item.title}</div>
                <div className="mt-2 text-sm text-muted-foreground">{item.detail}</div>
              </div>
            ))
          )}
        </div>
      </Panel>

      <RobotDrawer robotId={activeRobotId} open={Boolean(activeRobotId)} onOpenChange={(next) => !next && setSelectedRobotId(null)} />
    </>
  );
}
