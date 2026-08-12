import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { InteractiveSandboxApp } from "../InteractiveSandboxApp";

vi.mock("@/lib/api", () => ({
  postTelemetryEvent: vi.fn().mockResolvedValue({ status: "SUCCESS" }),
  fetchGraphState: vi.fn().mockResolvedValue({ field_mappings: [] }),
  resetTelemetryState: vi.fn().mockResolvedValue({ status: "SUCCESS" }),
}));

describe("InteractiveSandboxApp Component", () => {
  it("renders sandbox application header and default Finance domain fields", () => {
    render(<InteractiveSandboxApp />);

    expect(screen.getByText("💳 Finance")).toBeInTheDocument();
    expect(screen.getByText("👥 HR / ATS")).toBeInTheDocument();
    expect(screen.getByText("📈 Sales / CRM")).toBeInTheDocument();

    expect(screen.getByText("PDF INVOICE SOURCE")).toBeInTheDocument();
    expect(screen.getByText("SAP ERP FINANCIALS")).toBeInTheDocument();
  });

  it("switches domain tabs cleanly to HR Onboarding", async () => {
    render(<InteractiveSandboxApp />);

    const hrBtn = screen.getByText("👥 HR / ATS");
    fireEvent.click(hrBtn);

    await waitFor(() => {
      expect(screen.getByText("CANDIDATE RESUME PDF")).toBeInTheDocument();
      expect(screen.getByText("WORKDAY ATS PORTAL")).toBeInTheDocument();
    });
  });

  it("switches domain tabs cleanly to Sales CRM", async () => {
    render(<InteractiveSandboxApp />);

    const salesBtn = screen.getByText("📈 Sales / CRM");
    fireEvent.click(salesBtn);

    await waitFor(() => {
      expect(screen.getByText("EXCEL LEADS SPREADSHEET")).toBeInTheDocument();
      expect(screen.getByText("SALESFORCE CRM PORTAL")).toBeInTheDocument();
    });
  });
});
