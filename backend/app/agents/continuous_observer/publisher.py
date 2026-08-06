import inspect
import logging
from typing import Callable, List, Union, Awaitable
from app.agents.continuous_observer.models import WorkflowCandidate, ObserverNotification

logger = logging.getLogger("ghosttrace.continuous_observer.publisher")

CandidateCallback = Callable[[WorkflowCandidate], Union[None, Awaitable[None]]]
NotificationCallback = Callable[[ObserverNotification], Union[None, Awaitable[None]]]


class ObserverPublisher:
    """
    Publisher distributing discovered WorkflowCandidates and ObserverNotifications to subscribers.
    """
    def __init__(self):
        self._candidate_subscribers: List[CandidateCallback] = []
        self._notification_subscribers: List[NotificationCallback] = []

    def subscribe_candidate(self, callback: CandidateCallback) -> None:
        """Registers candidate discovery subscriber."""
        if callback not in self._candidate_subscribers:
            self._candidate_subscribers.append(callback)
            logger.debug(f"Registered candidate subscriber: {callback.__name__}")

    def subscribe_notification(self, callback: NotificationCallback) -> None:
        """Registers notification subscriber."""
        if callback not in self._notification_subscribers:
            self._notification_subscribers.append(callback)
            logger.debug(f"Registered notification subscriber: {callback.__name__}")

    async def publish_candidate(self, candidate: WorkflowCandidate) -> None:
        """Publishes WorkflowCandidate to subscribers."""
        for callback in self._candidate_subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(candidate)
                else:
                    callback(candidate)
            except Exception as e:
                logger.error(f"Error in candidate subscriber {callback.__name__}: {e}", exc_info=True)

    async def publish_notification(self, notification: ObserverNotification) -> None:
        """Publishes ObserverNotification to subscribers."""
        for callback in self._notification_subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(notification)
                else:
                    callback(notification)
            except Exception as e:
                logger.error(f"Error in notification subscriber {callback.__name__}: {e}", exc_info=True)

    def candidate_subscriber_count(self) -> int:
        return len(self._candidate_subscribers)

    def notification_subscriber_count(self) -> int:
        return len(self._notification_subscribers)
