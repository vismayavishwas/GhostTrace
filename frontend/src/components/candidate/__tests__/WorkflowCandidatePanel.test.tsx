import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { WorkflowCandidatePanel } from "../WorkflowCandidatePanel";

vi.mock("@/lib/api", () => ({
  refineCandidate: vi.fn().mockResolvedValue({
    status: "SUCCESS",
    version: 2,
    new_confidence: 0.95,
    previous_confidence: 0.80,
  }),
}));

describe("WorkflowCandidatePanel Component", () => {
  it("renders candidate name and learning confidence score", () => {
    render(
      <WorkflowCandidatePanel
        candidateName="Finance Invoice Workflow"
        confidenceScore={0.88}
        onAnalyzeTrigger={() => {}}
      />
    );

    expect(screen.getByText("Finance Invoice Workflow")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
  });

  it("renders clean deterministic banner when 0 outliers exist", () => {
    render(
      <WorkflowCandidatePanel
        confidenceScore={0.92}
        outliers={[]}
        onAnalyzeTrigger={() => {}}
      />
    );

    expect(
      screen.getByText("Clean 100% Deterministic Workflow Stream")
    ).toBeInTheDocument();
  });

  it("renders outlier review panel and batch action buttons when outliers exist", () => {
    const outliers = [
      {
        id: "outlier-1",
        label: "Copy Amount",
        selector: "#target-amount",
        reason: "Destination value changed from $14,850 to $22,400",
      },
    ];

    render(
      <WorkflowCandidatePanel
        outliers={outliers}
        onAnalyzeTrigger={() => {}}
      />
    );

    expect(screen.getByText("Semantic Deviation Observed")).toBeInTheDocument();
    expect(screen.getByText("Exclude from Workflow")).toBeInTheDocument();
    expect(screen.getByText("Include in Workflow")).toBeInTheDocument();
  });
});
