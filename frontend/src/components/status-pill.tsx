import { cn } from "@/lib/utils";

const colorMap: Record<string, string> = {
  operating: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  charging: "border-sky-400/30 bg-sky-400/10 text-sky-200",
  paused: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  returning_home: "border-violet-400/30 bg-violet-400/10 text-violet-200",
  fault: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  manual_override: "border-orange-400/30 bg-orange-400/10 text-orange-200",
  weather_paused: "border-blue-400/30 bg-blue-400/10 text-blue-200",
  idle: "border-slate-400/30 bg-slate-400/10 text-slate-300",
  online: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  degraded: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  offline: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  active: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  scheduled: "border-sky-400/30 bg-sky-400/10 text-sky-200",
  completed: "border-slate-400/30 bg-slate-400/10 text-slate-300",
  aborted: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  open: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  acknowledged: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  resolved: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  critical: "border-rose-400/30 bg-rose-400/10 text-rose-200",
  warning: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  info: "border-sky-400/30 bg-sky-400/10 text-sky-200",
  clear: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
  drizzle: "border-sky-400/30 bg-sky-400/10 text-sky-200",
  rain: "border-blue-400/30 bg-blue-400/10 text-blue-200",
  wind_gust: "border-indigo-400/30 bg-indigo-400/10 text-indigo-200",
  storm: "border-violet-400/30 bg-violet-400/10 text-violet-200",
};

export function StatusPill({ value, className }: { value: string; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium uppercase tracking-[0.18em]",
        colorMap[value] ?? "border-white/10 bg-white/5 text-muted-foreground",
        className,
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" />
      {value.replace(/_/g, " ")}
    </span>
  );
}
