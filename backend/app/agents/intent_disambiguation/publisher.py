import inspect
import logging
from typing import Callable, List, Union, Awaitable, Tuple, Optional, Any
from app.models.workflow import IntentDecision, WorkflowCandidate

logger = logging.getLogger("ghosttrace.intent_disambiguation.publisher")

# Decision subscriber callback accepts decision and optional workflow candidate
DecisionCallback = Callable[[IntentDecision, Optional[WorkflowCandidate]], Any]


class DecisionPublisher:
    """
    Publisher distributing resolved IntentDecision records and their associated WorkflowCandidate
    objects to downstream consumers (Workflow DNA Agent, Orchestrator, Dashboard).
    """
    def __init__(self):
        self._subscribers: List[DecisionCallback] = []

    def subscribe(self, callback: DecisionCallback) -> None:
        """Registers a subscriber callback."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered decision subscriber: {callback.__name__}")

    def unsubscribe(self, callback: DecisionCallback) -> None:
        """Unregisters a subscriber callback."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered decision subscriber: {callback.__name__}")

    async def publish(self, decision: IntentDecision, candidate: Optional[WorkflowCandidate] = None) -> None:
        """
        Publishes both the IntentDecision and its associated WorkflowCandidate to subscribers.
        """
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(decision, candidate)
                else:
                    callback(decision, candidate)
            except Exception as e:
                logger.error(f"Error in decision subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns subscriber count."""
        return len(self._subscribers)
