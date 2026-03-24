import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusPill } from "@/components/status-pill";

describe("StatusPill", () => {
  it("renders the provided value", () => {
    render(<StatusPill value="queued" />);
    expect(screen.getByText("queued")).toBeInTheDocument();
  });

  it("formats underscored values for display", () => {
    render(<StatusPill value="prod_like" />);
    expect(screen.getByText("prod like")).toBeInTheDocument();
  });
});
