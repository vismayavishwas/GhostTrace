import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  fetchHealthCheck,
  fetchTelemetryEvents,
  postTelemetryEvent,
  fetchWorkflows,
  fetchGraphState,
  triggerGraphExecution,
  resetTelemetryState,
  refineCandidate,
} from "../api";

global.fetch = vi.fn();

describe("REST API Client Service (api.ts)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetchHealthCheck returns json data on success", async () => {
    const mockData = { status: "healthy", service: "GhostTrace AI" };
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const res = await fetchHealthCheck();
    expect(res).toEqual(mockData);
  });

  it("fetchTelemetryEvents returns array of events on success", async () => {
    const mockEvents = [{ event_id: "evt-1", event_type: "PASTE" }];
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockEvents,
    });

    const res = await fetchTelemetryEvents();
    expect(res).toEqual(mockEvents);
  });

  it("postTelemetryEvent posts event data successfully", async () => {
    const mockResponse = { status: "SUCCESS", event_id: "evt-123" };
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const res = await postTelemetryEvent({ event_type: "COPY" });
    expect(res).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/telemetry/events"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("resetTelemetryState calls reset endpoint", async () => {
    const mockResponse = { status: "SUCCESS", message: "Shadow Mode state reset" };
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const res = await resetTelemetryState();
    expect(res).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/telemetry/reset"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("refineCandidate posts refinement decision", async () => {
    const mockResponse = { status: "SUCCESS", choice: "EXCLUDE" };
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const res = await refineCandidate("cand-1", "EXCLUDE", "#selector");
    expect(res).toEqual(mockResponse);
  });
});
