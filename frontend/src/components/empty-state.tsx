import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
  compact = false,
  tone = "default",
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
  compact?: boolean;
  tone?: "default" | "error";
}) {
  const accentClasses =
    tone === "error"
      ? "border-red-500/20 bg-red-500/[0.08] text-red-300"
      : "border-primary/20 bg-primary/[0.08] text-primary";

  return (
    <div
      className={cn(
        "rounded-[28px] border border-dashed border-border/80 bg-background/30 text-center shadow-panel",
        compact ? "p-6" : "p-8",
        className,
      )}
    >
      <div className={cn("mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border", accentClasses)}>
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="font-display text-xl text-foreground">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">{description}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </div>
  );
}
