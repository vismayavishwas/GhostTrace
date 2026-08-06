import logging
from typing import List, Optional
from app.agents.continuous_observer.models import WorkflowCandidate, ObserverNotification

logger = logging.getLogger("ghosttrace.continuous_observer.notification")


class NotificationService:
    """
    Notification service generating structured ObserverNotification alerts when
    workflow candidates are discovered, pattern significance milestones are achieved,
    or stream anomalies occur.
    """
    def __init__(self):
        self._history: List[ObserverNotification] = []

    def notify_candidate_discovered(self, candidate: WorkflowCandidate) -> ObserverNotification:
        """Pushes a notification when a new workflow candidate is discovered."""
        notification = ObserverNotification(
            notification_type="CANDIDATE_DISCOVERED",
            title=f"New Workflow Candidate: {candidate.name}",
            message=(
                f"Observed {candidate.occurrence_count} times across {len(candidate.applications_involved)} application(s). "
                f"Confidence: {int(candidate.confidence_score * 100)}%, Success Rate: {int(candidate.success_rate * 100)}%."
            ),
            candidate_id=candidate.candidate_id,
            severity="SUCCESS"
        )
        self._history.append(notification)
        logger.info(f"NotificationService pushed candidate alert: {notification.title}")
        return notification

    def notify_pattern_milestone(self, candidate: WorkflowCandidate) -> ObserverNotification:
        """Pushes a notification when a pattern reaches high significance (e.g. 20+ occurrences)."""
        notification = ObserverNotification(
            notification_type="PATTERN_MILESTONE",
            title=f"Pattern Milestone: {candidate.name}",
            message=f"Workflow candidate '{candidate.name}' reached {candidate.occurrence_count} occurrences with {int(candidate.confidence_score * 100)}% confidence.",
            candidate_id=candidate.candidate_id,
            severity="INFO"
        )
        self._history.append(notification)
        logger.info(f"NotificationService pushed milestone alert: {notification.title}")
        return notification

    def notify_anomaly(self, title: str, message: str, candidate_id: Optional[str] = None) -> ObserverNotification:
        """Pushes a notification when an observation anomaly is detected."""
        notification = ObserverNotification(
            notification_type="ANOMALY_DETECTED",
            title=title,
            message=message,
            candidate_id=candidate_id,
            severity="WARNING"
        )
        self._history.append(notification)
        logger.warning(f"NotificationService pushed anomaly alert: {title}")
        return notification

    def get_notification_history(self) -> List[ObserverNotification]:
        """Returns notification history."""
        return list(self._history)
