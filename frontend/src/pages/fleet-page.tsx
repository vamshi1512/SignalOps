import { useDeferredValue, useState } from "react";
import { Search } from "lucide-react";

import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { RobotDrawer } from "@/components/fleet/robot-drawer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useRobotsQuery, useZonesQuery } from "@/hooks/use-roboyard";

export function FleetPage() {
  const [search, setSearch] = useState("");
  const [zoneId, setZoneId] = useState<string | undefined>();
  const [status, setStatus] = useState<string | undefined>();
  const [selectedRobotId, setSelectedRobotId] = useState<string | null>(null);
  const deferredSearch = useDeferredValue(search);
  const robotsQuery = useRobotsQuery({ search: deferredSearch, zone_id: zoneId, status });
  const zonesQuery = useZonesQuery();
  const robots = robotsQuery.data?.items ?? [];
  const statusFilters = [
    { label: "All", value: undefined },
    { label: "Operating", value: "operating" },
    { label: "Charging", value: "charging" },
    { label: "Paused", value: "paused" },
    { label: "Manual", value: "manual_override" },
  ];

  return (
    <>
      <PageHeader
        eyebrow="Fleet registry"
        title="Provisioned robots, firmware posture, and zone assignment."
        description="Search, inspect, and operate the seeded demo fleet across mowing, utility, and inspection classes."
      />

      <div className="flex flex-wrap gap-3 rounded-[28px] border border-white/10 bg-white/[0.04] p-4">
        <div className="relative min-w-[280px] flex-1">
          <Search className="pointer-events-none absolute left-4 top-3.5 h-4 w-4 text-muted-foreground" />
          <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search robots, serials, or models" className="pl-11" />
        </div>
        <Button variant={zoneId ? "outline" : "default"} size="sm" onClick={() => setZoneId(undefined)}>
          All zones
        </Button>
        {zonesQuery.data?.items.map((zone) => (
          <Button key={zone.id} variant={zoneId === zone.id ? "default" : "outline"} size="sm" onClick={() => setZoneId(zone.id)}>
            {zone.name}
          </Button>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {statusFilters.map((filter) => (
          <Button key={filter.label} variant={status === filter.value ? "default" : "outline"} size="sm" onClick={() => setStatus(filter.value)}>
            {filter.label}
          </Button>
        ))}
      </div>

      {robotsQuery.isLoading ? <LoadingState title="Loading fleet registry" description="Provisioned robots, firmware posture, and live zone assignment are being synchronized." /> : null}
      {robotsQuery.isError ? (
        <ErrorState
          title="Fleet registry unavailable"
          description={robotsQuery.error instanceof Error ? robotsQuery.error.message : "The fleet registry could not be loaded."}
          action={<RetryButton onRetry={() => void robotsQuery.refetch()} />}
        />
      ) : null}
      {!robotsQuery.isLoading && !robotsQuery.isError && robots.length === 0 ? (
        <EmptyState
          title="No robots match the current filters"
          description="Adjust the search, zone, or status filters to inspect a different part of the fleet."
          action={<RetryButton onRetry={() => {
            setSearch("");
            setZoneId(undefined);
            setStatus(undefined);
          }}>Clear filters</RetryButton>}
        />
      ) : null}

      {robots.length > 0 ? (
        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
          {robots.map((robot) => (
            <button
              key={robot.id}
              type="button"
              onClick={() => setSelectedRobotId(robot.id)}
              className="surface-panel-elevated rounded-[32px] p-6 text-left transition hover:-translate-y-1"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="font-display text-2xl text-white">{robot.name}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{robot.model}</div>
                </div>
                <StatusPill value={robot.status} />
              </div>
              <div className="mt-6 grid grid-cols-2 gap-3">
                <FleetStat label="Battery" value={`${robot.battery_level.toFixed(0)}%`} />
                <FleetStat label="Zone" value={robot.zone.name} />
                <FleetStat label="Connectivity" value={robot.connectivity_state.replace("_", " ")} />
                <FleetStat label="Firmware" value={robot.firmware_version} />
              </div>
              <div className="mt-4 h-2 rounded-full bg-white/5">
                <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${robot.health_score}%` }} />
              </div>
              <div className="mt-2 text-xs uppercase tracking-[0.16em] text-muted-foreground">Health score {robot.health_score.toFixed(0)}%</div>
              <div className="mt-5 text-sm text-slate-300">{robot.status_reason}</div>
            </button>
          ))}
        </div>
      ) : null}

      <RobotDrawer robotId={selectedRobotId} open={Boolean(selectedRobotId)} onOpenChange={(next) => !next && setSelectedRobotId(null)} />
    </>
  );
}

function FleetStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 text-white">{value}</div>
    </div>
  );
}
