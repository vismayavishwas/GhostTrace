from collections import deque
from typing import List, Optional
from app.models.telemetry import TelemetryEvent


class SequenceBuffer:
    """
    Sliding window buffer holding recent TelemetryEvent instances.
    Provides fast lookup for incremental pattern matching.
    """
    def __init__(self, window_size: int = 50):
        if window_size <= 0:
            raise ValueError("window_size must be a positive integer.")
        self._window_size: int = window_size
        self._buffer: deque[TelemetryEvent] = deque(maxlen=window_size)
        self._event_map: dict[str, TelemetryEvent] = {}

    @property
    def window_size(self) -> int:
        return self._window_size

    def add_event(self, event: TelemetryEvent) -> None:
        """Adds a telemetry event to the sliding window."""
        if len(self._buffer) == self._window_size:
            oldest = self._buffer[0]
            self._event_map.pop(oldest.event_id, None)
            
        self._buffer.append(event)
        self._event_map[event.event_id] = event

    def get_window(self) -> List[TelemetryEvent]:
        """Returns all events currently in the sliding window."""
        return list(self._buffer)

    def get_event(self, event_id: str) -> Optional[TelemetryEvent]:
        """Retrieves an event by its unique ID from the active window map."""
        return self._event_map.get(event_id)

    def clear(self) -> None:
        """Clears the sliding buffer."""
        self._buffer.clear()
        self._event_map.clear()


    def size(self) -> int:
        """Returns the number of events in the buffer."""
        return len(self._buffer)
