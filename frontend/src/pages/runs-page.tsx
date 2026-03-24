import { useState } from "react";
import { AlertTriangle, ListFilter, PlaySquare, RefreshCcw } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { RunDetailDrawer } from "@/components/run-detail-drawer";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRunsQuery } from "@/hooks/use-testforge";
import { getErrorMessage } from "@/lib/api";
import { formatDurationMs, formatRelative } from "@/lib/format";
import type { RunStatus } from "@/types/api";

const filters: Array<"all" | RunStatus> = ["all", "failed", "partial", "passed", "queued", "running"];

export function RunsPage() {
  const [filter, setFilter] = useState<"all" | RunStatus>("all");
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const params = new URLSearchParams();
  if (filter !== "all") {
    params.set("status", filter);
  }
  const { data, error, isError, isLoading, refetch } = useRunsQuery(params);

  if (isLoading) {
    return (
      <div className="grid gap-4">
        <Skeleton className="h-48" />
        <Skeleton className="h-72" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Run history is unavailable"
        description={getErrorMessage(error, "The run explorer API returned an error.")}
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

  const runs = data.items;
  const failedRuns = runs.filter((run) => run.status === "failed").length;
  const partialRuns = runs.filter((run) => run.status === "partial").length;

  return (
    <>
      <PageHeader
        eyebrow="Run explorer"
        title="Trace execution history and inspect failure details."
        description="Review queued, running, passed, partial, and failed runs with direct access to UI screenshots, API traces, logs, and notifications."
        meta={[
          { label: "Visible runs", value: `${runs.length}` },
          { label: "Failed", value: `${failedRuns}` },
          { label: "Partial", value: `${partialRuns}` },
        ]}
        actions={
          <div className="flex flex-wrap gap-2">
            {filters.map((item) => (
              <Button key={item} variant={filter === item ? "default" : "outline"} size="sm" onClick={() => setFilter(item)}>
                <ListFilter className="h-4 w-4" />
                {item}
              </Button>
            ))}
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        <SummaryCard label="Visible runs" value={`${runs.length}`} />
        <SummaryCard label="Failed" value={`${failedRuns}`} />
        <SummaryCard label="Partial / flaky" value={`${partialRuns}`} />
      </div>

      {runs.length === 0 ? (
        <EmptyState
          icon={PlaySquare}
          title="No runs in this filter"
          description="Change the current filter to inspect seeded run history or trigger a suite manually from the Suites page."
          action={
            <Button variant="outline" onClick={() => setFilter("all")}>
              Clear filter
            </Button>
          }
        />
      ) : (
        <Panel title="Execution history" description="Each card opens a full run drawer with artifacts and notifications.">
          <div className="space-y-3">
            {runs.map((run) => (
              <button
                key={run.id}
                type="button"
                onClick={() => setSelectedRunId(run.id)}
                className="w-full rounded-[24px] border border-border bg-background/25 p-4 text-left transition hover:bg-secondary/50"
              >
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                  <div>
                    <div className="font-display text-xl text-foreground">{run.suite.name}</div>
                    <div className="mt-1 text-sm text-muted-foreground">
                      {run.project.name} · {run.environment.name} · {formatRelative(run.created_at)}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <StatusPill value={run.status} />
                    <StatusPill value={run.suite.suite_type} />
                    <StatusPill value={run.trigger_type} />
                  </div>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-5">
                  <RunStat label="Passed" value={`${run.pass_count}`} />
                  <RunStat label="Failed" value={`${run.fail_count}`} />
                  <RunStat label="Flaky" value={`${run.flaky_count}`} />
                  <RunStat label="Duration" value={formatDurationMs(run.duration_ms)} />
                  <RunStat label="Parallel" value={`${run.requested_parallel_workers}`} />
                </div>
              </button>
            ))}
          </div>
        </Panel>
      )}

      <RunDetailDrawer runId={selectedRunId} open={Boolean(selectedRunId)} onOpenChange={(open) => !open && setSelectedRunId(null)} />
    </>
  );
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="surface-panel p-5">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-3 font-display text-4xl text-foreground">{value}</div>
    </div>
  );
}

function RunStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card/70 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}
