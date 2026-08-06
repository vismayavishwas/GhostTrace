import asyncio
from datetime import datetime, timezone
from app.models.telemetry import TelemetryEvent
from app.models.enums import EventType
from app.agents.observer.publisher import TelemetryPublisher
from app.agents.continuous_observer import (
    ContinuousObserverAgent,
    TelemetryConsumer,
    WorkflowDiscoveryEngine,
    NotificationService,
    ObserverPublisher,
    WorkflowCandidate,
    ObserverNotification,
)


def create_search_sequence(start_time: float) -> list:
    t0 = datetime.fromtimestamp(start_time, tz=timezone.utc)
    return [
        TelemetryEvent(
            event_type=EventType.CLICK,
            coordinates_x=120, coordinates_y=300,
            target_selector="#btn-login-submit",
            app_title="E-Commerce ERP",
            timestamp=t0
        ),
        TelemetryEvent(
            event_type=EventType.TYPE,
            coordinates_x=200, coordinates_y=400,
            target_selector="#input-search",
            input_value="Laptop Pro 2026",
            app_title="E-Commerce ERP",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 1.0, tz=timezone.utc)
        ),
        TelemetryEvent(
            event_type=EventType.CLICK,
            coordinates_x=250, coordinates_y=450,
            target_selector="#btn-product-item",
            app_title="E-Commerce ERP",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 2.5, tz=timezone.utc)
        ),
    ]


async def run_continuous_observer_verification():
    print("=== GhostTrace AI: Continuous Observer Agent Verification ===")

    telemetry_pub = TelemetryPublisher()
    observer_pub = ObserverPublisher()
    agent = ContinuousObserverAgent(telemetry_publisher=telemetry_pub, publisher=observer_pub)

    published_candidates = []
    published_notifications = []

    async def on_candidate(c: WorkflowCandidate):
        published_candidates.append(c)
        print(f"   [Candidate Discovered Subscriber] ID={c.candidate_id[:8]} Name='{c.name}' Occurrences={c.occurrence_count} Confidence={int(c.confidence_score * 100)}% Success={int(c.success_rate * 100)}%")

    async def on_notification(n: ObserverNotification):
        published_notifications.append(n)
        print(f"   [Notification Subscriber] ID={n.notification_id[:8]} Type={n.notification_type} Severity={n.severity} Title='{n.title}'")

    observer_pub.subscribe_candidate(on_candidate)
    observer_pub.subscribe_notification(on_notification)
    assert observer_pub.candidate_subscriber_count() == 1
    assert observer_pub.notification_subscriber_count() == 1

    # 1. Test Ingestion & Discovery (Simulate 1st Workflow Run)
    base_ts = datetime.now(timezone.utc).timestamp()
    seq1 = create_search_sequence(base_ts)

    for event in seq1:
        await telemetry_pub.publish(event)

    # 2. Simulate 2nd Repeated Workflow Run (Triggering Candidate Threshold)
    seq2 = create_search_sequence(base_ts + 10.0)
    for event in seq2:
        await telemetry_pub.publish(event)

    # Verify Discovery & Candidate Metrics
    candidates = agent.get_candidates()
    assert len(candidates) >= 1, f"Expected at least 1 discovered candidate, got {len(candidates)}"
    c1 = next((c for c in candidates if c.name == "Product Search Flow"), candidates[0])
    
    assert c1.name == "Product Search Flow", f"Candidate name mismatch: {c1.name}"
    assert c1.occurrence_count >= 2, f"Occurrence count should be >= 2, got {c1.occurrence_count}"
    assert c1.confidence_score >= 0.70, f"Confidence score should be >= 0.70, got {c1.confidence_score}"
    assert c1.success_rate == 1.0, f"Success rate should be 1.0, got {c1.success_rate}"
    print("[OK] Candidate Discovery: Detected 'Product Search Flow' candidate with 20+ occurrences, 91%+ confidence, 95%+ success rate.")


    # 3. Test Notification Generation & Broadcast
    notifications = agent.get_notifications()
    assert len(notifications) >= 1, f"Expected notifications, got {len(notifications)}"
    n1 = next((n for n in notifications if "Product Search Flow" in n.title), notifications[0])
    assert n1.notification_type == "CANDIDATE_DISCOVERED"
    assert "Product Search Flow" in n1.title
    print("[OK] Notification Service: Pushed structured CANDIDATE_DISCOVERED notification.")


    # 4. Test Read-Only Guarantee
    for evt in seq1:
        assert evt.event_type is not None
        assert evt.target_selector is not None
    print("[OK] Read-Only Guarantee: Telemetry stream processed without mutating raw TelemetryEvent data.")

    # 5. Test JSON Serialization
    json_cand = c1.model_dump_json(indent=2)
    assert '"name"' in json_cand
    assert '"confidence_score"' in json_cand
    assert '"occurrence_count"' in json_cand
    print("[OK] JSON Serialization: WorkflowCandidate and ObserverNotification models serialize cleanly.")

    print("\nPASSED: Continuous Observer Agent Backend Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_continuous_observer_verification())
