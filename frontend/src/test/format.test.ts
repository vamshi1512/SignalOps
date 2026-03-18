import { describe, expect, it } from "vitest";

import { formatDelta, formatMetric } from "@/lib/format";

describe("format helpers", () => {
  it("formats metric percentages", () => {
    expect(formatMetric(12.345, "%")).toBe("12.3%");
  });

  it("formats positive deltas with sign", () => {
    expect(formatDelta(4.2, "%")).toBe("+4.2%");
  });
});

