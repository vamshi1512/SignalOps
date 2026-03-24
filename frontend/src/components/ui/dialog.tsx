import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export function DialogContent({
  className,
  children,
  ...props
}: DialogPrimitive.DialogContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-sm" />
      <DialogPrimitive.Content
        className={cn(
          "fixed inset-y-4 right-4 z-50 flex w-[min(760px,calc(100vw-2rem))] flex-col rounded-[28px] border border-border bg-card/95 shadow-panel outline-none",
          className,
        )}
        {...props}
      >
        <DialogPrimitive.Close className="absolute right-5 top-5 rounded-full border border-border p-2 text-muted-foreground transition hover:bg-secondary hover:text-foreground">
          <X className="h-4 w-4" />
        </DialogPrimitive.Close>
        {children}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export function DialogHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("border-b border-border/80 px-6 py-5", className)} {...props} />;
}

export function DialogTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("font-display text-xl text-foreground", className)} {...props} />;
}

export function DialogDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("mt-2 text-sm text-muted-foreground", className)} {...props} />;
}
