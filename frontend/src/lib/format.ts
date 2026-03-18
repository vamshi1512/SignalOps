import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

export function formatMetric(value: number, suffix = "") {
  if (suffix === "%") {
    return `${value.toFixed(1)}%`;
  }
  if (suffix === "h") {
    return `${value.toFixed(1)}h`;
  }
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
}

export function formatDelta(value: number, suffix = "") {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}${suffix}`;
}

export function formatDateTime(value: string) {
  return dayjs(value).format("MMM D, HH:mm");
}

export function formatRelative(value: string) {
  return dayjs(value).fromNow();
}

