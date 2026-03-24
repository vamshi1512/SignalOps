import type { ReactNode } from "react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  meta,
}: {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
  meta?: Array<{ label: string; value: string }>;
}) {
  return (
    <div className="overflow-hidden rounded-[34px] border border-border/70 bg-card/85 shadow-panel backdrop-blur-xl">
      <div className="relative">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-28 bg-gradient-to-r from-primary/10 via-transparent to-accent/10" />
        <div className="relative flex flex-col gap-6 p-6 lg:flex-row lg:items-end lg:justify-between lg:p-7">
          <div className="space-y-3">
            <Badge className="border-primary/20 bg-primary/[0.08] text-primary">{eyebrow}</Badge>
            <div>
              <h1 className="font-display text-3xl text-foreground lg:text-4xl">{title}</h1>
              <p className="mt-2 max-w-2xl text-sm text-muted-foreground lg:text-base">{description}</p>
            </div>
          </div>
          {actions}
        </div>
      </div>
      {meta?.length ? (
        <div className="grid gap-px border-t border-border/70 bg-border/50 md:grid-cols-3">
          {meta.map((item, index) => (
            <div
              key={`${item.label}-${item.value}`}
              className={cn("bg-card/95 px-6 py-4", meta.length > 3 && index >= 3 ? "md:border-t border-border/70" : "")}
            >
              <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">{item.label}</div>
              <div className="mt-2 font-display text-2xl text-foreground">{item.value}</div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
