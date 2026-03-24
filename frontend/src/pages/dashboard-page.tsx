import { useState } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { EmptyState } from "@/components/empty-state";
import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { RunDetailDrawer } from "@/components/run-detail-drawer";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useOverviewQuery } from "@/hooks/use-testforge";
import { getErrorMessage } from "@/lib/api";
import { formatDateTime, formatDurationMs, formatPercent, formatRelative } from "@/lib/format";

const axisStyle = {
  stroke: "hsl(var(--muted-foreground))",
  fontSize: 12,
};

const chartTooltipStyle = {
  background: "hsl(var(--card))",
  border: "1px solid hsl(var(--border))",
  borderRadius: 16,
};

export function DashboardPage() {
  const { data, error, isError, isLoading, refetch } = useOverviewQuery();
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="grid gap-4">
        <Skeleton className="h-52" />
        <div className="grid gap-4 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-36" />
          ))}
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Dashboard data is unavailable"
        description={getErrorMessage(error, "The overview API did not return a valid payload.")}
        tone="error"
        action={
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCcw className="h-4 w-4" />
            Retry load
          </Button>
        }
      />
    );
  }

  const attentionEnvironments = data.environments.filter((environment) => environment.status !== "healthy").length;

  return (
    <>
      <PageHeader
        eyebrow="Quality overview"
        title="Execution confidence across API and UI automation."
        description="Track pass-rate drift, flaky pressure, duration changes, and the suites that need engineering attention before releases go out."
        meta={[
          { label: "Recent runs", value: `${data.recent_runs.length}` },
          { label: "Suites at risk", value: `${data.suites_at_risk.length}` },
          { label: "Attention targets", value: `${attentionEnvironments}` },
        ]}
      />

      <div className="grid gap-4 lg:grid-cols-5">
        {data.metrics.map((metric, index) => (
          <div key={metric.label} className="animate-fade-up" style={{ animationDelay: `${index * 60}ms` }}>
            <MetricCard metric={metric} />
          </div>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.25fr_0.95fr]">
        <Panel eyebrow="Trend" title="Pass-rate trend" description="Fourteen-day stability across seeded and manually triggered runs.">
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.pass_rate_trend}>
                <defs>
                  <linearGradient id="passRateGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" tickFormatter={formatDateTime} {...axisStyle} />
                <YAxis {...axisStyle} domain={[0, 100]} />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  labelFormatter={(value) => formatDateTime(String(value))}
                />
                <Area type="monotone" dataKey="value" stroke="#38bdf8" fill="url(#passRateGradient)" strokeWidth={2.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel eyebrow="Runtime" title="Duration drift" description="Average suite runtime in minutes by execution day.">
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.duration_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" tickFormatter={formatDateTime} {...axisStyle} />
                <YAxis {...axisStyle} />
                <Tooltip
                  contentStyle={chartTooltipStyle}
                  labelFormatter={(value) => formatDateTime(String(value))}
                />
                <Line type="monotone" dataKey="value" stroke="#fb923c" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <Panel eyebrow="Stability" title="Flaky detections" description="Where retries and inconsistent assertions are accumulating.">
          {data.flaky_trend.length ? (
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.flaky_trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="timestamp" tickFormatter={formatDateTime} {...axisStyle} />
                  <YAxis {...axisStyle} />
                  <Tooltip contentStyle={chartTooltipStyle} labelFormatter={(value) => formatDateTime(String(value))} />
                  <Bar dataKey="value" fill="#fbbf24" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState
              icon={RefreshCcw}
              title="No flaky detections yet"
              description="Once seeded or manual runs record flaky retries, the stability trend will appear here."
              compact
            />
          )}
        </Panel>

        <Panel eyebrow="Hotspots" title="Failures by module" description="Current hotspot distribution for failing assertions.">
          {data.failures_by_module.length ? (
            <div className="space-y-3">
              {data.failures_by_module.map((item) => (
                <div key={item.module_name} className="surface-panel-subtle p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-medium text-foreground">{item.module_name}</div>
                    <StatusPill value="failed" />
                  </div>
                  <div className="mt-3 flex items-end justify-between">
                    <div className="text-3xl font-display text-foreground">{item.failures}</div>
                    <div className="text-sm text-muted-foreground">failing results</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={RefreshCcw}
              title="No module hotspots detected"
              description="Failing modules will be grouped here once a run records assertion failures."
              compact
            />
          )}
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel eyebrow="Watchlist" title="Suites at risk" description="Lowest pass-rate suites and the environments they are threatening.">
          {data.suites_at_risk.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {data.suites_at_risk.map((suite) => (
                <div key={suite.id} className="surface-panel-subtle p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="font-display text-xl text-foreground">{suite.name}</div>
                      <div className="mt-1 text-sm text-muted-foreground">{suite.owner}</div>
                    </div>
                    <StatusPill value={suite.suite_type} />
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {suite.latest_status ? <StatusPill value={suite.latest_status} /> : null}
                    {suite.environment_name ? (
                      <div className="rounded-full border border-border bg-card/70 px-3 py-1 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                        {suite.environment_name}
                      </div>
                    ) : null}
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-3">
                    <RiskStat label="Pass rate" value={formatPercent(suite.pass_rate_14d)} />
                    <RiskStat label="Flaky" value={`${suite.flaky_cases}`} />
                    <RiskStat label="Failures" value={`${suite.failing_results}`} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={RefreshCcw}
              title="No suites are currently flagged"
              description="Risk-ranked suites will appear here when pass-rate or flaky pressure drops below the healthy baseline."
              compact
            />
          )}
        </Panel>

        <div className="grid gap-4">
          <Panel eyebrow="Activity" title="Recent runs" description="Latest activity from manual launches and schedule triggers.">
            {data.recent_runs.length ? (
              <div className="space-y-3">
                {data.recent_runs.slice(0, 6).map((run) => (
                  <button
                    key={run.id}
                    type="button"
                    onClick={() => setSelectedRunId(run.id)}
                    className="w-full rounded-[24px] border border-border bg-background/25 p-4 text-left transition hover:bg-secondary/50"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusPill value={run.status} />
                      <StatusPill value={run.suite.suite_type} />
                      <StatusPill value={run.trigger_type} />
                    </div>
                    <div className="mt-3 font-medium text-foreground">{run.suite.name}</div>
                    <div className="mt-1 text-sm text-muted-foreground">
                      {run.environment.name} · {formatRelative(run.created_at)}
                    </div>
                    <div className="mt-3 flex items-center justify-between text-sm text-muted-foreground">
                      <span>
                        {run.pass_count}/{run.total_count} passed
                      </span>
                      <span>{formatDurationMs(run.duration_ms)}</span>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={RefreshCcw}
                title="No run history yet"
                description="Recent executions will appear here as soon as a seeded or manual launch completes."
                compact
              />
            )}
          </Panel>

          <Panel eyebrow="Targets" title="Environment posture" description="Current target health across seeded QA, staging, and mock environments.">
            {data.environments.length ? (
              <div className="grid gap-3">
                {data.environments.map((environment) => (
                  <div key={environment.id} className="flex items-center justify-between rounded-2xl border border-border bg-background/25 px-4 py-3">
                    <div>
                      <div className="font-medium text-foreground">{environment.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {environment.project_name}
                        {environment.last_checked_at ? ` · checked ${formatRelative(environment.last_checked_at)}` : ""}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <StatusPill value={environment.kind} />
                      <StatusPill value={environment.status} />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={RefreshCcw}
                title="No environment posture available"
                description="Seeded environments will appear here once the backend demo catalog is initialized."
                compact
              />
            )}
          </Panel>
        </div>
      </div>

      <RunDetailDrawer runId={selectedRunId} open={Boolean(selectedRunId)} onOpenChange={(open) => !open && setSelectedRunId(null)} />
    </>
  );
}

function RiskStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card/70 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 font-display text-2xl text-foreground">{value}</div>
    </div>
  );
}
