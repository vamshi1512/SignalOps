import { Boxes, CalendarClock, PlaySquare, RadioTower } from "lucide-react";
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
  { label: "Admin", email: "admin@testforge.dev", password: "Admin123!" },
  { label: "QA Lead", email: "qa.lead@testforge.dev", password: "QaLead123!" },
  { label: "Viewer", email: "viewer@testforge.dev", password: "Viewer123!" },
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
          <Badge className="border-primary/20 bg-primary/10 text-primary">TestForge Console</Badge>
          <div className="max-w-3xl space-y-5">
            <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-gradient-to-br from-sky-400 via-cyan-300 to-orange-300 text-slate-950 shadow-glow">
              <RadioTower className="h-7 w-7" />
            </div>
            <div>
              <h1 className="font-display text-5xl leading-tight text-foreground lg:text-6xl">
                Test automation management with platform-grade execution maturity.
              </h1>
              <p className="mt-4 max-w-2xl text-lg text-muted-foreground">
                Coordinate API and UI suites, execute runs, inspect failures, review audit history, and monitor
                scheduling confidence from one premium engineering dashboard.
              </p>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <FeatureCard icon={PlaySquare} title="Run orchestration" text="Manual launches, simulated parallelism, and scheduled suite execution." />
            <FeatureCard icon={CalendarClock} title="Schedule control" text="Cadence-aware execution windows with environment targeting." />
            <FeatureCard icon={Boxes} title="Rich artifacts" text="UI screenshots, API request traces, logs, and notifications on failed runs." />
          </div>
        </div>
        <div className="mt-8 rounded-[28px] border border-border bg-background/30 p-5">
          <div className="flex flex-wrap gap-3">
            {accounts.map((account) => (
              <button
                key={account.email}
                type="button"
                onClick={() => form.reset(account)}
                className="rounded-2xl border border-border bg-background/40 px-4 py-3 text-left transition hover:bg-secondary"
              >
                <div className="text-sm font-medium text-foreground">{account.label} demo</div>
                <div className="text-xs text-muted-foreground">{account.email}</div>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="surface-panel flex items-center justify-center p-8 lg:p-10">
        <div className="w-full max-w-md space-y-6">
          <div>
            <h2 className="font-display text-3xl text-foreground">Authenticate</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Use a seeded demo account to access the full QA execution workspace.
            </p>
          </div>
          <form className="space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Email</label>
              <Input type="email" {...form.register("email")} />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Password</label>
              <Input type="password" {...form.register("password")} />
            </div>
            {error ? (
              <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {error}
              </div>
            ) : null}
            <Button className="w-full" size="lg" type="submit" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting ? "Signing in..." : "Enter TestForge"}
            </Button>
          </form>
          <div className="rounded-3xl border border-border bg-background/35 p-5 text-sm text-muted-foreground">
            Seeded accounts initialize automatically on backend startup. OpenAPI docs remain available at
            <span className="ml-1 font-medium text-foreground">`/docs`</span>.
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
  icon: typeof PlaySquare;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-[28px] border border-border bg-background/30 p-5">
      <div className="mb-4 inline-flex rounded-2xl border border-border bg-secondary p-3">
        <Icon className="h-5 w-5 text-primary" />
      </div>
      <div className="font-display text-xl text-foreground">{title}</div>
      <div className="mt-2 text-sm text-muted-foreground">{text}</div>
    </div>
  );
}
