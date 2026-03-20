import { useState } from "react";

import { useAuth } from "@/auth/auth-provider";
import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useCommandRobotMutation, useCreateMissionMutation, useMissionsQuery, useRobotsQuery, useZonesQuery } from "@/hooks/use-roboyard";

const missionTypes = [
  { label: "Mow", value: "mow" },
  { label: "Inspect", value: "inspect" },
  { label: "Patrol", value: "patrol" },
  { label: "Haul", value: "haul" },
];

export function MissionsPage() {
  const { session } = useAuth();
  const robotsQuery = useRobotsQuery();
  const zonesQuery = useZonesQuery();
  const missionsQuery = useMissionsQuery();
  const createMission = useCreateMissionMutation();
  const commandMission = useCommandRobotMutation();

  const [robotId, setRobotId] = useState("");
  const [zoneId, setZoneId] = useState("");
  const [missionType, setMissionType] = useState("mow");
  const [missionName, setMissionName] = useState("Afternoon route");
  const [targetArea, setTargetArea] = useState("840");

  const defaultRobot = robotsQuery.data?.items[0];
  const activeRobotId = robotId || defaultRobot?.id || "";
  const activeZoneId = zoneId || defaultRobot?.zone.id || "";
  const canOperate = session?.user.role !== "viewer";

  return (
    <>
      <PageHeader
        eyebrow="Mission orchestration"
        title="Dispatch jobs, schedule windows, and control live mission execution."
        description="Create simulated autonomous runs and issue operator commands into the manual queue."
      />

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="surface-panel-elevated rounded-[32px] p-6">
          <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Create mission</div>
          <div className="mt-6 grid gap-4">
            <div>
              <label className="mb-2 block text-sm text-slate-300">Mission name</label>
              <Input value={missionName} onChange={(event) => setMissionName(event.target.value)} />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm text-slate-300">Robot</label>
                <Select
                  value={activeRobotId}
                  onValueChange={(value) => {
                    setRobotId(value);
                    const robot = robotsQuery.data?.items.find((item) => item.id === value);
                    if (robot) {
                      setZoneId(robot.zone.id);
                    }
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select robot" />
                  </SelectTrigger>
                  <SelectContent>
                    {robotsQuery.data?.items.map((robot) => (
                      <SelectItem key={robot.id} value={robot.id}>
                        {robot.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-300">Mission type</label>
                <Select value={missionType} onValueChange={setMissionType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {missionTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm text-slate-300">Zone</label>
                <Select value={activeZoneId} onValueChange={setZoneId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select zone" />
                  </SelectTrigger>
                  <SelectContent>
                    {zonesQuery.data?.items.map((zone) => (
                      <SelectItem key={zone.id} value={zone.id}>
                        {zone.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-300">Target area (sqm)</label>
                <Input value={targetArea} onChange={(event) => setTargetArea(event.target.value)} />
              </div>
            </div>

            <Button
              size="lg"
              disabled={!canOperate || !activeRobotId || !activeZoneId || createMission.isPending}
              onClick={() =>
                createMission.mutate({
                  robot_id: activeRobotId,
                  zone_id: activeZoneId,
                  name: missionName,
                  mission_type: missionType,
                  target_area_sqm: Number(targetArea),
                })
              }
            >
              {createMission.isPending ? "Creating mission..." : canOperate ? "Create mission" : "Viewer mode"}
            </Button>
          </div>
        </div>

        <div className="grid gap-4">
          {missionsQuery.isLoading ? <LoadingState title="Loading mission lanes" description="Current and scheduled robot missions are being assembled." /> : null}
          {missionsQuery.isError ? (
            <ErrorState
              title="Mission lane unavailable"
              description={missionsQuery.error instanceof Error ? missionsQuery.error.message : "The mission registry could not be loaded."}
              action={<RetryButton onRetry={() => void missionsQuery.refetch()} />}
            />
          ) : null}
          {!missionsQuery.isLoading && !missionsQuery.isError && (missionsQuery.data?.items.length ?? 0) === 0 ? (
            <EmptyState
              title="No missions scheduled"
              description="Create a mission from the control form to populate the live dispatch board."
            />
          ) : null}
          {missionsQuery.data?.items.map((mission) => (
            <div key={mission.id} className="surface-panel rounded-[32px] p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="font-display text-2xl text-white">{mission.name}</div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    {mission.robot.name} • {mission.zone.name}
                  </div>
                </div>
                <StatusPill value={mission.status} />
              </div>
              <div className="mt-5 h-2 rounded-full bg-white/5">
                <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${mission.progress_pct}%` }} />
              </div>
              <div className="mt-3 text-sm text-muted-foreground">
                {mission.progress_pct.toFixed(1)}% • {mission.completed_area_sqm.toFixed(0)} / {mission.target_area_sqm.toFixed(0)} sqm
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                {["pause", "resume", "return_to_base", "manual_override", "clear_override"].map((command) => (
                  <Button
                    key={command}
                    variant="outline"
                    size="sm"
                    disabled={!canOperate || commandMission.isPending}
                    onClick={() => commandMission.mutate({ robotId: mission.robot.id, command, note: `${command} from mission page` })}
                  >
                    {command.replace(/_/g, " ")}
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
