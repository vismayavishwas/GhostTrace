import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.models.telemetry import TelemetryEvent
from app.agents.ghost_replay.replay_streamer import ReplayStreamer

from app.agents.ghost_replay.models import ReplayFrame
from app.orchestration.nodes import (
    get_global_observer,
    get_global_pattern_discovery,
    get_global_compiler,
)

logger = logging.getLogger("ghosttrace.api.websockets")

router = APIRouter(tags=["WebSocket Streams"])


@router.websocket("/ws/reasoning")
async def websocket_reasoning_endpoint(websocket: WebSocket):
    """Specialized WebSocket stream for live AI Reasoning decision logs."""
    await websocket.accept()
    logger.info("Client connected to /ws/reasoning stream")
    pattern_agent = get_global_pattern_discovery()

    async def on_candidate(candidate):
        try:
            await websocket.send_json({
                "stream": "reasoning",
                "type": "CANDIDATE_DISCOVERED",
                "payload": candidate.model_dump()
            })
        except Exception:
            pass

    pattern_agent.publisher.subscribe(on_candidate)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pattern_agent.publisher.unsubscribe(on_candidate)
        logger.info("Client disconnected from /ws/reasoning")


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Specialized WebSocket stream for live telemetry interaction events."""
    await websocket.accept()
    logger.info("Client connected to /ws/telemetry stream")
    observer = get_global_observer()

    async def on_telemetry(event: TelemetryEvent):
        try:
            await websocket.send_json({
                "stream": "telemetry",
                "type": "TELEMETRY_EVENT",
                "payload": event.model_dump() if hasattr(event, "model_dump") else str(event)
            })
        except Exception:
            pass

    observer.publisher.subscribe(on_telemetry)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        observer.publisher.unsubscribe(on_telemetry)
        logger.info("Client disconnected from /ws/telemetry")



@router.websocket("/ws/replay")
async def websocket_replay_endpoint(websocket: WebSocket):
    """Specialized WebSocket stream for ReplayFrames visual reconstruction & playback controls."""
    await websocket.accept()
    logger.info("Client connected to /ws/replay stream")
    observer = get_global_observer()
    frame_count = 0

    # Internal buffer of frames for ReplayStreamer control
    buffered_frames = []
    streamer = ReplayStreamer("wf-live-replay", buffered_frames)

    async def on_telemetry(event: TelemetryEvent):
        nonlocal frame_count
        frame_count += 1
        frame = ReplayFrame(
            frame_index=frame_count,
            timestamp_ms=frame_count * 500.0,
            x=event.coordinates_x or 100,
            y=event.coordinates_y or 100,
            target_selector=event.target_selector or "body",
            is_click=(event.event_type.name if hasattr(event.event_type, "name") else str(event.event_type)) in ["CLICK", "COPY", "PASTE"],
            app_title=event.app_title or "Browser"
        )
        buffered_frames.append(frame)

        try:
            await websocket.send_json({
                "stream": "replay",
                "type": "REPLAY_FRAME",
                "payload": frame.model_dump(),
                "playback_state": streamer.state.model_dump()
            })
        except Exception:
            pass

    observer.publisher.subscribe(on_telemetry)

    try:
        while True:
            msg_text = await websocket.receive_text()
            try:
                msg = json.loads(msg_text)
                cmd = msg.get("command", "").upper()

                if cmd == "PLAY":
                    state = streamer.play()
                    await websocket.send_json({"type": "STATE_UPDATE", "state": state.model_dump()})
                elif cmd == "PAUSE":
                    state = streamer.pause()
                    await websocket.send_json({"type": "STATE_UPDATE", "state": state.model_dump()})
                elif cmd == "STOP":
                    state = streamer.stop()
                    await websocket.send_json({"type": "STATE_UPDATE", "state": state.model_dump()})
                elif cmd == "SET_SPEED":
                    speed = float(msg.get("multiplier", 1.0))
                    state = streamer.set_speed(speed)
                    await websocket.send_json({"type": "STATE_UPDATE", "state": state.model_dump()})
                elif cmd == "SEEK":
                    target_ms = float(msg.get("time_ms", 0.0))
                    state, frame = streamer.seek_to_time(target_ms)
                    await websocket.send_json({
                        "type": "SEEK_RESULT",
                        "state": state.model_dump(),
                        "active_frame": frame.model_dump() if frame else None
                    })
                elif cmd == "SKIP_TO_CLICK":
                    state, frame = streamer.skip_to_next_click()
                    await websocket.send_json({
                        "type": "SEEK_RESULT",
                        "state": state.model_dump(),
                        "active_frame": frame.model_dump() if frame else None
                    })
            except Exception as e:
                logger.debug(f"Replay WS command error: {e}")
    except WebSocketDisconnect:
        observer.publisher.unsubscribe(on_telemetry)
        logger.info("Client disconnected from /ws/replay")


@router.websocket("/ws/pipeline")
async def websocket_pipeline_endpoint(websocket: WebSocket):
    """Specialized WebSocket stream for Compiler & Sandbox pipeline progress."""
    await websocket.accept()
    logger.info("Client connected to /ws/pipeline stream")
    compiler = get_global_compiler()

    async def on_artifact(artifact):
        try:
            await websocket.send_json({
                "stream": "pipeline",
                "type": "CODE_COMPILED",
                "payload": artifact.model_dump()
            })
        except Exception:
            pass

    compiler.publisher.subscribe(on_artifact)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        compiler.publisher.unsubscribe(on_artifact)
        logger.info("Client disconnected from /ws/pipeline")
