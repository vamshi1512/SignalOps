import { ArrowDownRight, ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDelta, formatMetric } from "@/lib/format";
import type { MetricCard as MetricCardType } from "@/types/api";

export function MetricCard({ metric }: { metric: MetricCardType }) {
  const positive = metric.delta >= 0;
  const TrendIcon = positive ? ArrowUpRight : ArrowDownRight;

  return (
    <Card className="metric-glow border-white/10">
      <CardContent className="space-y-4 p-5">
        <div className="flex items-center justify-between">
          <Badge>{metric.label}</Badge>
          <span className="rounded-full border border-white/10 bg-white/5 p-2">
            <TrendIcon className={`h-4 w-4 ${positive ? "text-emerald-300" : "text-red-300"}`} />
          </span>
        </div>
        <div className="space-y-1">
          <div className="font-display text-3xl text-white">{formatMetric(metric.value, metric.suffix)}</div>
          <div className={`text-sm ${positive ? "text-emerald-300" : "text-red-300"}`}>
            {formatDelta(metric.delta, metric.suffix)} vs baseline
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

