import type { ReactNode } from "react";
import { AlertTriangle, Inbox, LoaderCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DataStateProps {
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}

function StateFrame({
  icon,
  title,
  description,
  action,
  className,
}: DataStateProps & { icon: ReactNode }) {
  return (
    <div
      className={cn(
        "surface-panel flex min-h-[220px] flex-col items-center justify-center rounded-[32px] border border-white/10 px-6 py-10 text-center",
        className,
      )}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full border border-white/10 bg-white/[0.06] text-cyan-100">
        {icon}
      </div>
      <h3 className="mt-5 font-display text-2xl text-white">{title}</h3>
      <p className="mt-3 max-w-xl text-sm leading-7 text-muted-foreground">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}

export function LoadingState({
  title = "Loading control surface",
  description = "Telemetry channels, fleet state, and analytics are being synchronized.",
  className,
}: Partial<DataStateProps>) {
  return (
    <StateFrame
      icon={<LoaderCircle className="h-6 w-6 animate-spin" />}
      title={title ?? "Loading"}
      description={description ?? "Loading data."}
      className={className}
    />
  );
}

export function EmptyState({ title, description, action, className }: DataStateProps) {
  return <StateFrame icon={<Inbox className="h-6 w-6" />} title={title} description={description} action={action} className={className} />;
}

export function ErrorState({
  title = "Unable to load data",
  description = "The control surface could not retrieve the latest fleet snapshot.",
  action,
  className,
}: Partial<DataStateProps>) {
  return (
    <StateFrame
      icon={<AlertTriangle className="h-6 w-6 text-rose-300" />}
      title={title ?? "Unable to load data"}
      description={description ?? "The control surface could not retrieve the latest fleet snapshot."}
      action={action}
      className={className}
    />
  );
}

export function RetryButton({ onRetry, children = "Retry" }: { onRetry?: () => void; children?: ReactNode }) {
  if (!onRetry) {
    return null;
  }
  return (
    <Button variant="outline" onClick={onRetry}>
      {children}
    </Button>
  );
}
