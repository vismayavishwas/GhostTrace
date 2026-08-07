import inspect
import logging
from typing import Callable, List, Union, Awaitable, Any
from app.models.workflow import WorkflowCandidate

logger = logging.getLogger("ghosttrace.pattern_discovery.publisher")

CandidateCallback = Callable[[WorkflowCandidate], Any]


class CandidatePublisher:
    """
    Publisher bus distributing detected WorkflowCandidate objects to downstream subscribers.
    """
    def __init__(self):
        self._subscribers: List[CandidateCallback] = []

    def subscribe(self, callback: CandidateCallback) -> None:
        """Registers a callback function to receive published WorkflowCandidates."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered candidate subscriber: {callback.__name__}")

    def unsubscribe(self, callback: CandidateCallback) -> None:
        """Unregisters a candidate subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered candidate subscriber: {callback.__name__}")

    async def publish(self, candidate: WorkflowCandidate) -> None:
        """Publishes a WorkflowCandidate to all registered subscribers."""
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(candidate)
                else:
                    callback(candidate)
            except Exception as e:
                logger.error(f"Error in candidate subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns count of active subscribers."""
        return len(self._subscribers)
