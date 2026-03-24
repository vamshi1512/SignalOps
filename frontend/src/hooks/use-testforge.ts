import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuth } from "@/auth/auth-provider";
import { api } from "@/lib/api";

function useToken() {
  return useAuth().session?.access_token ?? "";
}

function baseQueryOptions(token: string) {
  return {
    enabled: Boolean(token),
    staleTime: 30_000,
    retry: 1,
  } as const;
}

export function useOverviewQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["overview"],
    ...baseQueryOptions(token),
    queryFn: () => api.overview(token),
  });
}

export function useUsersQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["users"],
    ...baseQueryOptions(token),
    queryFn: () => api.users(token),
  });
}

export function useProjectsQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["projects"],
    ...baseQueryOptions(token),
    queryFn: () => api.projects(token),
  });
}

export function useEnvironmentsQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["environments"],
    ...baseQueryOptions(token),
    queryFn: () => api.environments(token),
  });
}

export function useFixturesQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["fixtures"],
    ...baseQueryOptions(token),
    queryFn: () => api.fixtures(token),
  });
}

export function useSuitesQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["suites"],
    ...baseQueryOptions(token),
    queryFn: () => api.suites(token),
  });
}

export function useSchedulesQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["schedules"],
    ...baseQueryOptions(token),
    queryFn: () => api.schedules(token),
  });
}

export function useRunsQuery(params: URLSearchParams) {
  const token = useToken();
  return useQuery({
    queryKey: ["runs", params.toString()],
    ...baseQueryOptions(token),
    placeholderData: keepPreviousData,
    queryFn: () => api.runs(token, params),
  });
}

export function useRunQuery(runId: string | null) {
  const token = useToken();
  return useQuery({
    queryKey: ["run", runId],
    ...baseQueryOptions(token),
    enabled: Boolean(token && runId),
    queryFn: () => api.run(token, runId!),
  });
}

export function useNotificationsQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["notifications"],
    ...baseQueryOptions(token),
    queryFn: () => api.notifications(token),
  });
}

export function useAuditQuery() {
  const token = useToken();
  return useQuery({
    queryKey: ["audit"],
    ...baseQueryOptions(token),
    queryFn: () => api.audit(token),
  });
}

function invalidateDashboard(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ["overview"] });
  queryClient.invalidateQueries({ queryKey: ["suites"] });
  queryClient.invalidateQueries({ queryKey: ["runs"] });
  queryClient.invalidateQueries({ queryKey: ["notifications"] });
  queryClient.invalidateQueries({ queryKey: ["schedules"] });
  queryClient.invalidateQueries({ queryKey: ["environments"] });
  queryClient.invalidateQueries({ queryKey: ["audit"] });
}

export function useLaunchSuiteRunMutation() {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ suiteId, payload }: { suiteId: string; payload: Record<string, unknown> }) =>
      api.launchSuiteRun(token, suiteId, payload),
    onSuccess: () => {
      invalidateDashboard(queryClient);
      queryClient.invalidateQueries({ queryKey: ["run"] });
    },
  });
}

export function useUpdateScheduleMutation() {
  const token = useToken();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ scheduleId, payload }: { scheduleId: string; payload: Record<string, unknown> }) =>
      api.updateSchedule(token, scheduleId, payload),
    onSuccess: () => invalidateDashboard(queryClient),
  });
}
