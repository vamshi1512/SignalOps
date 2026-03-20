import type { ReactNode } from "react";
import {
  Bot,
  Gauge,
  History,
  LogOut,
  Map,
  PanelLeftClose,
  Radio,
  ShieldCheck,
  Siren,
  Waypoints,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useLiveFleetStream, useOverviewQuery } from "@/hooks/use-roboyard";
import { formatRelative } from "@/lib/format";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "/console", label: "Control", icon: Gauge },
  { to: "/fleet", label: "Fleet", icon: Bot },
  { to: "/missions", label: "Missions", icon: Waypoints },
  { to: "/alerts", label: "Alerts", icon: Siren },
  { to: "/history", label: "Replay", icon: History },
  { to: "/admin", label: "Admin", icon: ShieldCheck },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { session, logout } = useAuth();
  const stream = useLiveFleetStream();
  const overview = useOverviewQuery();
  const navigationItems = navigation.filter((item) => item.to !== "/admin" || session?.user.role === "admin");

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-0 grid-fade opacity-20" />
      <div className="pointer-events-none absolute -left-24 top-12 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full bg-emerald-400/10 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-[1700px] flex-col gap-4 px-4 py-4 lg:flex-row lg:px-6">
        <aside className="surface-panel-elevated control-shell flex flex-col gap-6 p-5 lg:min-h-[calc(100vh-2rem)] lg:w-[300px]">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-[24px] bg-gradient-to-br from-cyan-300 via-emerald-300 to-lime-300 text-slate-950 shadow-glow">
                <Map className="h-7 w-7" />
              </div>
              <div>
                <div className="font-display text-xl text-white">RoboYard Control</div>
                <div className="text-sm text-muted-foreground">Autonomous ground operations</div>
              </div>
            </div>

            <div className="rounded-[28px] border border-cyan-400/15 bg-cyan-400/10 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
              <div className="flex items-center justify-between">
                <Badge className="border-cyan-400/20 bg-cyan-400/10 text-cyan-100">Demo fleet live</Badge>
                <span
                  className={cn(
                    "h-2.5 w-2.5 rounded-full",
                    stream.status === "connected" ? "bg-emerald-300 shadow-[0_0_24px_rgba(52,211,153,0.6)]" : "bg-amber-300",
                  )}
                />
              </div>
              <p className="mt-3 text-sm text-cyan-50/90">
                Streaming telemetry, autonomous mission execution, alert bursts, and weather-driven holds.
              </p>
            </div>
          </div>

          <nav className="grid gap-2">
            {navigationItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                    isActive ? "bg-white/10 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]" : "text-muted-foreground hover:bg-white/5 hover:text-white",
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="grid gap-3 rounded-[28px] border border-white/10 bg-white/[0.04] p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Weather cell</div>
                <div className="mt-2 font-display text-lg text-white">{overview.data?.weather.state ?? "standby"}</div>
              </div>
              <Badge>{stream.status}</Badge>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Open Alerts</div>
                <div className="mt-2 font-display text-2xl text-white">{overview.data?.active_alerts.length ?? "--"}</div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Last Tick</div>
                <div className="mt-2 text-sm text-white">{formatRelative(stream.lastTick)}</div>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
              <div className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Fleet posture</div>
              <div className="mt-2 flex items-center justify-between text-sm text-slate-200">
                <span>{overview.data?.robots.length ?? 0} tracked</span>
                <span>{overview.data?.active_missions.length ?? 0} live lanes</span>
              </div>
            </div>
          </div>

          <div className="mt-auto rounded-[28px] border border-white/10 bg-white/[0.04] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm text-muted-foreground">Signed in as</div>
                <div className="mt-1 font-medium text-white">{session?.user.full_name}</div>
                <div className="text-sm text-muted-foreground">{session?.user.title}</div>
              </div>
              <Badge>{session?.user.role ?? "viewer"}</Badge>
            </div>
            <div className="mt-4 grid gap-3 rounded-2xl border border-white/10 bg-slate-950/60 p-3">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <Radio className="h-4 w-4 text-cyan-300" />
                {session?.user.email}
              </div>
              <Button variant="ghost" size="sm" onClick={logout} className="justify-start">
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            </div>
          </div>
        </aside>

        <main className="flex-1 pb-8">
          <div className="mb-4 flex items-center justify-between gap-4 rounded-[28px] border border-white/10 bg-white/[0.04] px-5 py-4 lg:hidden">
            <div className="flex items-center gap-3">
              <PanelLeftClose className="h-5 w-5 text-cyan-300" />
              <div>
                <div className="font-display text-xl text-white">RoboYard Control</div>
                <div className="text-sm text-muted-foreground">Mission console</div>
              </div>
            </div>
            <Badge>{session?.user.role ?? "viewer"}</Badge>
          </div>
          <div className="grid gap-4">{children}</div>
        </main>
      </div>
    </div>
  );
}
