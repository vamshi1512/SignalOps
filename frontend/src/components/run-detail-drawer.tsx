import type { ReactNode } from "react";
import { AlertTriangle, ExternalLink, FileCode2, ImageIcon, RefreshCcw, ScrollText } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { StatusPill } from "@/components/status-pill";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRunQuery } from "@/hooks/use-testforge";
import { getErrorMessage } from "@/lib/api";
import { formatDateTime, formatDurationMs, formatRelative } from "@/lib/format";

export function RunDetailDrawer({
  runId,
  open,
  onOpenChange,
}: {
  runId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { data, error, isError, isLoading, refetch } = useRunQuery(runId);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="overflow-hidden">
        <DialogHeader>
          <DialogTitle>{data ? data.suite.name : "Run detail"}</DialogTitle>
          <DialogDescription>
            {data
              ? `${data.project.name} · ${data.environment.name} · ${formatRelative(data.created_at)}`
              : "Inspect screenshots, traces, logs, and failure summaries."}
          </DialogDescription>
        </DialogHeader>

        <div className="overflow-y-auto px-6 pb-6">
          {isLoading ? (
            <div className="space-y-4 pt-4">
              <Skeleton className="h-24" />
              <Skeleton className="h-40" />
              <Skeleton className="h-40" />
            </div>
          ) : isError || !data ? (
            <div className="pt-4">
              <EmptyState
                icon={AlertTriangle}
                title="Run detail could not be loaded"
                description={getErrorMessage(error, "The selected run detail request failed.")}
                tone="error"
                compact
                action={
                  <Button variant="outline" onClick={() => refetch()}>
                    <RefreshCcw className="h-4 w-4" />
                    Retry load
                  </Button>
                }
              />
            </div>
          ) : (
            <div className="space-y-5 pt-4">
              <div className="grid gap-3 md:grid-cols-4">
                <StatBlock label="Status" value={<StatusPill value={data.status} />} />
                <StatBlock label="Duration" value={formatDurationMs(data.duration_ms)} />
                <StatBlock label="Assertions" value={`${data.pass_count}/${data.total_count} passed`} />
                <StatBlock label="Parallel" value={`${data.requested_parallel_workers} workers`} />
              </div>

              <div className="rounded-[28px] border border-border bg-background/25 p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <StatusPill value={data.trigger_type} />
                  <StatusPill value={data.suite.suite_type} />
                  <StatusPill value={data.environment.kind} />
                  {data.flaky_count > 0 ? <StatusPill value="flaky" /> : null}
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <MetaRow label="Started" value={data.started_at ? formatDateTime(data.started_at) : "Queued"} />
                  <MetaRow label="Finished" value={data.finished_at ? formatDateTime(data.finished_at) : "Running"} />
                  <MetaRow label="Owner" value={data.suite.owner} />
                  <MetaRow label="Command" value={String(data.summary.source_command ?? "N/A")} />
                  <MetaRow label="Fixture profile" value={String(data.summary.fixture_profile ?? data.fixture_set?.name ?? "Default")} />
                  <MetaRow label="Branch" value={String(data.summary.branch ?? "main")} />
                </div>
              </div>

              {Object.keys(data.metadata).length ? (
                <div className="rounded-[28px] border border-border bg-background/25 p-5">
                  <div className="font-display text-lg text-foreground">Runtime metadata</div>
                  <div className="mt-3 grid gap-3 md:grid-cols-2">
                    {Object.entries(data.metadata).map(([key, value]) => (
                      <MetaRow key={key} label={formatKeyLabel(key)} value={String(value)} />
                    ))}
                  </div>
                </div>
              ) : null}

              {data.notifications.length ? (
                <div className="rounded-[28px] border border-border bg-background/25 p-5">
                  <div className="font-display text-lg text-foreground">Notifications</div>
                  <div className="mt-3 space-y-3">
                    {data.notifications.map((notification) => (
                      <div key={notification.id} className="rounded-2xl border border-border bg-card/60 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="font-medium text-foreground">{notification.subject}</div>
                            <div className="text-sm text-muted-foreground">{notification.recipient}</div>
                          </div>
                          <StatusPill value={notification.channel} />
                        </div>
                        <p className="mt-3 text-sm text-muted-foreground">{notification.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className="space-y-4">
                {data.results.map((result) => (
                  <div key={result.id} className="rounded-[28px] border border-border bg-card/75 p-5">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <div className="font-display text-xl text-foreground">{result.name}</div>
                        <div className="mt-1 text-sm text-muted-foreground">{result.module_name}</div>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        <StatusPill value={result.status} />
                        <div className="text-sm text-muted-foreground">{formatDurationMs(result.duration_ms)}</div>
                      </div>
                    </div>

                    {result.error_message ? (
                      <div className="mt-4 rounded-2xl border border-red-500/20 bg-red-500/8 p-4 text-sm text-red-200">
                        {result.error_message}
                      </div>
                    ) : null}

                    <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_0.9fr]">
                      <div className="space-y-3">
                        {result.attachments.length ? (
                          result.attachments.map((attachment) =>
                            attachment.type === "image" ? (
                              <div key={attachment.url} className="overflow-hidden rounded-2xl border border-border bg-background/40">
                                <img src={attachment.url} alt={attachment.label} className="h-auto w-full object-cover" />
                              </div>
                            ) : (
                              <a
                                key={attachment.url}
                                href={attachment.url}
                                target="_blank"
                                rel="noreferrer"
                                className="flex items-center justify-between rounded-2xl border border-border bg-background/35 px-4 py-3 text-sm text-muted-foreground transition hover:bg-secondary"
                              >
                                <span className="flex items-center gap-2">
                                  {attachment.type === "json" ? <FileCode2 className="h-4 w-4" /> : <ScrollText className="h-4 w-4" />}
                                  {attachment.label}
                                </span>
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            ),
                          )
                        ) : (
                          <div className="flex items-center gap-2 rounded-2xl border border-border bg-background/35 px-4 py-3 text-sm text-muted-foreground">
                            <ImageIcon className="h-4 w-4" />
                            No file artifacts for this result.
                          </div>
                        )}
                      </div>
                      <div className="space-y-3">
                        {Object.keys(result.request_details).length ? (
                          <TraceBlock title="Request" value={JSON.stringify(result.request_details, null, 2)} />
                        ) : null}
                        {Object.keys(result.response_details).length ? (
                          <TraceBlock title="Response" value={JSON.stringify(result.response_details, null, 2)} />
                        ) : null}
                        {result.stack_trace ? <TraceBlock title="Stack Trace" value={result.stack_trace} /> : null}
                        {result.logs ? <TraceBlock title="Runner Log" value={result.logs} /> : null}
                        {!Object.keys(result.request_details).length &&
                        !Object.keys(result.response_details).length &&
                        !result.stack_trace &&
                        !result.logs ? (
                          <div className="rounded-2xl border border-border bg-background/35 px-4 py-3 text-sm text-muted-foreground">
                            No structured trace details for this result.
                          </div>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function StatBlock({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-2xl border border-border bg-card/70 p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-3 text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card/65 px-4 py-3">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm text-foreground">{value}</div>
    </div>
  );
}

function TraceBlock({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-background/45 p-4">
      <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{title}</div>
      <pre className="mt-3 overflow-x-auto whitespace-pre-wrap break-all text-xs text-foreground">{value}</pre>
    </div>
  );
}

function formatKeyLabel(value: string) {
  return value.replace(/_/g, " ");
}
