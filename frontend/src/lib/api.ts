// GhostTrace AI REST API Client Service

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://ghosttrace-bcp2.onrender.com/api/v1";

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 5000): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function fetchHealthCheck() {
  try {
    const rootUrl = API_BASE_URL.replace(/\/api\/v1\/?$/, "");
    const res = await fetchWithTimeout(`${rootUrl}/health`, {}, 4000);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchTelemetryEvents() {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/telemetry/events`, {}, 4000);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function postTelemetryEvent(eventData: any) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/telemetry/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(eventData),
    }, 4000);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function fetchWorkflows() {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/workflows`, {}, 4000);
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

export async function fetchGraphState() {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/state`, {}, 4000);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function triggerGraphExecution(initialState?: any) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/state/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(initialState || {}),
    }, 6000);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function resetTelemetryState() {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/telemetry/reset`, {
      method: "POST",
    }, 5000);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function refineCandidate(candidateId: string, choice: "EXCLUDE" | "INCLUDE", targetSelector?: string) {
  try {
    const res = await fetchWithTimeout(`${API_BASE_URL}/state/refine`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ choice, target_selector: targetSelector || "#help-btn" }),
    }, 5000);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}


