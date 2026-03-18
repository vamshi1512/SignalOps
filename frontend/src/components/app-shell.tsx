import {
  Activity,
  AlertTriangle,
  Box,
  LayoutDashboard,
  LogOut,
  RadioTower,
  Siren,
  TerminalSquare,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/incidents", label: "Incidents", icon: Siren },
  { to: "/logs", label: "Logs", icon: TerminalSquare },
  { to: "/alerts", label: "Alerts", icon: AlertTriangle },
  { to: "/services", label: "Services", icon: Box },
  { to: "/activity", label: "Activity", icon: Activity },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { session, logout } = useAuth();

  return (
    <div className="relative min-h-screen">
      <div className="pointer-events-none absolute inset-0 grid-fade opacity-30" />
      <div className="relative mx-auto flex min-h-screen max-w-[1600px] flex-col gap-4 px-4 py-4 lg:flex-row lg:px-6">
        <aside className="surface-panel-elevated flex flex-col gap-6 p-5 lg:min-h-[calc(100vh-2rem)] lg:w-[280px]">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-emerald-400 text-slate-950 shadow-glow">
                <RadioTower className="h-6 w-6" />
              </div>
              <div>
                <div className="font-display text-xl text-white">SignalOps</div>
                <div className="text-sm text-muted-foreground">Cloud reliability console</div>
              </div>
            </div>
            <div className="rounded-3xl border border-cyan-400/15 bg-cyan-400/10 p-4">
              <Badge className="border-cyan-400/20 bg-cyan-400/10 text-cyan-200">Live posture</Badge>
              <p className="mt-3 text-sm text-cyan-50/90">
                Synthetic demo traffic is tuned for high-signal SRE workflows and incident review loops.
              </p>
            </div>
          </div>

          <nav className="grid gap-2">
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition",
                    isActive ? "bg-white/10 text-white" : "text-muted-foreground hover:bg-white/5 hover:text-white",
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto space-y-4 rounded-3xl border border-white/10 bg-white/[0.04] p-4">
            <div>
              <div className="text-sm text-muted-foreground">Signed in as</div>
              <div className="mt-1 font-medium text-white">{session?.user.full_name}</div>
              <div className="text-sm text-muted-foreground">{session?.user.email}</div>
            </div>
            <div className="flex items-center justify-between">
              <Badge>{session?.user.role ?? "viewer"}</Badge>
              <Button variant="ghost" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            </div>
          </div>
        </aside>

        <main className="flex-1 pb-8">
          <div className="mb-4 flex items-center justify-between gap-4 rounded-[28px] border border-white/10 bg-white/[0.04] px-5 py-4 lg:hidden">
            <div>
              <div className="font-display text-xl text-white">SignalOps</div>
              <div className="text-sm text-muted-foreground">Operations console</div>
            </div>
            <Badge>{session?.user.role ?? "viewer"}</Badge>
          </div>
          <div className="grid gap-4">{children}</div>
        </main>
      </div>
    </div>
  );
}

