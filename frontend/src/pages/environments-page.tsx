import { AlertTriangle, Boxes, FolderGit2, Orbit, RefreshCcw } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useEnvironmentsQuery,
  useFixturesQuery,
  useProjectsQuery,
  useSchedulesQuery,
  useUpdateScheduleMutation,
} from "@/hooks/use-testforge";
import { getErrorMessage } from "@/lib/api";
import { formatRelative } from "@/lib/format";

export function EnvironmentsPage() {
  const { data: projects, error: projectsError, isLoading: projectsLoading, refetch: refetchProjects } = useProjectsQuery();
  const { data: environments, error: environmentsError, isLoading: environmentsLoading, refetch: refetchEnvironments } = useEnvironmentsQuery();
  const { data: fixtures, error: fixturesError, isLoading: fixturesLoading, refetch: refetchFixtures } = useFixturesQuery();
  const { data: schedules, error: schedulesError, isLoading: schedulesLoading, refetch: refetchSchedules } = useSchedulesQuery();
  const updateScheduleMutation = useUpdateScheduleMutation();

  const isLoading = projectsLoading || environmentsLoading || fixturesLoading || schedulesLoading;
  if (isLoading) {
    return (
      <div className="grid gap-4">
        <Skeleton className="h-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  const queryError = projectsError ?? environmentsError ?? fixturesError ?? schedulesError;
  if (queryError || !projects || !environments || !fixtures || !schedules) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Environment data is unavailable"
        description={getErrorMessage(queryError, "One or more environment management queries failed.")}
        tone="error"
        action={
          <Button
            variant="outline"
            onClick={() => {
              void refetchProjects();
              void refetchEnvironments();
              void refetchFixtures();
              void refetchSchedules();
            }}
          >
            <RefreshCcw className="h-4 w-4" />
            Retry load
          </Button>
        }
      />
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Targeting and fixtures"
        title="Project, environment, fixture, and schedule management."
        description="Audit which projects exist, where suites execute, what fixture profiles they bind to, and how cadence behaves across QA, staging, and prod-like demos."
        meta={[
          { label: "Projects", value: `${projects.items.length}` },
          { label: "Environments", value: `${environments.items.length}` },
          { label: "Schedules", value: `${schedules.items.length}` },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <Panel title="Projects" description="Seeded repositories under active QA ownership.">
          {projects.items.length ? (
            <div className="grid gap-4 md:grid-cols-2">
              {projects.items.map((project) => (
                <div key={project.id} className="rounded-[28px] border border-border bg-background/25 p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-display text-xl text-foreground">{project.name}</div>
                      <div className="mt-1 text-sm text-muted-foreground">{project.owner}</div>
                    </div>
                    <FolderGit2 className="h-5 w-5 text-primary" />
                  </div>
                  <p className="mt-4 text-sm text-muted-foreground">{project.description}</p>
                  <div className="mt-4 rounded-2xl border border-border bg-card/70 p-3 text-sm text-foreground">
                    {project.repository_url}
                  </div>
                  <div className="mt-3 flex items-center justify-between text-sm text-muted-foreground">
                    <span>Default branch</span>
                    <span>{project.default_branch}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={FolderGit2} title="No projects seeded" description="Projects will appear here once the backend demo catalog is initialized." compact />
          )}
        </Panel>

        <Panel title="Fixture sets" description="Reusable demo datasets for API requests and browser flows.">
          {fixtures.items.length ? (
            <div className="grid gap-4">
              {fixtures.items.map((fixture) => (
                <div key={fixture.id} className="rounded-[28px] border border-border bg-background/25 p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="font-display text-xl text-foreground">{fixture.name}</div>
                      <div className="mt-1 text-sm text-muted-foreground">{fixture.description}</div>
                    </div>
                    <Boxes className="h-5 w-5 text-accent" />
                  </div>
                  <pre className="mt-4 overflow-x-auto rounded-2xl border border-border bg-card/70 p-3 text-xs text-foreground">
                    {JSON.stringify(fixture.payload, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={Boxes} title="No fixture sets found" description="Fixture payloads will appear here once projects have seeded data bindings." compact />
          )}
        </Panel>
      </div>

      {environments.items.length === 0 ? (
        <EmptyState
          icon={Orbit}
          title="No environments available"
          description="Seeded demo environments should appear here after backend startup."
        />
      ) : (
        <Panel title="Environments" description="Execution targets, health posture, and runtime variables.">
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
            {environments.items.map((environment) => (
              <div key={environment.id} className="rounded-[28px] border border-border bg-background/25 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="font-display text-xl text-foreground">{environment.name}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{environment.slug}</div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <StatusPill value={environment.kind} />
                    <StatusPill value={environment.status} />
                  </div>
                </div>
                <p className="mt-4 text-sm text-muted-foreground">{environment.health_summary}</p>
                <div className="mt-4 space-y-2 rounded-2xl border border-border bg-card/70 p-4 text-sm text-foreground">
                  <div>API: {environment.api_base_url}</div>
                  <div>UI: {environment.ui_base_url}</div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {Object.entries(environment.variables).map(([key, value]) => (
                    <span key={key} className="rounded-full border border-border bg-secondary/70 px-3 py-1 text-xs text-muted-foreground">
                      {key}: {value}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      <Panel title="Schedules" description="Upcoming cadence and quick pause/resume controls.">
        {schedules.items.length ? (
          <div className="grid gap-4">
            {schedules.items.map((schedule) => (
              <div key={schedule.id} className="flex flex-col gap-3 rounded-[24px] border border-border bg-background/25 p-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="font-medium text-foreground">{schedule.name}</div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    Every {schedule.cadence_minutes} min on {schedule.environment_name}
                  </div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    Next run {formatRelative(schedule.next_run_at)}
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <StatusPill value={schedule.active ? "active" : "paused"} />
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
              </div>
            ))}
          </div>
        ) : (
          <EmptyState icon={RefreshCcw} title="No schedules configured" description="Cadence controls will appear here once suites are assigned recurring runs." compact />
        )}
      </Panel>
    </>
  );
}
