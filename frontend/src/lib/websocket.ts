// GhostTrace AI Specialized WebSocket Stream Manager

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/ws";

export type StreamType = "telemetry" | "reasoning" | "replay" | "state" | "pipeline";

export class WebSocketStreamManager {
  private socket: WebSocket | null = null;
  private streamType: StreamType;
  private onMessageCallback: (data: any) => void;
  private onStatusChangeCallback?: (isConnected: boolean) => void;

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
    try {
      const url = `${WS_BASE_URL}/${this.streamType}`;
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        if (this.onStatusChangeCallback) this.onStatusChangeCallback(true);
      };

      this.socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.onMessageCallback(parsed);
        } catch {
          // Parse error ignore
        }
      };

      this.socket.onclose = () => {
        if (this.onStatusChangeCallback) this.onStatusChangeCallback(false);
      };

      this.socket.onerror = () => {
        if (this.onStatusChangeCallback) this.onStatusChangeCallback(false);
      };
    } catch {
      if (this.onStatusChangeCallback) this.onStatusChangeCallback(false);
    }
  }

  public send(payload: any) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload));
    }
  }

  public close() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
