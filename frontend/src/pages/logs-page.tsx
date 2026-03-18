import { useMemo, useState } from "react";

import { PageHeader } from "@/components/page-header";
import { Panel } from "@/components/panel";
import { StatusPill } from "@/components/status-pill";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useLogsQuery, useServicesQuery } from "@/hooks/use-signalops";
import { formatDateTime } from "@/lib/format";
import type { SeverityLevel } from "@/types/api";

const severityOptions: Array<SeverityLevel | "all"> = ["all", "info", "warning", "error", "critical"];

export function LogsPage() {
  const [serviceId, setServiceId] = useState("all");
  const [severity, setSeverity] = useState<SeverityLevel | "all">("all");
  const [status, setStatus] = useState("all");
  const [search, setSearch] = useState("");
  const { data: services } = useServicesQuery();

  const params = useMemo(() => {
    const next = new URLSearchParams();
    if (serviceId !== "all") next.set("service_id", serviceId);
    if (severity !== "all") next.set("severity", severity);
    if (status === "anomalous") next.set("status", "anomalous");
    return next;
  }, [serviceId, severity, status]);

  const { data } = useLogsQuery(params);
  const filteredLogs = useMemo(
    () =>
      data?.items.filter((log) =>
        search ? `${log.message} ${log.service.name}`.toLowerCase().includes(search.toLowerCase()) : true,
      ) ?? [],
    [data?.items, search],
  );

  return (
    <>
      <PageHeader
        eyebrow="Log stream"
        title="Search structured log traffic and isolate anomalous error bursts."
        description="Filter the event stream by service, severity, and anomaly state to find the signatures driving incidents and alert breaches."
      />

      <Panel
        title="Log explorer"
        description="Service, severity, anomaly, and message filters."
        action={
          <div className="grid gap-3 lg:grid-cols-4">
            <Input className="w-[220px]" placeholder="Search message or service" value={search} onChange={(event) => setSearch(event.target.value)} />
            <Select value={serviceId} onValueChange={setServiceId}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
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
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All events</SelectItem>
                <SelectItem value="anomalous">Anomalous only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        }
      >
        <div className="grid gap-3">
          {filteredLogs.map((log) => (
            <div key={log.id} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusPill value={log.severity} />
                  {log.is_anomalous ? <StatusPill value="escalated" /> : null}
                  <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{log.service.name}</span>
                </div>
                <div className="text-sm text-muted-foreground">{formatDateTime(log.occurred_at)}</div>
              </div>
              <div className="mt-4 font-medium text-white">{log.message}</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {log.tags.map((tag) => (
                  <span key={tag} className="rounded-full border border-white/10 bg-slate-950/70 px-2.5 py-1 text-xs text-slate-300">
                    {tag}
                  </span>
                ))}
              </div>
              <div className="mt-4 grid gap-2 text-xs text-muted-foreground md:grid-cols-3">
                <div>Source: {log.source}</div>
                <div>Anomaly score: {log.anomaly_score.toFixed(1)}</div>
                <div>Cluster: {log.metadata.cluster ?? "n/a"}</div>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </>
  );
}

