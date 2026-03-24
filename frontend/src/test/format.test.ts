import { describe, expect, it } from "vitest";

import { formatDelta, formatDurationMs, formatMetric, formatRelative } from "@/lib/format";

describe("format helpers", () => {
  it("formats metric percentages", () => {
    expect(formatMetric(12.345, "%")).toBe("12.3%");
  });

  it("formats positive deltas with sign", () => {
    expect(formatDelta(4.2, "%")).toBe("+4.2%");
  });

  it("formats missing relative timestamps", () => {
    expect(formatRelative(null)).toBe("Not yet");
  });

  it("formats durations in minutes when needed", () => {
    expect(formatDurationMs(120000)).toBe("2.0m");
  });
});
