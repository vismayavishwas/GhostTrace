import asyncio
import sys
from app.models.enums import EventType
from app.models.telemetry import TelemetryEvent
from app.agents.observer import ObserverAgent, TelemetryBuffer, TelemetryPublisher


async def run_observer_verification():
    print("=== GhostTrace AI: Observer Agent Verification ===")
    
    # 1. Test Dependency Injection & Buffer Capacity Initialization
    buffer = TelemetryBuffer(capacity=3)
    publisher = TelemetryPublisher()
    observer = ObserverAgent(buffer=buffer, publisher=publisher)
    
    published_events = []
    
    async def sample_subscriber(event: TelemetryEvent):
        published_events.append(event)
        print(f"   [Subscriber Received] Event ID={event.event_id[:8]}... Type={event.event_type} App='{event.app_title}'")
    
    publisher.subscribe(sample_subscriber)
    assert publisher.subscriber_count() == 1, "Subscriber registration failed"
    
    # 2. Test Processing Valid Mouse Click Payload (JSON Dict)
    valid_mouse_dict = {
        "event_type": "CLICK",
        "x": 150,
        "y": 420,
        "target_selector": "#login-btn",
        "element_tag": "BUTTON",
        "app_title": "Zendesk Customer Portal",
        "timestamp": "2026-08-05T14:30:00Z"
    }
    
    event_1 = await observer.process_raw_event(valid_mouse_dict)
    assert event_1 is not None, "Valid mouse click payload failed validation"
    assert event_1.event_type == EventType.CLICK
    assert event_1.coordinates_x == 150
    assert event_1.coordinates_y == 420
    assert event_1.target_selector == "#login-btn"
    assert event_1.app_title == "Zendesk Customer Portal"
    print("[OK] Valid Mouse Click Payload: Parsed, normalized, and validated successfully.")


    # 3. Test Processing Valid Keyboard Type Payload (JSON String)
    valid_type_json = """{
        "event_type": "TYPE",
        "input_value": "user@enterprise.com",
        "target_selector": "input[name='email']",
        "app_title": "SAP Logistics",
        "timestamp": 1754400000
    }"""
    
    event_2 = await observer.process_raw_event(valid_type_json)
    assert event_2 is not None, "Valid keyboard type payload failed validation"
    assert event_2.event_type == EventType.TYPE
    assert event_2.input_value == "user@enterprise.com"
    assert event_2.app_title == "SAP Logistics"
    print("[OK] Valid Keyboard Type Payload: Parsed from JSON string successfully.")

    # 4. Test Ring Buffer Capacity & Bounded FIFO Eviction
    await observer.process_raw_event({"event_type": "SCROLL", "app_title": "Excel 1"})
    await observer.process_raw_event({"event_type": "APP_SWITCH", "app_title": "Excel 2"})
    
    assert buffer.size() == 3, f"Buffer size mismatch: expected 3, got {buffer.size()}"
    recent_events = buffer.get_recent()
    assert len(recent_events) == 3
    # First event (event_1) should be evicted because capacity is 3 and we pushed 4 events
    assert recent_events[0].event_type == EventType.TYPE
    assert recent_events[-1].event_type == EventType.APP_SWITCH
    print("[OK] Ring Buffer Bounded Capacity: Bounded capacity limits and FIFO eviction confirmed.")

    # 5. Test Handling Malformed Payloads Gracefully (No Exceptions Raised)
    malformed_inputs = [
        "THIS IS NOT VALID JSON {{{{",
        12345,
        None,
        [],
        {"event_type": 99999, "invalid": True}  # Invalid enum value gracefully handled by fallback
    ]
    
    for malformed in malformed_inputs:
        result = await observer.process_raw_event(malformed) # type: ignore
        # Should gracefully return None or fallback without throwing exception
        if malformed in ["THIS IS NOT VALID JSON {{{{", 12345, None, []]:
            assert result is None, f"Malformed input {malformed} should have returned None"
            
    print("[OK] Malformed Event Handling: Malformed payloads handled gracefully without crashing.")
    
    # 6. Verify Subscriber Received All Valid & Fallback Published Events
    assert len(published_events) == 5, f"Subscriber event count mismatch: expected 5, got {len(published_events)}"
    print("[OK] Event Publisher: Subscriber notifications verified successfully.")

    
    print("\nPASSED: Observer Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_observer_verification())
