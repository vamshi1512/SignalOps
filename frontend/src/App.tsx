import { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { AppShell } from "@/components/app-shell";
import { Skeleton } from "@/components/ui/skeleton";
import { LoginPage } from "@/pages/login-page";

const DashboardPage = lazy(() => import("@/pages/dashboard-page").then((module) => ({ default: module.DashboardPage })));
const IncidentsPage = lazy(() => import("@/pages/incidents-page").then((module) => ({ default: module.IncidentsPage })));
const LogsPage = lazy(() => import("@/pages/logs-page").then((module) => ({ default: module.LogsPage })));
const AlertsPage = lazy(() => import("@/pages/alerts-page").then((module) => ({ default: module.AlertsPage })));
const ServicesPage = lazy(() => import("@/pages/services-page").then((module) => ({ default: module.ServicesPage })));
const ActivityPage = lazy(() => import("@/pages/activity-page").then((module) => ({ default: module.ActivityPage })));

export function App() {
  const { hydrated, session } = useAuth();

  if (!hydrated) {
    return (
      <div className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6">
        <div className="grid w-full gap-4 md:grid-cols-3">
          <Skeleton className="h-52" />
          <Skeleton className="h-52" />
          <Skeleton className="h-52" />
        </div>
      </div>
    );
  }

  if (!session) {
    return <LoginPage />;
  }

  return (
    <AppShell>
      <Suspense fallback={<Skeleton className="h-[420px]" />}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/logs" element={<LogsPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/activity" element={<ActivityPage />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}
