import inspect
import logging
from typing import Callable, List, Union, Awaitable, Any
from app.models.telemetry import TelemetryEvent

logger = logging.getLogger("ghosttrace.observer.publisher")

# Subscriber callback type (sync or async function accepting TelemetryEvent)
SubscriberCallback = Callable[[TelemetryEvent], Any]


class TelemetryPublisher:
    """
    Internal event publisher distributing validated TelemetryEvent objects to subscribers.
    """
    def __init__(self):
        self._subscribers: List[SubscriberCallback] = []

    def subscribe(self, callback: SubscriberCallback) -> None:
        """Registers a callback function to receive published TelemetryEvents."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered telemetry subscriber: {callback.__name__}")

    def unsubscribe(self, callback: SubscriberCallback) -> None:
        """Unregisters a subscriber callback."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered telemetry subscriber: {callback.__name__}")

    async def publish(self, event: TelemetryEvent) -> None:
        """
        Publishes a validated TelemetryEvent to all registered subscribers.
        Handles both sync and async subscriber callbacks safely.
        """
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns active subscriber count."""
        return len(self._subscribers)
