import { motion } from "framer-motion";

import { StatusPill } from "@/components/status-pill";
import { cn } from "@/lib/utils";
import type { Alert, Mission, RobotDetail, Zone } from "@/types/api";

interface YardMapProps {
  zones: Zone[];
  robots: RobotDetail[];
  missions: Mission[];
  alerts: Alert[];
  selectedRobotId?: string | null;
  onSelectRobot?: (robotId: string) => void;
}

function pointString(points: Array<{ x: number; y: number }>) {
  return points.map((point) => `${point.x},${point.y}`).join(" ");
}

export function YardMap({ zones, robots, missions, alerts, selectedRobotId, onSelectRobot }: YardMapProps) {
  return (
    <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/80">
      <div className="absolute inset-x-0 top-0 z-10 flex items-center justify-between border-b border-white/10 bg-slate-950/85 px-5 py-4 backdrop-blur">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Operational map</div>
          <div className="mt-1 font-display text-xl text-white">Fleet geofence, routing, and live robot position</div>
        </div>
        <StatusPill value="online" />
      </div>

      <svg viewBox="0 0 820 480" className="h-[520px] w-full">
        <rect x={0} y={0} width={820} height={480} fill="rgba(3,7,18,0.9)" />
        <g opacity={0.15}>
          {Array.from({ length: 18 }).map((_, index) => (
            <line key={`v-${index}`} x1={index * 48} y1={0} x2={index * 48} y2={480} stroke="#94a3b8" strokeWidth={1} />
          ))}
          {Array.from({ length: 12 }).map((_, index) => (
            <line key={`h-${index}`} x1={0} y1={index * 40} x2={820} y2={index * 40} stroke="#94a3b8" strokeWidth={1} />
          ))}
        </g>

        {zones.map((zone) => (
          <g key={zone.id}>
            <polygon
              points={pointString(zone.boundary)}
              fill={`${zone.color}16`}
              stroke={zone.color}
              strokeWidth={2}
              strokeDasharray="10 8"
            />
            {zone.task_areas.map((area, index) => {
              const x = Number(area.x ?? 0);
              const y = Number(area.y ?? 0);
              const width = Number(area.width ?? 0);
              const height = Number(area.height ?? 0);
              return (
                <rect
                  key={`${zone.id}-task-${index}`}
                  x={x}
                  y={y}
                  width={width}
                  height={height}
                  rx={18}
                  fill={`${zone.color}14`}
                  stroke={`${zone.color}55`}
                />
              );
            })}
            <g transform={`translate(${zone.charging_station.x} ${zone.charging_station.y})`}>
              <circle r={18} fill="rgba(8,145,178,0.2)" stroke="#38bdf8" strokeWidth={2} />
              <circle r={6} fill="#38bdf8" />
            </g>
            <text x={zone.boundary[0].x + 12} y={zone.boundary[0].y + 26} fill="#e2e8f0" fontSize={16} fontWeight={700}>
              {zone.name}
            </text>
          </g>
        ))}

        {missions.map((mission) => (
          <polyline
            key={mission.id}
            points={pointString(mission.route_points)}
            fill="none"
            stroke="rgba(148,163,184,0.42)"
            strokeWidth={2}
            strokeDasharray="5 7"
          />
        ))}

        {alerts.map((alert) => {
          const robot = robots.find((item) => item.id === alert.robot.id);
          if (!robot) {
            return null;
          }
          return (
            <g key={alert.id} transform={`translate(${robot.position_x} ${robot.position_y})`}>
              <circle r={18} fill="rgba(251,113,133,0.08)" stroke="rgba(251,113,133,0.4)" strokeWidth={1.5} />
              <path d="M -6 -6 L 6 6 M 6 -6 L -6 6" stroke="#fb7185" strokeWidth={2} />
            </g>
          );
        })}

        {robots.map((robot, index) => (
          <g
            key={robot.id}
            className="cursor-pointer"
            onClick={() => onSelectRobot?.(robot.id)}
            transform={`translate(${robot.position_x} ${robot.position_y})`}
          >
            <motion.circle
              r={selectedRobotId === robot.id ? 28 : 20}
              fill={selectedRobotId === robot.id ? "rgba(34,197,94,0.12)" : "rgba(15,23,42,0.9)"}
              stroke={selectedRobotId === robot.id ? "#34d399" : "#94a3b8"}
              strokeWidth={selectedRobotId === robot.id ? 3 : 2}
              initial={{ scale: 0.9, opacity: 0.8 }}
              animate={{ scale: [1, 1.06, 1], opacity: 1 }}
              transition={{ duration: 2.4, repeat: Number.POSITIVE_INFINITY, delay: index * 0.15 }}
            />
            <circle r={8} fill={robot.status === "operating" ? "#34d399" : robot.status === "charging" ? "#38bdf8" : "#f59e0b"} />
            <path
              d={`M 0 0 L ${Math.cos((robot.heading_deg * Math.PI) / 180) * 18} ${Math.sin((robot.heading_deg * Math.PI) / 180) * 18}`}
              stroke="#e2e8f0"
              strokeWidth={2}
              strokeLinecap="round"
            />
            <text x={24} y={-12} fill="#f8fafc" fontSize={13} fontWeight={600}>
              {robot.name}
            </text>
            <text x={24} y={6} fill="#94a3b8" fontSize={11}>
              {robot.battery_level.toFixed(0)}% battery
            </text>
          </g>
        ))}
      </svg>

      <div className="grid gap-2 border-t border-white/10 bg-slate-950/85 px-5 py-4 md:grid-cols-3">
        {robots.slice(0, 3).map((robot) => (
          <button
            key={robot.id}
            type="button"
            onClick={() => onSelectRobot?.(robot.id)}
            className={cn(
              "rounded-2xl border border-white/10 bg-white/[0.04] p-3 text-left transition hover:bg-white/[0.08]",
              selectedRobotId === robot.id && "border-cyan-400/30 bg-cyan-400/10",
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="font-medium text-white">{robot.name}</div>
              <StatusPill value={robot.status} className="text-[10px]" />
            </div>
            <div className="mt-2 text-sm text-muted-foreground">{robot.status_reason}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
