import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

export function formatMetric(value: number, suffix = "") {
  if (suffix === "%") {
    return `${value.toFixed(1)}%`;
  }
  if (suffix === "m") {
    return `${value.toFixed(1)}m`;
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
}

export function formatDelta(value: number, suffix = "") {
  const sign = value > 0 ? "+" : "";
  if (suffix === "%") {
    return `${sign}${value.toFixed(1)}%`;
  }
  if (suffix === "m") {
    return `${sign}${value.toFixed(1)}m`;
  }
  return `${sign}${new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value)}`;
}

export function formatDateTime(value: string) {
  return dayjs(value).format("MMM D, HH:mm");
}

export function formatRelative(value: string | null) {
  if (!value) {
    return "Not yet";
  }
  return dayjs(value).fromNow();
}

export function formatDurationMs(value: number) {
  if (value >= 60000) {
    return `${(value / 60000).toFixed(1)}m`;
  }
  return `${Math.round(value / 1000)}s`;
}

export function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}
