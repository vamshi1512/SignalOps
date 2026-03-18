import { useState } from "react";

import { useCreateRuleMutation, useServicesQuery } from "@/hooks/use-signalops";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { AlertMetric, SeverityLevel } from "@/types/api";

const metrics: AlertMetric[] = ["error_rate", "critical_logs", "anomaly_score", "incident_count"];
const severities: SeverityLevel[] = ["warning", "error", "critical"];

export function CreateRuleDialog() {
  const [open, setOpen] = useState(false);
  const { data: services } = useServicesQuery();
  const mutation = useCreateRuleMutation();
  const [form, setForm] = useState({
    service_id: "",
    name: "",
    description: "",
    metric: "error_rate" as AlertMetric,
    threshold: "5",
    window_minutes: "15",
    severity: "error" as SeverityLevel,
    suppression_minutes: "20",
    escalate_after_minutes: "20",
  });

  async function handleSubmit() {
    await mutation.mutateAsync({
      ...form,
      service_id: form.service_id || null,
      threshold: Number(form.threshold),
      window_minutes: Number(form.window_minutes),
      suppression_minutes: Number(form.suppression_minutes),
      escalate_after_minutes: Number(form.escalate_after_minutes),
    });
    setOpen(false);
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary">Create alert rule</Button>
      </DialogTrigger>
      <DialogContent className="max-w-[720px]">
        <DialogHeader>
          <DialogTitle>Create threshold rule</DialogTitle>
          <DialogDescription>
            Wire a service-level alert to error rate, critical bursts, anomaly score, or incident volume.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 p-6 md:grid-cols-2">
          <Field label="Rule name">
            <Input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          </Field>
          <Field label="Service scope">
            <Select value={form.service_id || "all"} onValueChange={(value) => setForm({ ...form, service_id: value === "all" ? "" : value })}>
              <SelectTrigger>
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
          </Field>
          <Field label="Metric">
            <Select value={form.metric} onValueChange={(value) => setForm({ ...form, metric: value as AlertMetric })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {metrics.map((metric) => (
                  <SelectItem key={metric} value={metric}>
                    {metric}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Severity">
            <Select value={form.severity} onValueChange={(value) => setForm({ ...form, severity: value as SeverityLevel })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {severities.map((severity) => (
                  <SelectItem key={severity} value={severity}>
                    {severity}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Threshold">
            <Input value={form.threshold} onChange={(event) => setForm({ ...form, threshold: event.target.value })} />
          </Field>
          <Field label="Window (minutes)">
            <Input value={form.window_minutes} onChange={(event) => setForm({ ...form, window_minutes: event.target.value })} />
          </Field>
          <Field label="Suppress (minutes)">
            <Input value={form.suppression_minutes} onChange={(event) => setForm({ ...form, suppression_minutes: event.target.value })} />
          </Field>
          <Field label="Escalate after">
            <Input value={form.escalate_after_minutes} onChange={(event) => setForm({ ...form, escalate_after_minutes: event.target.value })} />
          </Field>
          <div className="md:col-span-2">
            <Field label="Description">
              <Input value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
            </Field>
          </div>
          <div className="md:col-span-2">
            <Button onClick={handleSubmit} disabled={mutation.isPending}>
              {mutation.isPending ? "Creating..." : "Create rule"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <div className="text-sm text-slate-300">{label}</div>
      {children}
    </div>
  );
}

