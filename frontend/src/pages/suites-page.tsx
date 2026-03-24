import { startTransition, useDeferredValue, useState } from "react";
import { AlertTriangle, Play, RefreshCcw, Search, SlidersHorizontal } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { RunDetailDrawer } from "@/components/run-detail-drawer";
import { StatusPill } from "@/components/status-pill";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useLaunchSuiteRunMutation,
  useSuitesQuery,
  useUpdateScheduleMutation,
} from "@/hooks/use-testforge";
import { getErrorMessage } from "@/lib/api";
import { formatDurationMs, formatPercent, formatRelative } from "@/lib/format";
import type { SuiteType } from "@/types/api";

const filters: Array<"all" | SuiteType> = ["all", "api", "ui"];

export function SuitesPage() {
  const { data, error, isError, isLoading, refetch } = useSuitesQuery();
  const launchMutation = useLaunchSuiteRunMutation();
  const updateScheduleMutation = useUpdateScheduleMutation();
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<"all" | SuiteType>("all");
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const deferredSearch = useDeferredValue(search);

  const suites =
    data?.items.filter((suite) => {
      const matchesType = selectedType === "all" || suite.suite_type === selectedType;
      const term = deferredSearch.trim().toLowerCase();
      const matchesSearch =
        !term ||
        suite.name.toLowerCase().includes(term) ||
        suite.owner.toLowerCase().includes(term) ||
        suite.tags.some((tag) => tag.includes(term));
      return matchesType && matchesSearch;
    }) ?? [];

  async function handleLaunch(suiteId: string) {
    const run = await launchMutation.mutateAsync({ suiteId, payload: {} });
    setSelectedRunId(run.id);
  }

  if (isLoading) {
    return (
      <div className="grid gap-4">
        <Skeleton className="h-48" />
        <Skeleton className="h-72" />
        <Skeleton className="h-72" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Suites could not be loaded"
        description={getErrorMessage(error, "The suite inventory API returned an error.")}
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

  const scheduledSuiteCount = data.items.filter((suite) => suite.schedules.length > 0).length;
  const flakyWatchCount = data.items.filter((suite) => suite.is_flaky_watch).length;

  return (
    <>
      <PageHeader
        eyebrow="Suite orchestration"
        title="Manage reusable API and UI automation suites."
        description="Review ownership, target environments, fixture bindings, schedule cadence, and launch any suite on demand from the console."
        meta={[
          { label: "Visible suites", value: `${suites.length}` },
          { label: "Scheduled suites", value: `${scheduledSuiteCount}` },
          { label: "Flaky watchlists", value: `${flakyWatchCount}` },
        ]}
        actions={
          <div className="flex w-full flex-col gap-3 md:w-auto md:flex-row">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="w-full pl-10 md:w-72"
                placeholder="Search suites, owners, tags"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {filters.map((filter) => (
                <Button
                  key={filter}
                  variant={selectedType === filter ? "default" : "outline"}
                  size="sm"
                  onClick={() => startTransition(() => setSelectedType(filter))}
                >
                  <SlidersHorizontal className="h-4 w-4" />
                  {filter}
                </Button>
              ))}
            </div>
          </div>
        }
      />

      {suites.length === 0 ? (
        <EmptyState
          icon={Play}
          title="No suites match the current filters"
          description="Adjust the search term or suite-type filter to explore the seeded automation inventory."
          action={
            <Button variant="outline" onClick={() => {
              setSearch("");
              setSelectedType("all");
            }}>
              Reset filters
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4">
          {suites.map((suite) => (
            <Panel
              key={suite.id}
              title={suite.name}
              description={suite.description}
              action={
                <Button
                  size="sm"
                  onClick={() => handleLaunch(suite.id)}
                  disabled={launchMutation.isPending}
                >
                  <Play className="h-4 w-4" />
                  {launchMutation.isPending && launchMutation.variables?.suiteId === suite.id ? "Launching..." : "Run now"}
                </Button>
              }
            >
              <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <StatusPill value={suite.suite_type} />
                    <StatusPill value={suite.status} />
                    {suite.latest_run_status ? <StatusPill value={suite.latest_run_status} /> : null}
                    {suite.default_environment ? <StatusPill value={suite.default_environment.kind} /> : null}
                    {suite.is_flaky_watch ? <StatusPill value="flaky" /> : null}
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {suite.tags.map((tag) => (
                      <Badge key={tag} className="bg-background/45 text-muted-foreground">
                        {tag}
                      </Badge>
                    ))}
                  </div>

                  <div className="grid gap-3 md:grid-cols-4">
                    <SuiteStat label="Owner" value={suite.owner} />
                    <SuiteStat label="Pass rate" value={formatPercent(suite.pass_rate_14d)} />
                    <SuiteStat label="Flaky watch" value={`${suite.flaky_cases} cases`} />
                    <SuiteStat label="Parallel" value={`${suite.parallel_workers} workers`} />
                  </div>

                  <div className="rounded-[24px] border border-border bg-background/25 p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Command</div>
                    <div className="mt-2 break-all font-mono text-sm text-foreground">{suite.command}</div>
                    <div className="mt-3 text-sm text-muted-foreground">Repo path: {suite.repo_path}</div>
                  </div>

                  <div className="rounded-[24px] border border-border bg-background/25 p-4">
                    <div className="mb-3 text-xs uppercase tracking-[0.18em] text-muted-foreground">Cases</div>
                    <div className="space-y-3">
                      {suite.test_cases.map((testCase) => (
                        <div key={testCase.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-card/70 p-3 md:flex-row md:items-center md:justify-between">
                          <div>
                            <div className="font-medium text-foreground">{testCase.name}</div>
                            <div className="text-sm text-muted-foreground">{testCase.module_name}</div>
                          </div>
                          <div className="flex flex-wrap items-center gap-2">
                            <StatusPill value={testCase.deterministic_profile.includes("flaky") ? "flaky" : suite.suite_type} />
                            <span className="text-sm text-muted-foreground">{formatDurationMs(testCase.baseline_duration_ms)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-[24px] border border-border bg-background/25 p-4">
                    <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Targeting</div>
                    <div className="mt-3 space-y-3">
                      <InfoBlock label="Project" value={suite.project.name} />
                      <InfoBlock label="Environment" value={suite.default_environment?.name ?? "Not assigned"} />
                      <InfoBlock label="Fixtures" value={suite.default_fixture_set?.name ?? "Not assigned"} />
                      <InfoBlock label="Last run" value={suite.last_run_at ? formatRelative(suite.last_run_at) : "No runs yet"} />
                    </div>
                  </div>

                  <div className="rounded-[24px] border border-border bg-background/25 p-4">
                    <div className="mb-3 text-xs uppercase tracking-[0.18em] text-muted-foreground">Schedules</div>
                    {suite.schedules.length ? (
                      <div className="space-y-3">
                        {suite.schedules.map((schedule) => (
                          <div key={schedule.id} className="rounded-2xl border border-border bg-card/70 p-4">
                            <div className="flex items-start justify-between gap-4">
                              <div>
                                <div className="font-medium text-foreground">{schedule.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  Every {schedule.cadence_minutes} min · {schedule.environment_name}
                                </div>
                              </div>
                              <Button
                                variant={schedule.active ? "outline" : "default"}
                                size="sm"
                                onClick={() =>
                                  updateScheduleMutation.mutate({
                                    scheduleId: schedule.id,
                                    payload: { active: !schedule.active },
                                  })
                                }
                              >
                                {schedule.active ? "Pause" : "Resume"}
                              </Button>
                            </div>
                            <div className="mt-3 flex items-center justify-between text-sm text-muted-foreground">
                              <span>Next {formatRelative(schedule.next_run_at)}</span>
                              <StatusPill value={schedule.active ? "active" : "paused"} />
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <EmptyState
                        icon={RefreshCcw}
                        title="No schedules configured"
                        description="This suite can still be launched manually while cadence remains unassigned."
                        compact
                      />
                    )}
                  </div>
                </div>
              </div>
            </Panel>
          ))}
        </div>
      )}

      <RunDetailDrawer runId={selectedRunId} open={Boolean(selectedRunId)} onOpenChange={(open) => !open && setSelectedRunId(null)} />
    </>
  );
}

function SuiteStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card/70 p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card/70 px-4 py-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm text-foreground">{value}</div>
    </div>
  );
}
