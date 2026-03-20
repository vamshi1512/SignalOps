import { motion } from "framer-motion";
import { ArrowRight, Bot, CloudRain, Radar, Shield, Waypoints } from "lucide-react";
import { Link } from "react-router-dom";

import { ErrorState, LoadingState } from "@/components/data-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useDemoAccountsQuery } from "@/hooks/use-roboyard";

const highlights = [
  { icon: Bot, title: "Fleet supervision", body: "Track autonomous mowers, utility carts, and inspection bots in real time." },
  { icon: Waypoints, title: "Mission orchestration", body: "Pause, resume, reroute, or return robots to base with a live command queue." },
  { icon: CloudRain, title: "Weather-aware autonomy", body: "Inject rain and wind safety events that alter robot behavior and mission windows." },
  { icon: Shield, title: "Operational auditability", body: "Review operator actions, route replay, incidents, and robot health trends." },
];

export function LandingPage() {
  const accounts = useDemoAccountsQuery();

  return (
    <div className="relative min-h-screen overflow-hidden bg-background px-4 py-6 text-foreground">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,197,94,0.15),transparent_28%),radial-gradient(circle_at_top_right,rgba(56,189,248,0.16),transparent_24%),linear-gradient(180deg,rgba(2,6,23,0.95),rgba(2,6,23,1))]" />
      <div className="relative mx-auto flex max-w-[1480px] flex-col gap-10">
        <header className="flex items-center justify-between rounded-[32px] border border-white/10 bg-white/[0.03] px-6 py-4 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-[22px] bg-gradient-to-br from-cyan-300 to-emerald-300 text-slate-950">
              <Radar className="h-6 w-6" />
            </div>
            <div>
              <div className="font-display text-xl text-white">RoboYard Control</div>
              <div className="text-sm text-muted-foreground">Autonomous outdoor mission control</div>
            </div>
          </div>
          <Button asChild size="lg">
            <Link to="/login">
              Operator Login
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="rounded-[40px] border border-white/10 bg-slate-950/70 p-8 shadow-panel"
          >
            <Badge className="border-emerald-400/20 bg-emerald-400/10 text-emerald-100">Portfolio-grade realtime robotics stack</Badge>
            <h1 className="mt-6 max-w-4xl font-display text-5xl leading-tight text-white lg:text-7xl">
              Mission control for the autonomous yard.
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-slate-300">
              RoboYard Control simulates a serious operations console for autonomous lawn care, utility, and inspection
              robots with live telemetry, geofences, route progress, weather pauses, charging cycles, and operator
              overrides.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link to="/login">Launch Console</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <a href="#demo-accounts">View Demo Accounts</a>
              </Button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.08 }}
            className="rounded-[40px] border border-white/10 bg-slate-950/80 p-6 shadow-panel"
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Command preview</div>
                <div className="mt-2 font-display text-2xl text-white">North Course / Service Yard</div>
              </div>
              <Badge>Realtime map</Badge>
            </div>
            <div className="mt-6 rounded-[28px] border border-white/10 bg-slate-950 p-4">
              <svg viewBox="0 0 760 420" className="h-[320px] w-full">
                <rect width={760} height={420} fill="#020617" />
                <polygon points="40,40 340,40 340,180 40,180" fill="rgba(34,197,94,0.14)" stroke="#22c55e" strokeWidth="2" strokeDasharray="8 8" />
                <polygon points="400,60 710,60 710,210 400,210" fill="rgba(56,189,248,0.14)" stroke="#38bdf8" strokeWidth="2" strokeDasharray="8 8" />
                <polygon points="70,240 710,240 710,370 70,370" fill="rgba(245,158,11,0.12)" stroke="#f59e0b" strokeWidth="2" strokeDasharray="8 8" />
                <polyline points="58,58 110,58 110,160 180,160 180,58 250,58 250,160 322,160" fill="none" stroke="rgba(148,163,184,0.55)" strokeWidth="3" strokeDasharray="4 7" />
                <circle cx="180" cy="122" r="14" fill="#34d399" />
                <circle cx="520" cy="118" r="14" fill="#38bdf8" />
                <circle cx="280" cy="302" r="14" fill="#f59e0b" />
                <circle cx="194" cy="138" r="34" fill="rgba(52,211,153,0.1)" stroke="rgba(52,211,153,0.4)" />
                <text x="56" y="78" fill="#e2e8f0" fontSize="18" fontWeight="700">North Course</text>
                <text x="418" y="96" fill="#e2e8f0" fontSize="18" fontWeight="700">Service Yard</text>
                <text x="90" y="272" fill="#e2e8f0" fontSize="18" fontWeight="700">South Perimeter</text>
              </svg>
            </div>
          </motion.div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {highlights.map((item, index) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.12 + index * 0.06 }}
              className="rounded-[32px] border border-white/10 bg-white/[0.03] p-6 backdrop-blur"
            >
              <item.icon className="h-8 w-8 text-cyan-200" />
              <div className="mt-5 font-display text-2xl text-white">{item.title}</div>
              <p className="mt-3 text-sm leading-7 text-slate-300">{item.body}</p>
            </motion.div>
          ))}
        </section>

        <section id="demo-accounts" className="rounded-[40px] border border-white/10 bg-slate-950/75 p-8 shadow-panel">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <Badge>Demo access</Badge>
              <h2 className="mt-4 font-display text-4xl text-white">Portfolio walkthrough accounts</h2>
            </div>
            <Button asChild variant="outline">
              <Link to="/login">Use Demo Credentials</Link>
            </Button>
          </div>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {accounts.isLoading ? <LoadingState className="md:col-span-3" title="Loading demo personas" description="Preparing the seeded walkthrough accounts for the landing page." /> : null}
            {accounts.isError ? (
              <ErrorState
                className="md:col-span-3"
                title="Demo accounts unavailable"
                description={accounts.error instanceof Error ? accounts.error.message : "The landing page could not retrieve the seeded walkthrough credentials."}
              />
            ) : null}
            {accounts.data?.map((account) => (
              <div key={account.email} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-medium text-white">{account.full_name}</div>
                  <Badge>{account.role}</Badge>
                </div>
                <div className="mt-4 space-y-2 text-sm text-slate-300">
                  <div>{account.email}</div>
                  <div>Password: {account.password}</div>
                  <div>{account.title}</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
