import { useState } from "react";
import { ResponsiveContainer, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";

import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { useMissionReplayQuery, useRobotHistoryQuery, useRobotsQuery } from "@/hooks/use-roboyard";
import { formatDateTime } from "@/lib/format";

export function HistoryPage() {
  const robotsQuery = useRobotsQuery();
  const [robotId, setRobotId] = useState<string | undefined>();
  const [missionId, setMissionId] = useState<string | undefined>();
  const activeRobotId = robotId ?? robotsQuery.data?.items[0]?.id;
  const historyQuery = useRobotHistoryQuery(activeRobotId);
  const activeMissionId = missionId ?? historyQuery.data?.missions[0]?.id;
  const replayQuery = useMissionReplayQuery(activeMissionId);

  return (
    <>
      <PageHeader
        eyebrow="History and replay"
        title="Route replay, mission timeline, and operator action trace."
        description="Inspect robot telemetry after the fact, walk through mission sessions, and review event ordering."
      />

      <div className="flex flex-wrap gap-3">
        {robotsQuery.data?.items.map((robot) => (
          <Button key={robot.id} variant={activeRobotId === robot.id ? "default" : "outline"} onClick={() => setRobotId(robot.id)}>
            {robot.name}
          </Button>
        ))}
      </div>

      {robotsQuery.isLoading ? <LoadingState title="Loading replay index" description="Robots, event timelines, and mission sessions are being prepared." /> : null}
      {robotsQuery.isError ? (
        <ErrorState
          title="Replay index unavailable"
          description={robotsQuery.error instanceof Error ? robotsQuery.error.message : "Robot history could not be loaded."}
          action={<RetryButton onRetry={() => void robotsQuery.refetch()} />}
        />
      ) : null}
      {!robotsQuery.isLoading && !robotsQuery.isError && (robotsQuery.data?.items.length ?? 0) === 0 ? (
        <EmptyState title="No robots available for replay" description="Seed the fleet before opening the historical mission surfaces." />
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="surface-panel rounded-[32px] p-6">
          <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Robot telemetry history</div>
          {historyQuery.isLoading ? <LoadingState className="mt-4 min-h-[320px]" title="Loading telemetry trace" description="Robot history and event sequencing are being reconstructed." /> : null}
          {historyQuery.isError ? (
            <ErrorState
              className="mt-4 min-h-[320px]"
              title="Robot history unavailable"
              description={historyQuery.error instanceof Error ? historyQuery.error.message : "The selected robot history could not be loaded."}
              action={<RetryButton onRetry={() => void historyQuery.refetch()} />}
            />
          ) : null}
          {!historyQuery.isLoading && !historyQuery.isError ? (
            <>
              <div className="mt-4 h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historyQuery.data?.telemetry ?? []}>
                    <XAxis dataKey="recorded_at" tickFormatter={formatDateTime} stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }} />
                    <Line dataKey="battery_level" stroke="#38bdf8" dot={false} strokeWidth={2.2} />
                    <Line dataKey="mission_progress_pct" stroke="#34d399" dot={false} strokeWidth={2.2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-6 grid gap-3">
                {historyQuery.data?.events.length ? (
                  historyQuery.data.events.slice(0, 10).map((event) => (
                    <div key={event.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="font-medium text-white">{event.event_type.replace(/_/g, " ")}</div>
                        <div className="text-xs text-muted-foreground">{formatDateTime(event.occurred_at)}</div>
                      </div>
                      <div className="mt-2 text-sm text-muted-foreground">{event.message}</div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-muted-foreground">
                    No event markers were recorded for the selected robot session.
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>

        <div className="grid gap-4">
          <div className="surface-panel rounded-[32px] p-6">
            <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Mission replay</div>
            <div className="mt-4 flex flex-wrap gap-2">
              {historyQuery.data?.missions.map((mission) => (
                <Button key={mission.id} variant={activeMissionId === mission.id ? "default" : "outline"} size="sm" onClick={() => setMissionId(mission.id)}>
                  {mission.name}
                </Button>
              ))}
            </div>
            {replayQuery.isLoading ? <LoadingState className="mt-5 min-h-[280px]" title="Loading replay route" description="The selected mission trail is being reconstructed from seeded telemetry." /> : null}
            {replayQuery.isError ? (
              <ErrorState
                className="mt-5 min-h-[280px]"
                title="Replay route unavailable"
                description={replayQuery.error instanceof Error ? replayQuery.error.message : "The mission replay could not be generated."}
                action={<RetryButton onRetry={() => void replayQuery.refetch()} />}
              />
            ) : null}
            {!replayQuery.isLoading && !replayQuery.isError ? (
              <div className="mt-5 rounded-[28px] border border-white/10 bg-slate-950/70 p-4">
                <svg viewBox="0 0 760 320" className="h-[260px] w-full">
                  <rect width={760} height={320} fill="#020617" />
                  <polyline
                    points={(replayQuery.data?.telemetry ?? []).map((point) => `${point.position_x},${point.position_y}`).join(" ")}
                    fill="none"
                    stroke="#38bdf8"
                    strokeWidth={3}
                  />
                  {(replayQuery.data?.telemetry ?? []).slice(-1).map((point) => (
                    <circle key={point.id} cx={point.position_x} cy={point.position_y} r={8} fill="#34d399" />
                  ))}
                </svg>
              </div>
            ) : null}
          </div>

          <div className="surface-panel rounded-[32px] p-6">
            <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Replay event track</div>
            <div className="mt-4 grid gap-3">
              {replayQuery.data?.events.length ? (
                replayQuery.data.events.map((event) => (
                  <div key={event.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-medium text-white">{event.event_type.replace(/_/g, " ")}</div>
                      <StatusPill value={event.category} />
                    </div>
                    <div className="mt-2 text-sm text-muted-foreground">{event.message}</div>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-muted-foreground">
                  No replay events were recorded for the selected mission.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
