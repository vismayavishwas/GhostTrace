import logging
from typing import Optional, List
from app.models.telemetry import TelemetryEvent
from app.agents.observer.publisher import TelemetryPublisher
from app.agents.continuous_observer.models import WorkflowCandidate, ObserverNotification
from app.agents.continuous_observer.telemetry_consumer import TelemetryConsumer
from app.agents.continuous_observer.workflow_discovery import WorkflowDiscoveryEngine
from app.agents.continuous_observer.notification_service import NotificationService
from app.agents.continuous_observer.publisher import ObserverPublisher

logger = logging.getLogger("ghosttrace.continuous_observer")


class ContinuousObserverAgent:
    """
    Continuous Observer Agent responsible for background telemetry observation,
    incremental workflow candidate discovery, pattern metrics calculation (occurrences,
    confidence score, success rate), and real-time observer notification broadcasting.
    Strictly READ-ONLY.
    """
    def __init__(
        self,
        consumer: Optional[TelemetryConsumer] = None,
        discovery_engine: Optional[WorkflowDiscoveryEngine] = None,
        notification_service: Optional[NotificationService] = None,
        telemetry_publisher: Optional[TelemetryPublisher] = None,
        publisher: Optional[ObserverPublisher] = None,
    ):
        self.consumer = consumer or TelemetryConsumer()
        self.discovery_engine = discovery_engine or WorkflowDiscoveryEngine()
        self.notification_service = notification_service or NotificationService()
        self.publisher = publisher or ObserverPublisher()

        # Subscribe independently to TelemetryPublisher if provided
        if telemetry_publisher:
            telemetry_publisher.subscribe(self.on_telemetry_event)
            logger.info("ContinuousObserverAgent subscribed independently to TelemetryPublisher")

    async def on_telemetry_event(self, event: TelemetryEvent) -> List[WorkflowCandidate]:
        """Callback executed upon receiving a TelemetryEvent from TelemetryPublisher."""
        return await self.process_telemetry_event(event)

    async def process_telemetry_event(
        self,
        event: TelemetryEvent,
        success: bool = True,
        latency_ms: float = 0.0
    ) -> List[WorkflowCandidate]:
        """
        Ingests a telemetry event, analyzes recent observation window for recurring patterns,
        emits discovered candidates, and pushes observer notifications.
        """
        # 1. Ingest Observation (Read-Only)
        self.consumer.ingest_event(event, success=success, latency_ms=latency_ms)

        # 2. Analyze Observation Window for Workflow Candidates
        recent_obs = self.consumer.get_recent_observations()
        discovered_candidates = self.discovery_engine.analyze_observations(recent_obs)

        # 3. Handle Discovered Candidates & Notifications
        for candidate in discovered_candidates:
            logger.info(
                f"ContinuousObserverAgent discovered Candidate '{candidate.name}' "
                f"(Occurrences: {candidate.occurrence_count}, Confidence: {candidate.confidence_score}, Success: {candidate.success_rate})"
            )

            # Generate & Publish Candidate Discovery Notification
            notification = self.notification_service.notify_candidate_discovered(candidate)
            await self.publisher.publish_notification(notification)

            # Generate Milestone Notification if candidate has reached significant repetitions
            if candidate.occurrence_count >= 5:
                milestone_notif = self.notification_service.notify_pattern_milestone(candidate)
                await self.publisher.publish_notification(milestone_notif)

            await self.publisher.publish_candidate(candidate)

        # 4. Handle Anomaly Alerts if execution failure occurs
        if not success:
            anomaly_notif = self.notification_service.notify_anomaly(
                title="Stream Interaction Failure",
                message=f"Action failed on target selector: {event.target_selector or 'unknown'}"
            )
            await self.publisher.publish_notification(anomaly_notif)

        return discovered_candidates


    def get_candidates(self) -> List[WorkflowCandidate]:
        """Returns all discovered workflow candidates."""
        return self.discovery_engine.get_all_candidates()

    def get_notifications(self) -> List[ObserverNotification]:
        """Returns notification history."""
        return self.notification_service.get_notification_history()
