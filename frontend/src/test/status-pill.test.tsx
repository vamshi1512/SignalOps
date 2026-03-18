import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusPill } from "@/components/status-pill";

describe("StatusPill", () => {
  it("renders the provided value", () => {
    render(<StatusPill value="critical" />);
    expect(screen.getByText("critical")).toBeInTheDocument();
  });
});

