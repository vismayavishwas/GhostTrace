// GhostTrace AI Central Environment Configuration

export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_URL || "https://ghosttrace-bcp2.onrender.com/api/v1";

export const WS_BASE_URL: string =
  process.env.NEXT_PUBLIC_WS_URL || "wss://ghosttrace-bcp2.onrender.com/ws";

export const WS_TELEMETRY_URL: string =
  process.env.NEXT_PUBLIC_WS_TELEMETRY_URL || `${WS_BASE_URL}/telemetry`;

export const WS_STATE_URL: string =
  process.env.NEXT_PUBLIC_WS_STATE_URL || `${WS_BASE_URL}/state`;
