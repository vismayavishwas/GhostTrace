from collections import deque
from threading import Lock
from typing import List, Optional
from app.models.telemetry import TelemetryEvent


class TelemetryBuffer:
    """
    Thread-safe, bounded ring buffer for storing validated TelemetryEvent objects.
    """
    def __init__(self, capacity: int = 1000):
        if capacity <= 0:
            raise ValueError("Buffer capacity must be a positive integer.")
        self._capacity: int = capacity
        self._buffer: deque[TelemetryEvent] = deque(maxlen=capacity)
        self._lock: Lock = Lock()

    @property
    def capacity(self) -> int:
        return self._capacity

    def append(self, event: TelemetryEvent) -> None:
        """Appends a validated TelemetryEvent to the ring buffer."""
        with self._lock:
            self._buffer.append(event)

    def get_recent(self, n: Optional[int] = None) -> List[TelemetryEvent]:
        """
        Retrieves the last n events from the buffer (or all if n is None).
        Returns events ordered from oldest to newest.
        """
        with self._lock:
            if n is None or n >= len(self._buffer):
                return list(self._buffer)
            return list(self._buffer)[-n:]

    def clear(self) -> None:
        """Clears all events from the buffer."""
        with self._lock:
            self._buffer.clear()

    def size(self) -> int:
        """Returns the current number of events stored in the buffer."""
        with self._lock:
            return len(self._buffer)

    def is_full(self) -> bool:
        """Returns True if the buffer has reached maximum capacity."""
        with self._lock:
            return len(self._buffer) == self._capacity
