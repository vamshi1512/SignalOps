import { useMemo, useState } from "react";

import { CreateRuleDialog } from "@/components/alerts/create-rule-dialog";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAcknowledgeAlertMutation, useAlertsQuery, useRulesQuery, useSuppressAlertMutation } from "@/hooks/use-signalops";
import { formatDateTime } from "@/lib/format";
import type { AlertStatus } from "@/types/api";

const statuses: Array<AlertStatus | "all"> = ["all", "open", "acknowledged", "suppressed", "escalated", "resolved"];

export function AlertsPage() {
  const [status, setStatus] = useState<AlertStatus | "all">("all");
  const params = useMemo(() => {
    const next = new URLSearchParams();
    if (status !== "all") next.set("status", status);
    return next;
  }, [status]);

  const { data: alerts } = useAlertsQuery(params);
  const { data: rules } = useRulesQuery();
  const acknowledge = useAcknowledgeAlertMutation();
  const suppress = useSuppressAlertMutation();

  return (
    <>
      <PageHeader
        eyebrow="Alerting"
        title="Threshold rules, acknowledgement flows, and escalation simulation."
        description="Shape service alerts, suppress noisy signals, and acknowledge actionable breaches while preserving a full audit trail."
        actions={<CreateRuleDialog />}
      />

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <Panel
          title="Alert stream"
          description="Current rule breaches across services."
          action={
            <Select value={status} onValueChange={(value) => setStatus(value as AlertStatus | "all")}>
              <SelectTrigger className="w-[190px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {statuses.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          }
        >
          <div className="space-y-3">
            {alerts?.items.map((alert) => (
              <div key={alert.id} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="font-medium text-white">{alert.message}</div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <StatusPill value={alert.status} />
                      <StatusPill value={alert.rule.severity} />
                      <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                        {alert.service.name}
                      </span>
                    </div>
                  </div>
                  <div className="text-sm text-muted-foreground">{formatDateTime(alert.triggered_at)}</div>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  <MetricCell label="Current" value={alert.current_value.toFixed(1)} />
                  <MetricCell label="Threshold" value={alert.threshold.toFixed(1)} />
                  <MetricCell label="Escalation" value={`L${alert.escalation_level}`} />
                </div>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Button
                    variant="secondary"
                    size="sm"
                    disabled={acknowledge.isPending || alert.status === "acknowledged"}
                    onClick={() => acknowledge.mutate(alert.id)}
                  >
                    Acknowledge
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={suppress.isPending}
                    onClick={() => suppress.mutate({ alertId: alert.id, minutes: 30 })}
                  >
                    Suppress 30m
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Alert rules" description="Seeded and custom policies driving the platform.">
          <div className="space-y-3">
            {rules?.items.map((rule) => (
              <div key={rule.id} className="rounded-[24px] border border-white/10 bg-white/[0.04] p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium text-white">{rule.name}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{rule.service?.name ?? "Global scope"}</div>
                  </div>
                  <StatusPill value={rule.severity} />
                </div>
                <div className="mt-3 grid grid-cols-2 gap-3 text-sm text-slate-300">
                  <div>Metric: {rule.metric}</div>
                  <div>Threshold: {rule.threshold}</div>
                  <div>Window: {rule.window_minutes}m</div>
                  <div>Escalate: {rule.escalate_after_minutes}m</div>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}

function MetricCell({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 font-display text-2xl text-white">{value}</div>
    </div>
  );
}

