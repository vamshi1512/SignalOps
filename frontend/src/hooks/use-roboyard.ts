import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuth } from "@/auth/auth-provider";
import { api } from "@/lib/api";
import type { DashboardOverview, ListResponse, LiveFleetMessage, Robot } from "@/types/api";

function requireToken(token: string | undefined) {
  if (!token) {
    throw new Error("Session token missing");
  }
  return token;
}

function mergeRobots<T extends { id: string }>(current: T[], incoming: T[]) {
  const next = new Map(current.map((item) => [item.id, item]));
  incoming.forEach((item) => next.set(item.id, item));
  return Array.from(next.values());
}

export function useOverviewQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["overview"],
    queryFn: () => api.overview(requireToken(session?.access_token)),
    enabled: Boolean(session?.access_token),
    refetchInterval: 30_000,
  });
}

export function useZonesQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["zones"],
    queryFn: () => api.zones(requireToken(session?.access_token)),
    enabled: Boolean(session?.access_token),
  });
}

export function useRobotsQuery(filters?: Record<string, string | number | boolean | undefined>) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["robots", filters ?? {}],
    queryFn: () => api.robots(requireToken(session?.access_token), filters),
    enabled: Boolean(session?.access_token),
  });
}

export function useRobotQuery(robotId?: string) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["robot", robotId],
    queryFn: () => api.robot(requireToken(session?.access_token), robotId ?? ""),
    enabled: Boolean(session?.access_token && robotId),
  });
}

export function useMissionsQuery(filters?: Record<string, string | number | boolean | undefined>) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["missions", filters ?? {}],
    queryFn: () => api.missions(requireToken(session?.access_token), filters),
    enabled: Boolean(session?.access_token),
  });
}

export function useAlertsQuery(filters?: Record<string, string | number | boolean | undefined>) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["alerts", filters ?? {}],
    queryFn: () => api.alerts(requireToken(session?.access_token), filters),
    enabled: Boolean(session?.access_token),
  });
}

export function useRobotHistoryQuery(robotId?: string) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["history", robotId],
    queryFn: () => api.robotHistory(requireToken(session?.access_token), robotId ?? ""),
    enabled: Boolean(session?.access_token && robotId),
  });
}

export function useMissionReplayQuery(missionId?: string) {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["replay", missionId],
    queryFn: () => api.missionReplay(requireToken(session?.access_token), missionId ?? ""),
    enabled: Boolean(session?.access_token && missionId),
  });
}

export function useConfigQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["config"],
    queryFn: () => api.config(requireToken(session?.access_token)),
    enabled: Boolean(session?.access_token),
  });
}

export function useUsersQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["users"],
    queryFn: () => api.users(requireToken(session?.access_token)),
    enabled: Boolean(session?.access_token),
  });
}

export function useAuditQuery() {
  const { session } = useAuth();
  return useQuery({
    queryKey: ["audit"],
    queryFn: () => api.audit(requireToken(session?.access_token)),
    enabled: Boolean(session?.access_token),
  });
}

export function useDemoAccountsQuery() {
  return useQuery({
    queryKey: ["demo-accounts"],
    queryFn: () => api.demoAccounts(),
  });
}

export function useCreateMissionMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.createMission(requireToken(session?.access_token), payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["missions"] });
      void queryClient.invalidateQueries({ queryKey: ["overview"] });
      void queryClient.invalidateQueries({ queryKey: ["robots"] });
    },
  });
}

export function useCommandRobotMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ robotId, command, note }: { robotId: string; command: string; note?: string }) =>
      api.commandRobot(requireToken(session?.access_token), robotId, { command, note }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["missions"] });
      void queryClient.invalidateQueries({ queryKey: ["overview"] });
      void queryClient.invalidateQueries({ queryKey: ["robots"] });
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}

export function useAcknowledgeAlertMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ alertId, notes }: { alertId: string; notes: string }) =>
      api.acknowledgeAlert(requireToken(session?.access_token), alertId, notes),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
      void queryClient.invalidateQueries({ queryKey: ["overview"] });
    },
  });
}

export function useUpdateConfigMutation() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.updateConfig(requireToken(session?.access_token), payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["config"] });
      void queryClient.invalidateQueries({ queryKey: ["overview"] });
    },
  });
}

export function useLiveFleetStream() {
  const { session } = useAuth();
  const queryClient = useQueryClient();
  const [status, setStatus] = useState<"idle" | "connecting" | "connected" | "closed">("idle");
  const [lastTick, setLastTick] = useState<string | null>(null);

  useEffect(() => {
    if (!session?.access_token) {
      return;
    }

    const socket = new WebSocket(api.websocketUrl(session.access_token));
    let heartbeat: number | undefined;

    socket.onopen = () => {
      setStatus("connected");
      heartbeat = window.setInterval(() => {
        socket.send("ping");
      }, 20_000);
    };

    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as LiveFleetMessage;
      if (payload.type !== "fleet_tick" || !payload.robots || !payload.weather) {
        return;
      }
      const robots = payload.robots;
      const weather = payload.weather;
      if (payload.timestamp) {
        setLastTick(payload.timestamp);
      }
      queryClient.setQueryData<DashboardOverview | undefined>(["overview"], (current) => {
        if (!current) {
          return current;
        }
        return {
          ...current,
          generated_at: payload.timestamp ?? current.generated_at,
          robots: mergeRobots(current.robots, robots),
          active_alerts: payload.alerts
            ? mergeRobots(current.active_alerts, payload.alerts).filter((alert) => alert.status === "open").slice(0, 8)
            : current.active_alerts,
          weather: {
            ...current.weather,
            state: weather.state,
            intensity: weather.intensity,
            updated_at: payload.timestamp ?? current.weather.updated_at,
          },
        };
      });
      queryClient.setQueriesData<ListResponse<Robot> | undefined>({ queryKey: ["robots"] }, (current) => {
        if (!current || !current.items) {
          return current;
        }
        return {
          ...current,
          items: mergeRobots(current.items, robots as Robot[]),
        };
      });
    };

    socket.onerror = () => setStatus("closed");
    socket.onclose = () => setStatus("closed");

    return () => {
      if (heartbeat) {
        window.clearInterval(heartbeat);
      }
      socket.close();
      setStatus("closed");
    };
  }, [queryClient, session?.access_token]);

  const effectiveStatus = !session?.access_token ? "idle" : status === "idle" ? "connecting" : status;
  return { status: effectiveStatus, lastTick };
}
