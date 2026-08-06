import inspect
import logging
from typing import Callable, List, Union, Awaitable
from app.models.workflow import WorkflowDNA

logger = logging.getLogger("ghosttrace.workflow_dna.publisher")

DNACallback = Callable[[WorkflowDNA], Union[None, Awaitable[None]]]


class DNAPublisher:
    """
    Publisher distributing synthesized WorkflowDNA objects to downstream subscribers
    (Compiler Agent, Orchestrator, Database Store).
    """
    def __init__(self):
        self._subscribers: List[DNACallback] = []

    def subscribe(self, callback: DNACallback) -> None:
        """Registers a subscriber callback to receive WorkflowDNA objects."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered DNA subscriber: {callback.__name__}")

    def unsubscribe(self, callback: DNACallback) -> None:
        """Unregisters a DNA subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered DNA subscriber: {callback.__name__}")

    async def publish(self, dna: WorkflowDNA) -> None:
        """Publishes a WorkflowDNA object to all registered subscribers."""
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(dna)
                else:
                    callback(dna)
            except Exception as e:
                logger.error(f"Error in DNA subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns active subscriber count."""
        return len(self._subscribers)
