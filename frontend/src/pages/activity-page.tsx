import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { useAuditQuery } from "@/hooks/use-signalops";
import { formatDateTime } from "@/lib/format";

export function ActivityPage() {
  const { data } = useAuditQuery();

  return (
    <>
      <PageHeader
        eyebrow="Audit trail"
        title="Operator and automation activity history across incidents and alerts."
        description="Every meaningful operational action is captured here to support traceability and post-incident review."
      />

      <Panel title="Recent activity" description="Newest actions first.">
        <div className="space-y-3">
          {data?.items.map((entry) => (
            <div key={entry.id} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="font-medium text-white">{entry.message}</div>
                  <div className="mt-1 text-sm text-muted-foreground">
                    {entry.actor_email ?? "signalops-automation"} · {entry.action}
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">{formatDateTime(entry.created_at)}</div>
              </div>
              <div className="mt-3 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                {entry.resource_type} / {entry.resource_id}
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}

