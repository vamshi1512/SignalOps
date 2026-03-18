import { useState } from "react";
import { AlertTriangle, Clock3, FileSearch } from "lucide-react";

import {
  useAddIncidentNoteMutation,
  useIncidentQuery,
  useUpdateIncidentMutation,
  useUsersQuery,
} from "@/hooks/use-signalops";
import { formatDateTime, formatRelative } from "@/lib/format";
import { StatusPill } from "@/components/status-pill";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { IncidentStatus, SeverityLevel } from "@/types/api";

const severityOptions: SeverityLevel[] = ["warning", "error", "critical"];
const statusOptions: IncidentStatus[] = ["open", "acknowledged", "investigating", "resolved"];

export function IncidentDrawer({
  incidentId,
  onClose,
}: {
  incidentId: string | null;
  onClose: () => void;
}) {
  const { data: incident } = useIncidentQuery(incidentId);
  const { data: users } = useUsersQuery();
  const updateIncident = useUpdateIncidentMutation();
  const addNote = useAddIncidentNoteMutation();

  return (
    <Dialog open={Boolean(incidentId)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{incident?.title ?? "Incident details"}</DialogTitle>
          <DialogDescription>
            Timeline, ownership, and remediation controls for the selected incident.
          </DialogDescription>
        </DialogHeader>

        {incident ? (
          <IncidentContent
            key={incident.id}
            incident={incident}
            userOptions={users?.items ?? []}
            onSave={async (payload) => {
              await updateIncident.mutateAsync({ incidentId: incident.id, payload });
            }}
            onAddNote={async (content) => {
              await addNote.mutateAsync({ incidentId: incident.id, content });
            }}
            saving={updateIncident.isPending}
            posting={addNote.isPending}
          />
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function IncidentContent({
  incident,
  userOptions,
  onSave,
  onAddNote,
  saving,
  posting,
}: {
  incident: NonNullable<ReturnType<typeof useIncidentQuery>["data"]>;
  userOptions: Array<{ id: string; full_name: string }>;
  onSave: (payload: Record<string, unknown>) => Promise<void>;
  onAddNote: (content: string) => Promise<void>;
  saving: boolean;
  posting: boolean;
}) {
  const [severity, setSeverity] = useState<SeverityLevel>(incident.severity);
  const [status, setStatus] = useState<IncidentStatus>(incident.status);
  const [assigneeId, setAssigneeId] = useState<string>(incident.assignee?.id ?? "unassigned");
  const [summary, setSummary] = useState(incident.summary);
  const [note, setNote] = useState("");

  async function handleSave() {
    await onSave({
      severity,
      status,
      summary,
      assignee_id: assigneeId === "unassigned" ? null : assigneeId,
    });
  }

  async function handleAddNote() {
    if (!note.trim()) return;
    await onAddNote(note);
    setNote("");
  }

  return (
    <div className="flex flex-1 flex-col overflow-y-auto">
      <div className="grid gap-5 border-b border-white/10 px-6 py-6">
        <div className="flex flex-wrap items-center gap-3">
          <StatusPill value={incident.status} />
          <StatusPill value={incident.severity} />
          <StatusPill value={incident.environment} />
          <span className="text-sm text-muted-foreground">{incident.service.name}</span>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          <StatCard icon={Clock3} label="First seen" value={formatDateTime(incident.first_seen_at)} detail={formatRelative(incident.first_seen_at)} />
          <StatCard icon={AlertTriangle} label="Error rate" value={`${incident.current_error_rate.toFixed(1)}%`} detail={`${incident.occurrence_count} occurrences`} />
          <StatCard icon={FileSearch} label="Health impact" value={`${incident.health_impact.toFixed(0)} pts`} detail={`${incident.affected_logs} grouped logs`} />
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-4">
          <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Root cause hint</div>
          <p className="mt-3 text-sm leading-6 text-slate-200">{incident.root_cause_hint}</p>
        </div>
      </div>

      <div className="grid gap-6 px-6 py-6 lg:grid-cols-[1fr_0.95fr]">
        <div className="space-y-4">
          <div>
            <div className="mb-2 text-sm text-slate-300">Incident summary</div>
            <Textarea value={summary} onChange={(event) => setSummary(event.target.value)} />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <Field label="Severity">
              <Select value={severity} onValueChange={(value) => setSeverity(value as SeverityLevel)}>
                <SelectTrigger>
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
            </Field>
            <Field label="Status">
              <Select value={status} onValueChange={(value) => setStatus(value as IncidentStatus)}>
                <SelectTrigger>
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
            </Field>
            <Field label="Assignee">
              <Select value={assigneeId} onValueChange={setAssigneeId}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="unassigned">Unassigned</SelectItem>
                  {userOptions.map((user) => (
                    <SelectItem key={user.id} value={user.id}>
                      {user.full_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Apply incident changes"}
          </Button>
        </div>

        <div className="space-y-4">
          <div>
            <div className="mb-2 text-sm text-slate-300">Operator note</div>
            <Textarea
              placeholder="Capture mitigation progress, handoff context, or rollback decisions."
              value={note}
              onChange={(event) => setNote(event.target.value)}
            />
          </div>
          <Button variant="secondary" onClick={handleAddNote} disabled={posting || !note.trim()}>
            {posting ? "Posting..." : "Add note"}
          </Button>
          <div className="space-y-3">
            <div className="text-sm text-slate-300">Timeline</div>
            <div className="space-y-3">
              {incident.notes.map((entry) => (
                <div key={entry.id} className="rounded-3xl border border-white/10 bg-white/[0.04] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-medium text-white">
                      {entry.author?.full_name ?? "SignalOps Automation"}
                    </div>
                    <div className="text-xs text-muted-foreground">{formatDateTime(entry.created_at)}</div>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{entry.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof Clock3;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-4">
      <div className="mb-3 inline-flex rounded-2xl border border-white/10 bg-white/5 p-2">
        <Icon className="h-4 w-4 text-cyan-200" />
      </div>
      <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{label}</div>
      <div className="mt-2 font-display text-2xl text-white">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{detail}</div>
    </div>
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
