import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "@/auth/auth-provider";
import { AppShell } from "@/components/app-shell";
import { LoadingState } from "@/components/data-state";
import { AdminPage } from "@/pages/admin-page";
import { AlertsPage } from "@/pages/alerts-page";
import { ConsolePage } from "@/pages/console-page";
import { FleetPage } from "@/pages/fleet-page";
import { HistoryPage } from "@/pages/history-page";
import { LandingPage } from "@/pages/landing-page";
import { LoginPage } from "@/pages/login-page";
import { MissionsPage } from "@/pages/missions-page";
import type { UserRole } from "@/types/api";

function ProtectedLayout({ allowedRoles }: { allowedRoles?: UserRole[] }) {
  const { hydrated, session } = useAuth();
  if (!hydrated) {
    return (
      <div className="min-h-screen bg-background p-4">
        <LoadingState className="mx-auto mt-10 max-w-3xl" />
      </div>
    );
  }
  if (!session) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(session.user.role)) {
    return <Navigate to="/console" replace />;
  }
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

export function App() {
  const { session } = useAuth();

  return (
    <Routes>
      <Route path="/" element={session ? <Navigate to="/console" replace /> : <LandingPage />} />
      <Route path="/login" element={session ? <Navigate to="/console" replace /> : <LoginPage />} />
      <Route element={<ProtectedLayout />}>
        <Route path="/console" element={<ConsolePage />} />
        <Route path="/fleet" element={<FleetPage />} />
        <Route path="/missions" element={<MissionsPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Route>
      <Route element={<ProtectedLayout allowedRoles={["admin"]} />}>
        <Route path="/admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to={session ? "/console" : "/"} replace />} />
    </Routes>
  );
}
