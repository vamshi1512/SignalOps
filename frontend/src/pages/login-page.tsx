import { RadioTower, ShieldCheck, Siren, TerminalSquare } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { useAuth } from "@/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

type FormValues = z.infer<typeof schema>;

const accounts = [
  { label: "Admin", email: "admin@signalops.dev", password: "Admin123!" },
  { label: "SRE", email: "sre@signalops.dev", password: "Sre123!" },
  { label: "Viewer", email: "viewer@signalops.dev", password: "Viewer123!" },
];

export function LoginPage() {
  const { login, error, clearError } = useAuth();
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: accounts[1],
  });

  async function onSubmit(values: FormValues) {
    clearError();
    await login(values.email, values.password);
  }

  return (
    <div className="mx-auto grid min-h-screen w-full max-w-[1600px] gap-6 px-4 py-4 lg:grid-cols-[1.15fr_0.85fr] lg:px-6">
      <section className="surface-panel-elevated flex flex-col justify-between overflow-hidden p-8 lg:p-10">
        <div className="space-y-8">
          <Badge className="border-cyan-400/20 bg-cyan-400/10 text-cyan-100">SignalOps Console</Badge>
          <div className="max-w-3xl space-y-5">
            <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-gradient-to-br from-cyan-400 via-sky-400 to-emerald-400 text-slate-950 shadow-glow">
              <RadioTower className="h-7 w-7" />
            </div>
            <div>
              <h1 className="font-display text-5xl leading-tight text-white lg:text-6xl">
                Reliability operations tooling with real incident gravity.
              </h1>
              <p className="mt-4 max-w-2xl text-lg text-slate-300">
                Ingest logs, cluster repeated failures into incidents, drive alert workflows, and visualize service
                posture from one dark-mode operations console.
              </p>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <FeatureCard icon={TerminalSquare} title="Structured logs" text="Burst-aware ingestion with severity, tags, and anomaly context." />
            <FeatureCard icon={Siren} title="Incident grouping" text="Repeated failures collapse into investigation-ready incidents." />
            <FeatureCard icon={ShieldCheck} title="Alert control" text="Threshold rules, suppression, acknowledgement, and escalation loops." />
          </div>
        </div>
        <div className="mt-8 rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
          <div className="flex flex-wrap gap-3">
            {accounts.map((account) => (
              <button
                key={account.email}
                type="button"
                onClick={() => form.reset(account)}
                className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left transition hover:bg-white/10"
              >
                <div className="text-sm font-medium text-white">{account.label} demo</div>
                <div className="text-xs text-muted-foreground">{account.email}</div>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="surface-panel flex items-center justify-center p-8 lg:p-10">
        <div className="w-full max-w-md space-y-6">
          <div>
            <h2 className="font-display text-3xl text-white">Authenticate</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Use a seeded demo account to access the full operations workspace.
            </p>
          </div>
          <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Email</label>
              <Input type="email" {...form.register("email")} />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-300">Password</label>
              <Input type="password" {...form.register("password")} />
            </div>
            {error ? (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {error}
              </div>
            ) : null}
            <Button className="w-full" size="lg" type="submit" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting ? "Signing in..." : "Enter SignalOps"}
            </Button>
          </form>
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-sm text-muted-foreground">
            Seeded accounts initialize automatically on backend startup. OpenAPI docs remain available at
            <span className="ml-1 font-medium text-white">`/docs`</span>.
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof TerminalSquare;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
      <div className="mb-4 inline-flex rounded-2xl border border-white/10 bg-white/10 p-3">
        <Icon className="h-5 w-5 text-cyan-200" />
      </div>
      <div className="font-display text-xl text-white">{title}</div>
      <div className="mt-2 text-sm text-muted-foreground">{text}</div>
    </div>
  );
}

