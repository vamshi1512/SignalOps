import { useState } from "react";

import { useAuth } from "@/auth/auth-provider";
import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusPill } from "@/components/status-pill";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAlertsQuery, useAcknowledgeAlertMutation } from "@/hooks/use-roboyard";
import { formatDateTime, formatRelative } from "@/lib/format";
import type { Alert } from "@/types/api";

export function AlertsPage() {
  const { session } = useAuth();
  const alertsQuery = useAlertsQuery();
  const acknowledge = useAcknowledgeAlertMutation();
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [notes, setNotes] = useState("Acknowledged from alert center");
  const canAcknowledge = session?.user.role !== "viewer";

  return (
    <>
      <PageHeader
        eyebrow="Incidents and alerts"
        title="Safety alerts, degraded telemetry, and operator acknowledgment flow."
        description="Review current incidents, triage them by severity, and record acknowledgment notes."
      />

      {alertsQuery.isLoading ? <LoadingState title="Loading alert center" description="Incidents, degraded telemetry, and safety holds are being synchronized." /> : null}
      {alertsQuery.isError ? (
        <ErrorState
          title="Alert center unavailable"
          description={alertsQuery.error instanceof Error ? alertsQuery.error.message : "Current alerts could not be loaded."}
          action={<RetryButton onRetry={() => void alertsQuery.refetch()} />}
        />
      ) : null}
      {!alertsQuery.isLoading && !alertsQuery.isError && (alertsQuery.data?.items.length ?? 0) === 0 ? (
        <EmptyState title="No alerts in the queue" description="The fleet is currently operating without active or historical incident records." />
      ) : null}

      <div className="grid gap-4 xl:grid-cols-2">
        {alertsQuery.data?.items.map((alert) => (
          <button
            key={alert.id}
            type="button"
            onClick={() => {
              setSelectedAlert(alert);
              setNotes(alert.notes || "Acknowledged from alert center");
            }}
            className="surface-panel rounded-[32px] p-6 text-left transition hover:-translate-y-1"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-display text-2xl text-white">{alert.title}</div>
                <div className="mt-1 text-sm text-muted-foreground">{alert.robot.name}</div>
              </div>
              <div className="flex gap-2">
                <StatusPill value={alert.severity} />
                <StatusPill value={alert.status} />
              </div>
            </div>
            <div className="mt-4 text-sm text-slate-300">{alert.message}</div>
            <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
              <span>{formatRelative(alert.occurred_at)}</span>
              <span>{formatDateTime(alert.occurred_at)}</span>
            </div>
          </button>
        ))}
      </div>

      <Dialog open={Boolean(selectedAlert)} onOpenChange={(next) => !next && setSelectedAlert(null)}>
        <DialogContent>
          {selectedAlert ? (
            <>
              <DialogHeader>
                <DialogTitle>{selectedAlert.title}</DialogTitle>
                <DialogDescription>{selectedAlert.robot.name} • {selectedAlert.type.replace(/_/g, " ")}</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 p-6">
                <div className="flex gap-2">
                  <StatusPill value={selectedAlert.severity} />
                  <StatusPill value={selectedAlert.status} />
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-300">
                  {selectedAlert.message}
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-300">
                  Occurred {formatDateTime(selectedAlert.occurred_at)} • Last state {formatRelative(selectedAlert.occurred_at)}
                </div>
                {Object.keys(selectedAlert.metadata).length ? (
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedAlert.metadata).map(([key, value]) => (
                      <div key={key} className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs uppercase tracking-[0.16em] text-slate-300">
                        {key}: {String(value)}
                      </div>
                    ))}
                  </div>
                ) : null}
                <div>
                  <label className="mb-2 block text-sm text-slate-300">Acknowledgment note</label>
                  <Textarea value={notes} onChange={(event) => setNotes(event.target.value)} disabled={!canAcknowledge || selectedAlert.status !== "open"} />
                </div>
                <Button
                  disabled={!canAcknowledge || selectedAlert.status !== "open" || acknowledge.isPending}
                  onClick={() =>
                    acknowledge.mutate(
                      { alertId: selectedAlert.id, notes },
                      {
                        onSuccess: (alert) => setSelectedAlert(alert),
                      },
                    )
                  }
                >
                  {acknowledge.isPending ? "Acknowledging..." : "Acknowledge alert"}
                </Button>
              </div>
            </>
          ) : null}
        </DialogContent>
      </Dialog>
    </>
  );
}
