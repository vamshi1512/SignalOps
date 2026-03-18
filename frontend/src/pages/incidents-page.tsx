import { useMemo, useState } from "react";

import { IncidentDrawer } from "@/components/incidents/incident-drawer";
import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useIncidentsQuery, useServicesQuery } from "@/hooks/use-signalops";
import { formatDateTime, formatRelative } from "@/lib/format";
import type { IncidentStatus, SeverityLevel } from "@/types/api";

const severityOptions: Array<SeverityLevel | "all"> = ["all", "warning", "error", "critical"];
const statusOptions: Array<IncidentStatus | "all"> = ["all", "open", "acknowledged", "investigating", "resolved"];

export function IncidentsPage() {
  const [serviceId, setServiceId] = useState("all");
  const [severity, setSeverity] = useState<SeverityLevel | "all">("all");
  const [status, setStatus] = useState<IncidentStatus | "all">("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { data: services } = useServicesQuery();

  const params = useMemo(() => {
    const next = new URLSearchParams();
    if (serviceId !== "all") next.set("service_id", serviceId);
    if (severity !== "all") next.set("severity", severity);
    if (status !== "all") next.set("status", status);
    return next;
  }, [serviceId, severity, status]);

  const { data } = useIncidentsQuery(params);

  return (
    <>
      <PageHeader
        eyebrow="Incident management"
        title="Group repeated failures into actionable incidents with ownership and timeline context."
        description="Track open incidents, change severity, assign responders, add notes, and resolve issues without leaving the console."
      />

      <Panel
        title="Incident queue"
        description="Filter by service, severity, or lifecycle status."
        action={
          <div className="grid gap-3 sm:grid-cols-3">
            <Select value={serviceId} onValueChange={setServiceId}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Service" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All services</SelectItem>
                {services?.items.map((service) => (
                  <SelectItem key={service.id} value={service.id}>
                    {service.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={severity} onValueChange={(value) => setSeverity(value as SeverityLevel | "all")}>
              <SelectTrigger className="w-[160px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {severityOptions.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={(value) => setStatus(value as IncidentStatus | "all")}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {statusOptions.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        }
      >
        <div className="overflow-hidden rounded-[28px] border border-white/10">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/80 text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Incident</th>
                <th className="px-4 py-3">Service</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Assignee</th>
                <th className="px-4 py-3">Last seen</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((incident) => (
                <tr
                  key={incident.id}
                  className="cursor-pointer border-t border-white/10 bg-white/[0.02] transition hover:bg-white/[0.05]"
                  onClick={() => setSelectedId(incident.id)}
                >
                  <td className="px-4 py-4">
                    <div className="font-medium text-white">{incident.title}</div>
                    <div className="mt-1 text-xs text-muted-foreground">{incident.summary}</div>
                  </td>
                  <td className="px-4 py-4 text-slate-300">{incident.service.name}</td>
                  <td className="px-4 py-4">
                    <StatusPill value={incident.status} />
                  </td>
                  <td className="px-4 py-4">
                    <StatusPill value={incident.severity} />
                  </td>
                  <td className="px-4 py-4 text-slate-300">{incident.assignee?.full_name ?? "Unassigned"}</td>
                  <td className="px-4 py-4">
                    <div className="text-slate-300">{formatDateTime(incident.last_seen_at)}</div>
                    <div className="text-xs text-muted-foreground">{formatRelative(incident.last_seen_at)}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <IncidentDrawer incidentId={selectedId} onClose={() => setSelectedId(null)} />
    </>
  );
}

