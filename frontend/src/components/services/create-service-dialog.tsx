import { useState } from "react";

import { useCreateServiceMutation } from "@/hooks/use-signalops";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { ServiceEnvironment, ServicePriority } from "@/types/api";

const environments: ServiceEnvironment[] = ["production", "staging", "development"];
const priorities: ServicePriority[] = ["p0", "p1", "p2", "p3"];

export function CreateServiceDialog() {
  const [open, setOpen] = useState(false);
  const mutation = useCreateServiceMutation();
  const [form, setForm] = useState({
    name: "",
    slug: "",
    owner: "",
    environment: "production" as ServiceEnvironment,
    priority: "p1" as ServicePriority,
    sla_target: "99.9",
    description: "",
  });

  async function handleSubmit() {
    await mutation.mutateAsync({
      ...form,
      sla_target: Number(form.sla_target),
    });
    setOpen(false);
    setForm({
      name: "",
      slug: "",
      owner: "",
      environment: "production",
      priority: "p1",
      sla_target: "99.9",
      description: "",
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Register service</Button>
      </DialogTrigger>
      <DialogContent className="max-w-[720px]">
        <DialogHeader>
          <DialogTitle>Add service registry entry</DialogTitle>
          <DialogDescription>
            Register a new service with ownership, environment posture, priority, and SLA metadata.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 p-6 md:grid-cols-2">
          <Field label="Name">
            <Input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          </Field>
          <Field label="Slug">
            <Input value={form.slug} onChange={(event) => setForm({ ...form, slug: event.target.value })} />
          </Field>
          <Field label="Owner">
            <Input value={form.owner} onChange={(event) => setForm({ ...form, owner: event.target.value })} />
          </Field>
          <Field label="SLA target">
            <Input
              type="number"
              step="0.01"
              value={form.sla_target}
              onChange={(event) => setForm({ ...form, sla_target: event.target.value })}
            />
          </Field>
          <Field label="Environment">
            <Select value={form.environment} onValueChange={(value) => setForm({ ...form, environment: value as ServiceEnvironment })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {environments.map((environment) => (
                  <SelectItem key={environment} value={environment}>
                    {environment}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Priority">
            <Select value={form.priority} onValueChange={(value) => setForm({ ...form, priority: value as ServicePriority })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {priorities.map((priority) => (
                  <SelectItem key={priority} value={priority}>
                    {priority}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <div className="md:col-span-2">
            <Field label="Description">
              <Textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
            </Field>
          </div>
          <div className="md:col-span-2">
            <Button onClick={handleSubmit} disabled={mutation.isPending}>
              {mutation.isPending ? "Creating..." : "Create service"}
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

