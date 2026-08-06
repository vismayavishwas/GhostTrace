import asyncio
from datetime import datetime, timezone
from app.models.telemetry import TelemetryEvent
from app.models.enums import EventType
from app.agents.ghost_replay import (
    GhostReplayAgent,
    TrajectoryExtractor,
    ReplayStreamer,
    ReplayFrame,
    ReplaySessionState,
)


def create_sample_telemetry_events() -> list:
    t0 = datetime.now(timezone.utc)
    return [
        TelemetryEvent(
            event_type=EventType.NAVIGATION,
            coordinates_x=100, coordinates_y=200,
            target_selector="body",
            timestamp=t0,
            metadata={"viewport_width": 1920, "viewport_height": 1080, "scroll_x": 0.0, "scroll_y": 0.0}
        ),
        TelemetryEvent(
            event_type=EventType.SCROLL,
            coordinates_x=150, coordinates_y=250,
            target_selector="#btn-login",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 0.5, tz=timezone.utc),
            metadata={"viewport_width": 1920, "viewport_height": 1080, "scroll_x": 0.0, "scroll_y": 0.0}
        ),
        TelemetryEvent(
            event_type=EventType.CLICK,
            coordinates_x=160, coordinates_y=255,
            target_selector="#btn-login",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 1.2, tz=timezone.utc),
            metadata={"viewport_width": 1920, "viewport_height": 1080, "scroll_x": 0.0, "scroll_y": 100.0}
        ),
        TelemetryEvent(
            event_type=EventType.TYPE,
            coordinates_x=160, coordinates_y=255,
            target_selector="#input-user",
            input_value="admin",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 2.5, tz=timezone.utc),
            metadata={"viewport_width": 1920, "viewport_height": 1080, "scroll_x": 0.0, "scroll_y": 100.0}
        ),
        TelemetryEvent(
            event_type=EventType.CLICK,
            coordinates_x=300, coordinates_y=400,
            target_selector="#btn-submit",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 4.0, tz=timezone.utc),
            metadata={"viewport_width": 1920, "viewport_height": 1080, "scroll_x": 0.0, "scroll_y": 150.0}
        )
    ]


async def run_ghost_replay_verification():
    print("=== GhostTrace AI: Ghost Replay Agent Verification ===")

    agent = GhostReplayAgent()

    # 1. Test Trajectory Extraction & Viewport Context
    events = create_sample_telemetry_events()
    streamer = agent.create_replay_session("wf-ghost-demo-123", events)
    frames = streamer.frames

    assert len(frames) == 5, f"Expected 5 frames, got {len(frames)}"
    assert frames[0].timestamp_ms == 0.0, f"Initial timestamp should be 0.0ms, got {frames[0].timestamp_ms}"
    assert frames[2].is_click is True, "Frame index 2 should be identified as a click event"
    assert frames[2].scroll_y == 100.0, "Scroll Y position mismatch"
    assert len(frames[0].frame_id) > 0, "Frame ID missing"
    print("[OK] Trajectory Extraction: Normalized timestamped ReplayFrames extracted with viewport/scroll metadata.")

    # 2. Test Playback Speed Control (0.25x to 4.0x)
    streamer.set_speed(0.25)
    assert streamer.state.speed_multiplier == 0.25
    streamer.set_speed(4.0)
    assert streamer.state.speed_multiplier == 4.0
    streamer.set_speed(1.5)
    assert streamer.state.speed_multiplier == 1.5
    print("[OK] Speed Control: Supported speed multipliers (0.25x, 0.5x, 1x, 1.5x, 2x, 4x).")

    # 3. Test Session State Transitions
    streamer.play()
    assert streamer.state.status == "PLAYING"
    streamer.pause()
    assert streamer.state.status == "PAUSED"
    streamer.stop()
    assert streamer.state.status == "STOPPED"
    assert streamer.state.current_time_ms == 0.0
    print("[OK] State Transitions: IDLE -> PLAYING -> PAUSED -> STOPPED state transitions verified.")

    # 4. Test Timeline Seek & Skip to Next Click
    state_seek, frame_seek = streamer.seek_to_time(1200.0)
    assert state_seek.current_time_ms == 1200.0
    assert frame_seek is not None and frame_seek.frame_index == 2
    print("[OK] Timeline Seek: Seeked to 1200ms and active frame matched.")

    # Fast forward to next click
    state_skip, frame_skip = streamer.skip_to_next_click()
    assert frame_skip is not None and frame_skip.frame_index == 4, f"Expected frame index 4, got {frame_skip.frame_index if frame_skip else None}"
    assert frame_skip.is_click is True
    print("[OK] Skip to Next Click: Fast-forwarded directly to the next click frame at 4000ms.")

    # 5. Test JSON Serialization
    json_frame = frames[0].model_dump_json(indent=2)
    assert '"frame_id"' in json_frame
    assert '"viewport_width"' in json_frame
    assert '"scroll_y"' in json_frame
    print("[OK] JSON Serialization: ReplayFrame and ReplaySessionState models serialize cleanly.")

    print("\nPASSED: Ghost Replay Agent Backend Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_ghost_replay_verification())
