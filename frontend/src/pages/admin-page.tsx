import { useState } from "react";

import { ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuditQuery, useConfigQuery, useUpdateConfigMutation, useUsersQuery } from "@/hooks/use-roboyard";
import { formatDateTime } from "@/lib/format";

export function AdminPage() {
  const configQuery = useConfigQuery();
  const usersQuery = useUsersQuery();
  const auditQuery = useAuditQuery();
  const updateConfig = useUpdateConfigMutation();
  const [lowBatteryThreshold, setLowBatteryThreshold] = useState<string | null>(null);

  const config = configQuery.data;

  return (
    <>
      <PageHeader
        eyebrow="Administration"
        title="Policy thresholds, role management, and operations audit."
        description="Review control-plane settings and the operator activity trail across the demo environment."
      />

      {(configQuery.isLoading || usersQuery.isLoading || auditQuery.isLoading) ? (
        <LoadingState title="Loading admin surfaces" description="Control-plane settings, user roles, and audit telemetry are being assembled." />
      ) : null}
      {configQuery.isError || usersQuery.isError || auditQuery.isError ? (
        <ErrorState
          title="Administration surface unavailable"
          description={
            configQuery.error instanceof Error
              ? configQuery.error.message
              : usersQuery.error instanceof Error
                ? usersQuery.error.message
                : auditQuery.error instanceof Error
                  ? auditQuery.error.message
                  : "One or more admin data sources failed to load."
          }
          action={
            <RetryButton
              onRetry={() => {
                void configQuery.refetch();
                void usersQuery.refetch();
                void auditQuery.refetch();
              }}
            />
          }
        />
      ) : null}

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="grid gap-4">
          <div className="surface-panel rounded-[32px] p-6">
            <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Simulator policy</div>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <ConfigStat label="Weather enabled" value={config?.weather_enabled ? "yes" : "no"} />
              <ConfigStat label="Deterministic mode" value={config?.deterministic_mode ? "yes" : "no"} />
              <ConfigStat label="Current weather" value={config?.current_weather ?? "clear"} />
              <ConfigStat label="Collision threshold" value={config ? config.collision_threshold.toFixed(2) : "--"} />
            </div>
            <div className="mt-6 grid gap-3">
              <label className="text-sm text-slate-300">Low battery threshold</label>
              <Input
                value={lowBatteryThreshold ?? String(config?.low_battery_threshold ?? "")}
                onChange={(event) => setLowBatteryThreshold(event.target.value)}
                disabled={updateConfig.isPending}
              />
              <Button
                disabled={updateConfig.isPending}
                onClick={() =>
                  updateConfig.mutate({
                    low_battery_threshold: Number(lowBatteryThreshold ?? config?.low_battery_threshold ?? 24),
                  })
                }
              >
                {updateConfig.isPending ? "Saving threshold..." : "Save threshold"}
              </Button>
            </div>
          </div>

          <div className="surface-panel rounded-[32px] p-6">
            <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Users and roles</div>
            <div className="mt-4 grid gap-3">
              {usersQuery.data?.items.map((user) => (
                <div key={user.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-medium text-white">{user.full_name}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                    </div>
                    <div className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                      {user.role}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="surface-panel rounded-[32px] p-6">
          <div className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Audit log</div>
          <div className="mt-4 grid gap-3">
            {auditQuery.data?.items.map((entry) => (
              <div key={entry.id} className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium text-white">{entry.action}</div>
                    <div className="mt-1 text-sm text-muted-foreground">{entry.message}</div>
                  </div>
                  <div className="text-xs text-muted-foreground">{formatDateTime(entry.created_at)}</div>
                </div>
                <div className="mt-3 text-xs uppercase tracking-[0.16em] text-slate-400">
                  {entry.actor_email ?? "system"} • {entry.resource_type} • {entry.resource_id}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

function ConfigStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 text-lg text-white">{value}</div>
    </div>
  );
}
