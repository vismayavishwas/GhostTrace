import inspect
import logging
from typing import Callable, List, Union, Awaitable, Tuple, Optional
from app.agents.compiler.models import CodeArtifact
from app.agents.self_healing.models import HealingRecord, HealingSummary

logger = logging.getLogger("ghosttrace.self_healing.publisher")

HealingCallback = Callable[[HealingRecord, CodeArtifact], Union[None, Awaitable[None]]]


class HealingPublisher:
    """
    Publisher distributing HealingRecord objects and versioned CodeArtifacts to subscribers.
    """
    def __init__(self):
        self._subscribers: List[HealingCallback] = []

    def subscribe(self, callback: HealingCallback) -> None:
        """Registers a healing subscriber callback."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered healing subscriber: {callback.__name__}")

    def unsubscribe(self, callback: HealingCallback) -> None:
        """Unregisters a subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered healing subscriber: {callback.__name__}")

    async def publish(self, record: HealingRecord, artifact: CodeArtifact) -> None:
        """Publishes HealingRecord and versioned CodeArtifact to subscribers."""
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(record, artifact)
                else:
                    callback(record, artifact)
            except Exception as e:
                logger.error(f"Error in healing subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns subscriber count."""
        return len(self._subscribers)
