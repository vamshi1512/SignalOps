import { ArrowDownRight, ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDelta, formatMetric } from "@/lib/format";
import type { MetricCard as MetricCardType } from "@/types/api";

export function MetricCard({ metric }: { metric: MetricCardType }) {
  const positive = metric.delta >= 0;
  const TrendIcon = positive ? ArrowUpRight : ArrowDownRight;

  return (
    <Card className="metric-glow border-border/60">
      <CardContent className="space-y-4 p-5">
        <div className="flex items-center justify-between">
          <Badge className="bg-background/45">{metric.label}</Badge>
          <span className="rounded-full border border-border/70 bg-background/55 p-2 shadow-inner">
            <TrendIcon className={`h-4 w-4 ${positive ? "text-emerald-400" : "text-red-400"}`} />
          </span>
        </div>
        <div className="space-y-1">
          <div className="font-display text-3xl text-foreground">{formatMetric(metric.value, metric.suffix)}</div>
          <div className={`text-sm ${positive ? "text-emerald-400" : "text-red-400"}`}>
            {formatDelta(metric.delta, metric.suffix)} vs baseline
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
