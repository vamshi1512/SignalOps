import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuth } from "@/auth/auth-provider";
import { api } from "@/lib/api";

export function useOverviewQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["overview"],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.overview(session!.access_token),
  });
}

export function useUsersQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["users"],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.users(session!.access_token),
  });
}

export function useServicesQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["services"],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.services(session!.access_token),
  });
}

export function useIncidentsQuery(params: URLSearchParams) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["incidents", params.toString()],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.incidents(session!.access_token, params),
  });
}

export function useIncidentQuery(incidentId: string | null) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["incident", incidentId],
    enabled: Boolean(session?.access_token && incidentId),
    queryFn: () => api.incident(session!.access_token, incidentId!),
  });
}

export function useLogsQuery(params: URLSearchParams) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["logs", params.toString()],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.logs(session!.access_token, params),
  });
}

export function useAlertsQuery(params: URLSearchParams) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["alerts", params.toString()],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.alerts(session!.access_token, params),
  });
}

export function useRulesQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["rules"],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.rules(session!.access_token),
  });
}

export function useAuditQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["audit"],
    enabled: Boolean(session?.access_token),
    queryFn: () => api.audit(session!.access_token),
  });
}

function invalidateConsoleState(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ["overview"] });
  queryClient.invalidateQueries({ queryKey: ["incidents"] });
  queryClient.invalidateQueries({ queryKey: ["alerts"] });
  queryClient.invalidateQueries({ queryKey: ["logs"] });
  queryClient.invalidateQueries({ queryKey: ["services"] });
  queryClient.invalidateQueries({ queryKey: ["audit"] });
}

export function useUpdateIncidentMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ incidentId, payload }: { incidentId: string; payload: Record<string, unknown> }) =>
      api.updateIncident(session!.access_token, incidentId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["incident", variables.incidentId] });
      invalidateConsoleState(queryClient);
    },
  });
}

export function useAddIncidentNoteMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ incidentId, content }: { incidentId: string; content: string }) =>
      api.addIncidentNote(session!.access_token, incidentId, content),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["incident", variables.incidentId] });
      invalidateConsoleState(queryClient);
    },
  });
}

export function useAcknowledgeAlertMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (alertId: string) => api.acknowledgeAlert(session!.access_token, alertId),
    onSuccess: () => invalidateConsoleState(queryClient),
  });
}

export function useSuppressAlertMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ alertId, minutes }: { alertId: string; minutes: number }) =>
      api.suppressAlert(session!.access_token, alertId, minutes),
    onSuccess: () => invalidateConsoleState(queryClient),
  });
}

export function useCreateServiceMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.createService(session!.access_token, payload),
    onSuccess: () => invalidateConsoleState(queryClient),
  });
}

export function useCreateRuleMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.createRule(session!.access_token, payload),
    onSuccess: () => invalidateConsoleState(queryClient),
  });
}

