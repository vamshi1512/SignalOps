import type { ReactNode } from "react";

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
    <div className="flex flex-col gap-6 rounded-[32px] border border-white/10 bg-slate-950/65 p-6 shadow-panel lg:flex-row lg:items-end lg:justify-between">
      <div className="space-y-3">
        <Badge>{eyebrow}</Badge>
        <div>
          <h1 className="font-display text-3xl text-white lg:text-4xl">{title}</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground lg:text-base">{description}</p>
        </div>
      </div>
      {actions}
    </div>
  );
}

