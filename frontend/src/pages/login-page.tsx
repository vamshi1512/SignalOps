import { type FormEvent, useState } from "react";
import { ArrowRight, LockKeyhole } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { ErrorState, LoadingState } from "@/components/data-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useDemoAccountsQuery } from "@/hooks/use-roboyard";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, error, clearError } = useAuth();
  const accounts = useDemoAccountsQuery();
  const [email, setEmail] = useState("ops@roboyard.dev");
  const [password, setPassword] = useState("Ops123!");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    clearError();
    try {
      await login(email, password);
      navigate("/console");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-background px-4 py-6">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_left_top,rgba(34,197,94,0.14),transparent_28%),radial-gradient(circle_at_right_top,rgba(56,189,248,0.16),transparent_24%),linear-gradient(180deg,rgba(2,6,23,0.96),rgba(2,6,23,1))]" />
      <div className="relative mx-auto grid min-h-[calc(100vh-3rem)] max-w-[1320px] gap-6 lg:grid-cols-[1fr_440px]">
        <div className="flex flex-col justify-between rounded-[40px] border border-white/10 bg-white/[0.03] p-8 shadow-panel">
          <div>
            <Badge className="border-cyan-400/20 bg-cyan-400/10 text-cyan-100">Mission console access</Badge>
            <h1 className="mt-6 max-w-3xl font-display text-5xl leading-tight text-white lg:text-6xl">
              Sign into the autonomous operations floor.
            </h1>
            <p className="mt-5 max-w-2xl text-lg text-slate-300">
              Monitor fleet state, inspect route history, acknowledge safety alerts, and issue mission commands from a
              realtime control surface.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {accounts.isLoading ? <LoadingState className="md:col-span-3 min-h-[180px]" title="Loading demo credentials" description="Operator, admin, and viewer personas are being prepared." /> : null}
            {accounts.isError ? (
              <ErrorState
                className="md:col-span-3 min-h-[180px]"
                title="Unable to load demo credentials"
                description={accounts.error instanceof Error ? accounts.error.message : "The login page could not load the seeded account presets."}
              />
            ) : null}
            {accounts.data?.map((account) => (
              <button
                key={account.email}
                type="button"
                onClick={() => {
                  setEmail(account.email);
                  setPassword(account.password);
                }}
                className="rounded-[28px] border border-white/10 bg-slate-950/60 p-5 text-left transition hover:border-cyan-400/30 hover:bg-cyan-400/10"
              >
                <div className="font-medium text-white">{account.full_name}</div>
                <div className="mt-2 text-sm text-slate-300">{account.role}</div>
                <div className="mt-4 text-xs text-muted-foreground">{account.email}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center">
          <form onSubmit={handleSubmit} className="w-full rounded-[36px] border border-white/10 bg-slate-950/85 p-8 shadow-panel">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-200">
                <LockKeyhole className="h-6 w-6" />
              </div>
              <div>
                <div className="font-display text-2xl text-white">Operator Login</div>
                <div className="text-sm text-muted-foreground">JWT session access</div>
              </div>
            </div>

            <div className="mt-8 grid gap-4">
              <div>
                <label className="mb-2 block text-sm text-slate-300">Email</label>
                <Input value={email} onChange={(event) => setEmail(event.target.value)} />
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-300">Password</label>
                <Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
              </div>
            </div>

            {error ? <div className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-200">{error}</div> : null}

            <Button type="submit" size="lg" className="mt-6 w-full" disabled={isSubmitting}>
              {isSubmitting ? "Signing in..." : "Enter RoboYard Control"}
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
