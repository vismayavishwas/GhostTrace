import logging
from collections import deque
from typing import List, Optional, Deque
from app.models.telemetry import TelemetryEvent
from app.agents.observer.publisher import TelemetryPublisher
from app.agents.continuous_observer.models import ObservationEvent

logger = logging.getLogger("ghosttrace.continuous_observer.consumer")


class TelemetryConsumer:
    """
    Independent, read-only telemetry consumer that subscribes directly to TelemetryPublisher.
    Maintains a bounded window of ObservationEvents without mutating telemetry data or creating coupled pipelines.
    """
    def __init__(
        self,
        publisher: Optional[TelemetryPublisher] = None,
        max_buffer_size: int = 200
    ):
        self.max_buffer_size = max_buffer_size
        self._buffer: Deque[ObservationEvent] = deque(maxlen=max_buffer_size)

        if publisher:
            publisher.subscribe(self.on_telemetry_event)
            logger.info("TelemetryConsumer subscribed independently to TelemetryPublisher")

    def on_telemetry_event(self, event: TelemetryEvent) -> ObservationEvent:
        """Callback executed upon receiving a TelemetryEvent from TelemetryPublisher."""
        obs = ObservationEvent(
            telemetry_event=event,
            app_title=event.app_title or "Unknown Application",
            latency_ms=0.0,
            success_signal=True
        )
        self._buffer.append(obs)
        logger.debug(f"TelemetryConsumer ingested event ID={event.event_id[:8]} Type={event.event_type}")
        return obs

    def ingest_event(self, event: TelemetryEvent, success: bool = True, latency_ms: float = 0.0) -> ObservationEvent:
        """Direct ingestion method for adapter / unit testing."""
        obs = ObservationEvent(
            telemetry_event=event,
            app_title=event.app_title or "Unknown Application",
            latency_ms=latency_ms,
            success_signal=success
        )
        self._buffer.append(obs)
        return obs

    def get_recent_observations(self) -> List[ObservationEvent]:
        """Returns snapshot of current observation buffer."""
        return list(self._buffer)

    def buffer_count(self) -> int:
        """Returns number of observations in buffer."""
        return len(self._buffer)
