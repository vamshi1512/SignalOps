import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EmptyState, ErrorState, LoadingState, RetryButton } from "@/components/data-state";

describe("data state components", () => {
  it("renders loading state copy", () => {
    render(<LoadingState title="Loading telemetry" description="Syncing fleet state" />);
    expect(screen.getByText("Loading telemetry")).toBeInTheDocument();
    expect(screen.getByText("Syncing fleet state")).toBeInTheDocument();
  });

  it("renders empty and error state actions", async () => {
    const onRetry = vi.fn();
    render(
      <>
        <EmptyState title="No robots" description="Nothing to inspect." action={<RetryButton onRetry={onRetry}>Reload</RetryButton>} />
        <ErrorState title="Load failed" description="Try again." action={<RetryButton onRetry={onRetry} />} />
      </>,
    );

    expect(screen.getByText("No robots")).toBeInTheDocument();
    expect(screen.getByText("Load failed")).toBeInTheDocument();
    expect(screen.getAllByRole("button")).toHaveLength(2);
  });
});
