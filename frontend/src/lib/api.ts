// GhostTrace AI REST API Client Service

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export async function fetchHealthCheck() {
  try {
    const res = await fetch(`http://127.0.0.1:8000/health`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchTelemetryEvents() {
  try {
    const res = await fetch(`${API_BASE_URL}/telemetry/events`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function postTelemetryEvent(eventData: any) {
  try {
    const res = await fetch(`${API_BASE_URL}/telemetry/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(eventData),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchWorkflows() {
  try {
    const res = await fetch(`${API_BASE_URL}/workflows`);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function fetchGraphState() {
  try {
    const res = await fetch(`${API_BASE_URL}/state`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function triggerGraphExecution(initialState?: any) {
  try {
    const res = await fetch(`${API_BASE_URL}/state/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(initialState || {}),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function resetTelemetryState() {
  try {
    const res = await fetch(`${API_BASE_URL}/telemetry/reset`, {
      method: "POST",
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function refineCandidate(candidateId: string, choice: "EXCLUDE" | "INCLUDE", targetSelector?: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/state/refine`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ choice, target_selector: targetSelector || "#help-btn" }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}


