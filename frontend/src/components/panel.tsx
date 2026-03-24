import type { PropsWithChildren, ReactNode } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface PanelProps extends PropsWithChildren {
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
  eyebrow?: string;
}

export function Panel({ title, description, action, className, eyebrow, children }: PanelProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          {eyebrow ? <div className="mb-2 text-[11px] uppercase tracking-[0.2em] text-muted-foreground">{eyebrow}</div> : null}
          <CardTitle>{title}</CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </div>
        {action}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
