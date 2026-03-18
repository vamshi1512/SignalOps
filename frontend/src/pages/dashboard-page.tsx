import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { Skeleton } from "@/components/ui/skeleton";
import { useOverviewQuery } from "@/hooks/use-signalops";
import { formatDateTime, formatRelative } from "@/lib/format";

const axisStyle = {
  stroke: "#64748b",
  fontSize: 12,
};

export function DashboardPage() {
  const { data, isLoading } = useOverviewQuery();

  if (isLoading || !data) {
    return (
      <div className="grid gap-4">
        <Skeleton className="h-48" />
        <div className="grid gap-4 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-40" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Operations overview"
        title="Reliability posture across services, alerts, and incident response loops."
        description="A live SRE cockpit for service health, anomaly bursts, alert volumes, and the incidents that matter right now."
      />

      <div className="grid gap-4 lg:grid-cols-5">
        {data.metrics.map((metric, index) => (
          <div key={metric.label} className="animate-fade-up" style={{ animationDelay: `${index * 70}ms` }}>
            <MetricCard metric={metric} />
          </div>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.45fr_1fr]">
        <Panel title="Reliability trendline" description="Error-rate drift and incident pressure over the observed window.">
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.error_rate_trend}>
                <defs>
                  <linearGradient id="errorGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.45} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="timestamp" tickFormatter={formatDateTime} {...axisStyle} />
                <YAxis {...axisStyle} />
                <Tooltip
                  contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }}
                  labelFormatter={(value) => formatDateTime(String(value))}
                />
                <Area type="monotone" dataKey="value" stroke="#38bdf8" fill="url(#errorGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Alert volume" description="Threshold rule pressure by hour.">
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.alert_volume_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="timestamp" tickFormatter={formatDateTime} {...axisStyle} />
                <YAxis {...axisStyle} />
                <Tooltip
                  contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }}
                  labelFormatter={(value) => formatDateTime(String(value))}
                />
                <Line type="monotone" dataKey="value" stroke="#34d399" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel title="Service healthboard" description="SLA-aligned registry view with open incidents and alert pressure.">
          <div className="grid gap-4 md:grid-cols-2">
            {data.services.map((service) => (
              <div key={service.id} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="font-display text-xl text-white">{service.name}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{service.owner}</div>
                  </div>
                  <StatusPill value={service.environment} />
                </div>
                <div className="mt-5 grid grid-cols-3 gap-3">
                  <ServiceStat label="Health" value={`${service.health_score.toFixed(0)}%`} />
                  <ServiceStat label="Incidents" value={`${service.open_incidents}`} />
                  <ServiceStat label="Alerts" value={`${service.open_alerts}`} />
                </div>
                <div className="mt-5 flex items-center justify-between">
                  <StatusPill value={service.priority} />
                  <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                    SLA {service.sla_target.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <div className="grid gap-4">
          <Panel title="Recent incidents" description="Newest clustered failures demanding operator attention.">
            <div className="space-y-3">
              {data.recent_incidents.slice(0, 5).map((incident) => (
                <div key={incident.id} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusPill value={incident.status} />
                    <StatusPill value={incident.severity} />
                    <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                      {incident.service.name}
                    </span>
                  </div>
                  <div className="mt-3 font-medium text-white">{incident.title}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{incident.summary}</div>
                  <div className="mt-3 text-xs text-muted-foreground">
                    Last activity {formatRelative(incident.last_seen_at)}
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Active alerts" description="Current rule breaches across the platform.">
            <div className="space-y-3">
              {data.active_alerts.slice(0, 5).map((alert) => (
                <div key={alert.id} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-medium text-white">{alert.message}</div>
                      <div className="mt-1 text-sm text-muted-foreground">{alert.service.name}</div>
                    </div>
                    <StatusPill value={alert.status} />
                  </div>
                  <div className="mt-3 text-sm text-slate-300">
                    Current value {alert.current_value.toFixed(1)} / threshold {alert.threshold.toFixed(1)}
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </>
  );
}

function ServiceStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 font-display text-2xl text-white">{value}</div>
    </div>
  );
}

