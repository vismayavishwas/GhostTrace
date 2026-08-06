import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any, Optional
from app.agents.ghost_replay.ghost_replay_agent import GhostReplayAgent
from app.agents.ghost_replay.models import ReplayFrame

logger = logging.getLogger("ghosttrace.api.ghost_replay")
router = APIRouter(prefix="/ws/ghost-replay", tags=["GhostReplay"])

_global_replay_agent = GhostReplayAgent()


def get_ghost_replay_agent() -> GhostReplayAgent:
    return _global_replay_agent


@router.websocket("/{workflow_id}")
async def ghost_replay_websocket(
    websocket: WebSocket,
    workflow_id: str,
    agent: GhostReplayAgent = Depends(get_ghost_replay_agent)
):
    """
    WebSocket transport streaming timestamped ReplayFrames for visual ghost replay.
    Supports play, pause, stop, speed changes, and skip-to-next-click commands.
    """
    await websocket.accept()
    logger.info(f"WebSocket client connected to GhostReplay for Workflow ID={workflow_id[:8]}")

    streamer = agent.get_streamer(workflow_id)
    if not streamer:
        # Send empty initial state if workflow_id has no session registered
        frames = agent.get_frames(workflow_id)
        streamer = agent.create_replay_session(workflow_id, [])

    try:
        # Send initial session state metadata
        await websocket.send_text(streamer.state.model_dump_json())

        while True:
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
                cmd = msg.get("command", "").lower()

                if cmd == "play":
                    state = streamer.play()
                    await websocket.send_text(state.model_dump_json())
                elif cmd == "pause":
                    state = streamer.pause()
                    await websocket.send_text(state.model_dump_json())
                elif cmd == "stop":
                    state = streamer.stop()
                    await websocket.send_text(state.model_dump_json())
                elif cmd == "set_speed":
                    mult = float(msg.get("multiplier", 1.0))
                    state = streamer.set_speed(mult)
                    await websocket.send_text(state.model_dump_json())
                elif cmd == "seek":
                    target_ms = float(msg.get("target_time_ms", 0.0))
                    state, frame = streamer.seek_to_time(target_ms)
                    await websocket.send_text(json.dumps({
                        "session": state.model_dump(),
                        "active_frame": frame.model_dump() if frame else None
                    }))
                elif cmd == "skip_to_next_click":
                    state, frame = streamer.skip_to_next_click()
                    await websocket.send_text(json.dumps({
                        "session": state.model_dump(),
                        "active_frame": frame.model_dump() if frame else None
                    }))
                elif cmd == "get_frames":
                    # Send complete frames payload for client-side interpolation
                    frames_data = [f.model_dump() for f in streamer.frames]
                    await websocket.send_text(json.dumps({
                        "type": "frames_batch",
                        "workflow_id": workflow_id,
                        "frames": frames_data
                    }))

            except json.JSONDecodeError:
                logger.warning(f"Received malformed WebSocket payload: {data_text}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected from GhostReplay for Workflow ID={workflow_id[:8]}")
