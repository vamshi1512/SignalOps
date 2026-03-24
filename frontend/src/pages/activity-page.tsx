import { AlertTriangle, BellRing, Clock3, RefreshCcw, Users2 } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAuditQuery,
  useNotificationsQuery,
  useUsersQuery,
} from "@/hooks/use-testforge";
import { getErrorMessage } from "@/lib/api";
import { formatDateTime, formatRelative } from "@/lib/format";

export function ActivityPage() {
  const { data: notifications, error: notificationsError, isLoading: notificationsLoading, refetch: refetchNotifications } = useNotificationsQuery();
  const { data: audit, error: auditError, isLoading: auditLoading, refetch: refetchAudit } = useAuditQuery();
  const { data: users, error: usersError, isLoading: usersLoading, refetch: refetchUsers } = useUsersQuery();

  if (notificationsLoading || auditLoading || usersLoading) {
    return (
      <div className="grid gap-4">
        <Skeleton className="h-48" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  const queryError = notificationsError ?? auditError ?? usersError;
  if (queryError || !notifications || !audit || !users) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Activity data is unavailable"
        description={getErrorMessage(queryError, "Activity feeds could not be loaded from the backend.")}
        tone="error"
        action={
          <Button
            variant="outline"
            onClick={() => {
              void refetchNotifications();
              void refetchAudit();
              void refetchUsers();
            }}
          >
            <RefreshCcw className="h-4 w-4" />
            Retry load
          </Button>
        }
      />
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Governance and alerts"
        title="Audit trail, notification simulation, and team visibility."
        description="Review which runs emitted alerts, how the system recorded lifecycle changes, and which seeded users represent platform personas."
        meta={[
          { label: "Notifications", value: `${notifications.items.length}` },
          { label: "Audit entries", value: `${audit.items.length}` },
          { label: "Seeded users", value: `${users.items.length}` },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <Panel title="Notifications" description="Simulated Slack and email delivery on failed runs.">
          {notifications.items.length ? (
            <div className="space-y-3">
              {notifications.items.map((notification) => (
                <div key={notification.id} className="rounded-[24px] border border-border bg-background/25 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="font-medium text-foreground">{notification.subject}</div>
                      <div className="mt-1 text-sm text-muted-foreground">{notification.recipient}</div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <StatusPill value={notification.channel} />
                      <StatusPill value={notification.status} />
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">{notification.message}</p>
                  <div className="mt-3 text-xs uppercase tracking-[0.18em] text-muted-foreground">
                    {formatRelative(notification.created_at)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={BellRing} title="No simulated notifications yet" description="Failed runs will emit seeded Slack and email records into this feed." compact />
          )}
        </Panel>

        <Panel title="Audit trail" description="System and operator actions recorded by the backend services.">
          {audit.items.length ? (
            <div className="space-y-3">
              {audit.items.map((entry) => (
                <div key={entry.id} className="rounded-[24px] border border-border bg-background/25 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-medium text-foreground">{entry.message}</div>
                      <div className="mt-1 text-sm text-muted-foreground">
                        {entry.actor_email ?? "system"} · {entry.resource_type}
                      </div>
                    </div>
                    <Clock3 className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="mt-3 text-sm text-muted-foreground">{formatDateTime(entry.created_at)}</div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={Clock3} title="No audit events recorded" description="Audit events will populate here as suites, schedules, and runs mutate platform state." compact />
          )}
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[0.7fr_1.3fr]">
        <Panel title="Seeded users" description="Demo personas for admin, QA lead, and read-only access.">
          {users.items.length ? (
            <div className="space-y-3">
              {users.items.map((user) => (
                <div key={user.id} className="rounded-[24px] border border-border bg-background/25 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="font-medium text-foreground">{user.full_name}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                    </div>
                    <StatusPill value={user.role} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState icon={Users2} title="No users available" description="Seeded personas will appear here after the backend startup seed completes." compact />
          )}
        </Panel>

        <Panel title="Demo target references" description="Useful entry points when presenting the platform or browsing the mock app manually.">
          <div className="grid gap-4 md:grid-cols-3">
            <ReferenceCard icon={BellRing} title="Checkout target" value="/api/v1/target-ui/checkout" />
            <ReferenceCard icon={BellRing} title="Admin target" value="/api/v1/target-ui/admin" />
            <ReferenceCard icon={Users2} title="API base" value="/api/v1/target-api" />
          </div>
        </Panel>
      </div>
    </>
  );
}

function ReferenceCard({
  icon: Icon,
  title,
  value,
}: {
  icon: typeof BellRing;
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-[24px] border border-border bg-background/25 p-5">
      <div className="mb-3 inline-flex rounded-2xl border border-border bg-secondary/70 p-3">
        <Icon className="h-5 w-5 text-primary" />
      </div>
      <div className="font-display text-lg text-foreground">{title}</div>
      <div className="mt-2 break-all font-mono text-sm text-muted-foreground">{value}</div>
    </div>
  );
}
