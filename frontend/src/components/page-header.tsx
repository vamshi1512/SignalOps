import type { ReactNode } from "react";
import { Activity } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
}) {
  return (
    <div className="surface-panel control-shell flex flex-col gap-6 rounded-[36px] p-6 lg:flex-row lg:items-end lg:justify-between">
      <div className="space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <Badge>{eyebrow}</Badge>
          <span className="status-chip">
            <Activity className="h-3.5 w-3.5 text-cyan-200" />
            Live console
          </span>
        </div>
        <div>
          <h1 className="font-display text-3xl text-white lg:text-4xl">{title}</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground lg:text-base">{description}</p>
        </div>
      </div>
      {actions}
    </div>
  );
}
