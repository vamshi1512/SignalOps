import { cn } from "@/lib/utils";

const colorMap: Record<string, string> = {
  healthy: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  degraded: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  offline: "border-red-500/30 bg-red-500/10 text-red-300",
  qa: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  staging: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  prod_like: "border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-300",
  mock: "border-teal-500/30 bg-teal-500/10 text-teal-300",
  active: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  draft: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  paused: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  queued: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  running: "border-cyan-500/30 bg-cyan-500/10 text-cyan-300",
  passed: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  failed: "border-red-500/30 bg-red-500/10 text-red-300",
  partial: "border-orange-500/30 bg-orange-500/10 text-orange-300",
  flaky: "border-yellow-500/30 bg-yellow-500/10 text-yellow-300",
  skipped: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  api: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  ui: "border-violet-500/30 bg-violet-500/10 text-violet-300",
  manual: "border-cyan-500/30 bg-cyan-500/10 text-cyan-300",
  scheduled: "border-orange-500/30 bg-orange-500/10 text-orange-300",
  demo: "border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-300",
  admin: "border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-300",
  qa_engineer: "border-cyan-500/30 bg-cyan-500/10 text-cyan-300",
  viewer: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  slack: "border-violet-500/30 bg-violet-500/10 text-violet-300",
  email: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  webhook: "border-teal-500/30 bg-teal-500/10 text-teal-300",
  sent: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  pending: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  skipped_state: "border-slate-500/30 bg-slate-500/10 text-slate-300",
};

export function StatusPill({ value }: { value: string }) {
  const normalized = value === "skipped" ? "skipped" : value;
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2.5 py-1 text-xs font-medium uppercase tracking-[0.18em]",
        colorMap[normalized] ?? "border-border bg-secondary/60 text-muted-foreground",
      )}
    >
      {value.replace(/_/g, " ")}
    </span>
  );
}
