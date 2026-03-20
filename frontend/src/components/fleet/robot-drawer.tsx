import type { ReactNode } from "react";
import { ResponsiveContainer, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";

import { useAuth } from "@/auth/auth-provider";
import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useCommandRobotMutation, useRobotHistoryQuery, useRobotQuery } from "@/hooks/use-roboyard";
import { formatBattery, formatDateTime, formatDistance, formatRelative } from "@/lib/format";

export function RobotDrawer({
  robotId,
  open,
  onOpenChange,
}: {
  robotId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { session } = useAuth();
  const robotQuery = useRobotQuery(robotId ?? undefined);
  const historyQuery = useRobotHistoryQuery(robotId ?? undefined);
  const commandMutation = useCommandRobotMutation();

  const robot = robotQuery.data;
  const history = historyQuery.data;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[calc(100vh-2rem)] overflow-y-auto">
        {robotQuery.isLoading || historyQuery.isLoading ? (
          <LoadingState className="min-h-[320px]" title="Loading robot telemetry" description="History traces, mission context, and recent events are being assembled." />
        ) : null}

        {robotQuery.isError ? (
          <ErrorState
            className="min-h-[320px]"
            title="Robot detail unavailable"
            description={robotQuery.error instanceof Error ? robotQuery.error.message : "The selected robot could not be loaded."}
            action={
              <RetryButton
                onRetry={() => {
                  void robotQuery.refetch();
                  void historyQuery.refetch();
                }}
              />
            }
          />
        ) : null}

        {!robotQuery.isLoading && !robotQuery.isError && !robot ? (
          <EmptyState className="min-h-[320px]" title="No robot selected" description="Choose a fleet card to inspect telemetry, commands, and recent events." />
        ) : null}

        {!robotQuery.isLoading && !robotQuery.isError && robot ? (
          <>
            <DialogHeader>
              <DialogTitle>{robot.name}</DialogTitle>
              <DialogDescription>
                {robot.model} • {robot.serial} • last telemetry {formatRelative(robot.last_seen_at)}
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-6 p-6">
              <div className="grid gap-3 md:grid-cols-2">
                <StatCard label="Status" value={<StatusPill value={robot.status} />} />
                <StatCard label="Connectivity" value={<StatusPill value={robot.connectivity_state} />} />
                <StatCard label="Battery" value={formatBattery(robot.battery_level)} />
                <StatCard label="Distance" value={formatDistance(robot.total_distance_m)} />
                <StatCard label="Runtime" value={`${robot.total_runtime_minutes.toFixed(1)} min`} />
                <StatCard label="Zone" value={robot.zone.name} />
              </div>

              {robot.active_mission ? (
                <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Active mission</div>
                      <div className="mt-2 font-display text-2xl text-white">{robot.active_mission.name}</div>
                    </div>
                    <StatusPill value={robot.active_mission.status} />
                  </div>
                  <div className="mt-4 h-2 rounded-full bg-white/5">
                    <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${robot.active_mission.progress_pct}%` }} />
                  </div>
                  <div className="mt-2 text-sm text-muted-foreground">{robot.active_mission.progress_pct.toFixed(1)}% mission completion</div>
                </div>
              ) : null}

              <div className="grid gap-3 md:grid-cols-3">
                {[
                  ["pause", "Pause mission"],
                  ["resume", "Resume autonomy"],
                  ["return_to_base", "Return to base"],
                  ["manual_override", "Manual override"],
                  ["clear_override", "Clear override"],
                  ["emergency_stop", "Emergency stop"],
                ].map(([command, label]) => (
                  <Button
                    key={command}
                    variant={command === "emergency_stop" ? "danger" : "outline"}
                    disabled={commandMutation.isPending}
                    onClick={() => {
                      if (!robotId || session?.user.role === "viewer") {
                        return;
                      }
                      commandMutation.mutate({ robotId, command, note: label });
                    }}
                  >
                    {label}
                  </Button>
                ))}
              </div>

              <div className="surface-panel rounded-[28px] border border-white/10 p-5">
                <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Battery and progress replay</div>
                <div className="mt-4 h-[240px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={history?.telemetry ?? []}>
                      <XAxis dataKey="recorded_at" tickFormatter={formatDateTime} stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip
                        contentStyle={{ background: "#020617", borderColor: "#1e293b", borderRadius: 16 }}
                        labelFormatter={(value) => formatDateTime(String(value))}
                      />
                      <Line type="monotone" dataKey="battery_level" stroke="#38bdf8" dot={false} strokeWidth={2.5} />
                      <Line type="monotone" dataKey="mission_progress_pct" stroke="#34d399" dot={false} strokeWidth={2.5} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="grid gap-3">
                <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Recent events</div>
                {history?.events.length ? (
                  history.events.slice(0, 8).map((event) => (
                    <div key={event.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                      <div className="flex items-center justify-between gap-3">
                        <div className="font-medium text-white">{event.event_type.replace(/_/g, " ")}</div>
                        <div className="text-xs text-muted-foreground">{formatRelative(event.occurred_at)}</div>
                      </div>
                      <div className="mt-2 text-sm text-muted-foreground">{event.message}</div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-muted-foreground">
                    No recent robot events were recorded.
                  </div>
                )}
              </div>
            </div>
          </>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function StatCard({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 text-lg text-white">{value}</div>
    </div>
  );
}
