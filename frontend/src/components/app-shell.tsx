import {
  Activity,
  FolderKanban,
  LayoutDashboard,
  LogOut,
  MoonStar,
  Orbit,
  PlaySquare,
  RadioTower,
  SunMedium,
} from "lucide-react";
import { type ReactNode, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navigation = [
  { to: "/", label: "Overview", icon: LayoutDashboard },
  { to: "/suites", label: "Suites", icon: FolderKanban },
  { to: "/runs", label: "Runs", icon: PlaySquare },
  { to: "/environments", label: "Environments", icon: Orbit },
  { to: "/activity", label: "Activity", icon: Activity },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { session, logout } = useAuth();
  const [theme, setTheme] = useState<"dark" | "light">(
    () => {
      const storedTheme = localStorage.getItem("testforge-theme");
      if (storedTheme === "light" || storedTheme === "dark") {
        return storedTheme;
      }
      if (typeof window !== "undefined" && "matchMedia" in window && window.matchMedia("(prefers-color-scheme: light)").matches) {
        return "light";
      }
      return "dark";
    },
  );

  useEffect(() => {
    document.documentElement.classList.toggle("light", theme === "light");
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("testforge-theme", theme);
  }, [theme]);

  return (
    <div className="relative min-h-screen">
      <div className="pointer-events-none absolute inset-0 grid-fade opacity-30" />
      <div className="relative mx-auto flex min-h-screen max-w-[1600px] flex-col gap-4 px-4 py-4 lg:flex-row lg:px-6">
        <aside className="surface-panel-elevated flex flex-col gap-6 p-5 lg:min-h-[calc(100vh-2rem)] lg:w-[280px]">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-400 via-cyan-300 to-orange-300 text-slate-950 shadow-glow">
                <RadioTower className="h-6 w-6" />
              </div>
              <div>
                <div className="font-display text-xl text-foreground">TestForge</div>
                <div className="text-sm text-muted-foreground">QA orchestration platform</div>
              </div>
            </div>
            <div className="rounded-3xl border border-primary/20 bg-primary/10 p-4">
              <Badge className="border-primary/20 bg-primary/10 text-primary">Execution fabric</Badge>
              <p className="mt-3 text-sm text-foreground/80">
                Seeded suites, deterministic history, and scheduled runs make the dashboard demo-ready from first boot.
              </p>
            </div>
            <div className="grid gap-3 rounded-3xl border border-border/80 bg-background/25 p-4">
              <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Workspace posture</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-border bg-card/65 px-3 py-3">
                  <div className="text-xs text-muted-foreground">Mode</div>
                  <div className="mt-1 font-medium text-foreground">Demo seeded</div>
                </div>
                <div className="rounded-2xl border border-border bg-card/65 px-3 py-3">
                  <div className="text-xs text-muted-foreground">Theme</div>
                  <div className="mt-1 font-medium text-foreground">{theme}</div>
                </div>
              </div>
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
                    isActive ? "bg-secondary text-foreground" : "text-muted-foreground hover:bg-secondary/70 hover:text-foreground",
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto space-y-4 rounded-3xl border border-border bg-background/25 p-4">
            <div>
              <div className="text-sm text-muted-foreground">Signed in as</div>
              <div className="mt-1 font-medium text-foreground">{session?.user.full_name}</div>
              <div className="text-sm text-muted-foreground">{session?.user.email}</div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              >
                {theme === "dark" ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
                {theme === "dark" ? "Light" : "Dark"} mode
              </Button>
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
          <div className="mb-4 flex items-center justify-between gap-4 rounded-[28px] border border-border bg-card/85 px-5 py-4 lg:hidden">
            <div>
              <div className="font-display text-xl text-foreground">TestForge</div>
              <div className="text-sm text-muted-foreground">Execution console</div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
                {theme === "dark" ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
              </Button>
              <Badge>{session?.user.role ?? "viewer"}</Badge>
            </div>
          </div>
          <div className="grid gap-4">{children}</div>
        </main>
      </div>
    </div>
  );
}
