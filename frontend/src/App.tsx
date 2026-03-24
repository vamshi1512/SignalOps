import { Suspense, lazy } from "react";
import { Route, Routes } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { AppShell } from "@/components/app-shell";
import { Skeleton } from "@/components/ui/skeleton";
import { LoginPage } from "@/pages/login-page";

const DashboardPage = lazy(() => import("@/pages/dashboard-page").then((module) => ({ default: module.DashboardPage })));
const SuitesPage = lazy(() => import("@/pages/suites-page").then((module) => ({ default: module.SuitesPage })));
const RunsPage = lazy(() => import("@/pages/runs-page").then((module) => ({ default: module.RunsPage })));
const EnvironmentsPage = lazy(() => import("@/pages/environments-page").then((module) => ({ default: module.EnvironmentsPage })));
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
          <Route path="/suites" element={<SuitesPage />} />
          <Route path="/runs" element={<RunsPage />} />
          <Route path="/environments" element={<EnvironmentsPage />} />
          <Route path="/activity" element={<ActivityPage />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}
