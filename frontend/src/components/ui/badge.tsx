import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-border bg-secondary/70 px-2.5 py-1 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}
