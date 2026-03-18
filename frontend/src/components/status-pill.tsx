import { cn } from "@/lib/utils";

const colorMap: Record<string, string> = {
  critical: "border-red-500/30 bg-red-500/10 text-red-300",
  error: "border-orange-500/30 bg-orange-500/10 text-orange-300",
  warning: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  info: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  open: "border-cyan-500/30 bg-cyan-500/10 text-cyan-300",
  investigating: "border-indigo-500/30 bg-indigo-500/10 text-indigo-300",
  acknowledged: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  resolved: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  escalated: "border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-300",
  suppressed: "border-yellow-500/30 bg-yellow-500/10 text-yellow-300",
  production: "border-red-500/30 bg-red-500/10 text-red-300",
  staging: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  development: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  p0: "border-red-500/30 bg-red-500/10 text-red-300",
  p1: "border-orange-500/30 bg-orange-500/10 text-orange-300",
  p2: "border-cyan-500/30 bg-cyan-500/10 text-cyan-300",
  p3: "border-slate-500/30 bg-slate-500/10 text-slate-300",
};

export function StatusPill({ value }: { value: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2.5 py-1 text-xs font-medium uppercase tracking-[0.18em]",
        colorMap[value] ?? "border-white/10 bg-white/5 text-muted-foreground",
      )}
    >
      {value.replace(/_/g, " ")}
    </span>
  );
}

