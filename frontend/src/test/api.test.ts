import { describe, expect, it } from "vitest";

import { ApiError, getErrorMessage } from "@/lib/api";

describe("getErrorMessage", () => {
  it("prefers API error messages", () => {
    expect(getErrorMessage(new ApiError("Backend rejected the request", 400))).toBe("Backend rejected the request");
  });

  it("falls back for unknown values", () => {
    expect(getErrorMessage(null, "Fallback message")).toBe("Fallback message");
  });
});
