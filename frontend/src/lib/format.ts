import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

export function formatMetric(value: number, suffix = "") {
  if (suffix.trim() === "%") {
    return `${value.toFixed(1)}%`;
  }
  if (suffix.trim() === "sqm") {
    return `${new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value)} sqm`;
  }
  if (suffix.trim() === "min") {
    return `${value.toFixed(1)} min`;
  }
  return `${new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value)}${suffix}`;
}

export function formatDelta(value: number, suffix = "") {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}${suffix}`;
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "n/a";
  }
  return dayjs(value).format("MMM D, HH:mm");
}

export function formatRelative(value: string | null | undefined) {
  if (!value) {
    return "n/a";
  }
  return dayjs(value).fromNow();
}

export function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}

export function formatBattery(value: number) {
  return `${value.toFixed(0)}%`;
}

export function formatDistance(value: number) {
  return value >= 1000 ? `${(value / 1000).toFixed(1)} km` : `${value.toFixed(0)} m`;
}
