const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "wss://ghosttrace-bcp2.onrender.com/ws";

export type StreamType = "telemetry" | "reasoning" | "replay" | "state" | "pipeline";

export class WebSocketStreamManager {
  private socket: WebSocket | null = null;
  private streamType: StreamType;
  private onMessageCallback: (data: any) => void;
  private onStatusChangeCallback?: (isConnected: boolean) => void;

  private destroyed = false;
  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;

  private static readonly MAX_RECONNECT_DELAY_MS = 30000;
  private static readonly BASE_DELAY_MS = 1500;

  constructor(
    streamType: StreamType,
    onMessage: (data: any) => void,
    onStatusChange?: (isConnected: boolean) => void
  ) {
    this.streamType = streamType;
    this.onMessageCallback = onMessage;
    this.onStatusChangeCallback = onStatusChange;
    this.connect();
  }

  public connect() {
    if (this.destroyed) return;

    try {
      const url = `${WS_BASE_URL}/${this.streamType}`;
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.reconnectAttempt = 0;
        if (this.onStatusChangeCallback) this.onStatusChangeCallback(true);
        this.startPing();
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.onMessageCallback(parsed);
        } catch {
          // Parse error — ignore
        }
      };

      this.socket.onclose = () => {
        this.stopPing();
        if (this.onStatusChangeCallback) this.onStatusChangeCallback(false);
        this.scheduleReconnect();
      };

      this.socket.onerror = () => {
        this.stopPing();
        if (this.onStatusChangeCallback) this.onStatusChangeCallback(false);
        // onclose fires after onerror so reconnect handled there
      };
    } catch {
      if (this.onStatusChangeCallback) this.onStatusChangeCallback(false);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.destroyed) return;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);

    const delay = Math.min(
      WebSocketStreamManager.BASE_DELAY_MS * Math.pow(1.8, this.reconnectAttempt),
      WebSocketStreamManager.MAX_RECONNECT_DELAY_MS
    );
    this.reconnectAttempt++;

    this.reconnectTimer = setTimeout(() => {
      if (!this.destroyed) this.connect();
    }, delay);
  }

  private startPing() {
    this.stopPing();
    // Send a ping every 20s to keep the WS alive through Render's idle timeout
    this.pingTimer = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        try { this.socket.send(JSON.stringify({ type: "PING" })); } catch { /* ignore */ }
      }
    }, 20000);
  }

  private stopPing() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  public send(payload: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  public close() {
    this.destroyed = true;
    this.stopPing();
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

/**
 * Keeps the Render backend warm by pinging /health every 9 minutes.
 * Render free tier sleeps after ~15 min of inactivity — this prevents cold starts.
 */
export function startBackendKeepAlive() {
  const rootUrl = (process.env.NEXT_PUBLIC_API_URL || "https://ghosttrace-bcp2.onrender.com/api/v1")
    .replace(/\/api\/v1\/?$/, "");

  const ping = () => {
    fetch(`${rootUrl}/health`, { method: "GET" }).catch(() => {});
  };

  ping(); // Immediate ping on mount
  return setInterval(ping, 9 * 60 * 1000); // Every 9 minutes
}
