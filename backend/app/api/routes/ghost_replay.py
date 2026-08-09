import logging
from typing import List, Dict, Any
from fastapi import APIRouter
from app.orchestration.nodes import get_global_observer
from app.agents.ghost_replay.path_extractor import TrajectoryExtractor
from app.api.routes.telemetry import in_memory_events

logger = logging.getLogger("ghosttrace.api.ghost_replay")

router = APIRouter(prefix="/api/v1/replay", tags=["Ghost Replay"])


@router.get("/frames")
async def get_replay_frames():
    """
    Returns actual ReplayFrame trajectory coordinates extracted from captured telemetry events.
    Never fabricates pseudo-random coordinates.
    """
    events = get_global_observer().buffer.get_recent() or in_memory_events
    if not events:
        return {"frames": [], "message": "No telemetry frames available."}

    extractor = TrajectoryExtractor()
    frames = extractor.extract_trajectory(events)
    frame_dicts = [f.model_dump() if hasattr(f, "model_dump") else f.__dict__ for f in frames]

    return {
        "frames": frame_dicts,
        "total_frames": len(frame_dicts),
        "duration_ms": frame_dicts[-1].get("timestamp_ms", 0) if frame_dicts else 0
    }
