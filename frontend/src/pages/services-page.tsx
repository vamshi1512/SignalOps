import { CreateServiceDialog } from "@/components/services/create-service-dialog";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { useServicesQuery } from "@/hooks/use-signalops";

export function ServicesPage() {
  const { data } = useServicesQuery();

  return (
    <>
      <PageHeader
        eyebrow="Service registry"
        title="Catalog service ownership, environment posture, priority, and SLA targets."
        description="The registry anchors incident routing and reliability scoring across every monitored service."
        actions={<CreateServiceDialog />}
      />

      <Panel title="Registered services" description="Registry entries enriched with live health posture.">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data?.items.map((service) => (
            <div key={service.id} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="font-display text-xl text-white">{service.name}</div>
                  <div className="mt-1 text-sm text-muted-foreground">{service.owner}</div>
                </div>
                <StatusPill value={service.priority} />
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-300">{service.description}</p>
              <div className="mt-5 grid grid-cols-3 gap-3">
                <StatBlock label="Health" value={`${service.health_score.toFixed(0)}%`} />
                <StatBlock label="Incidents" value={`${service.open_incidents}`} />
                <StatBlock label="Alerts" value={`${service.open_alerts}`} />
              </div>
              <div className="mt-5 flex items-center justify-between">
                <StatusPill value={service.environment} />
                <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  SLA {service.sla_target.toFixed(2)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}

function StatBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-2 font-display text-2xl text-white">{value}</div>
    </div>
  );
}

