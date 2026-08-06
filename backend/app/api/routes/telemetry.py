import json
import logging
from uuid import uuid4
from typing import List, Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.agents.observer import ObserverAgent
from app.db.database import AsyncSessionLocal
from app.db.repository import DatabaseRepository
from app.db.models import TelemetryEventRecord

from app.orchestration.nodes import get_global_observer

logger = logging.getLogger("ghosttrace.api.telemetry")

router = APIRouter(prefix="/api/v1/telemetry", tags=["Telemetry Ingestion"])

# Global event memory buffer for fast access
in_memory_events: List[Dict[str, Any]] = []


@router.post("/events")
async def post_telemetry_event(payload: Dict[str, Any]):
    """Ingests raw telemetry event, persists to SQLite DB, and updates live perception stream."""
    in_memory_events.insert(0, payload)
    if len(in_memory_events) > 100:
        in_memory_events.pop()

    # Pass payload into global ObserverAgent to trigger TelemetryPublisher & PatternDiscovery
    global_observer = get_global_observer()
    await global_observer.process_raw_event(payload)


    try:
        async with AsyncSessionLocal() as session:
            repo = DatabaseRepository(session)
            sess_id = payload.get("session_id") or "sess-default-001"
            await repo.create_session(sess_id, app_title=payload.get("app_title", "Web App"))

            rec = TelemetryEventRecord(
                event_id=payload.get("event_id") or f"evt-{uuid4().hex[:8]}",
                session_id=sess_id,
                event_type=payload.get("event_type", "CLICK").upper(),
                active_tab=payload.get("active_tab"),
                url=payload.get("url"),
                target_selector=payload.get("target_selector"),
                xpath=payload.get("xpath"),
                bounding_box=payload.get("bounding_box"),
                scroll_pos=payload.get("scroll_pos"),
                input_masked=payload.get("input_masked"),
                coordinates_x=float(payload.get("coordinates_x", 0.0)),
                coordinates_y=float(payload.get("coordinates_y", 0.0)),
            )
            await repo.save_telemetry_event(rec)
    except Exception as e:
        logger.warning(f"Error persisting event to SQLite: {e}")



    return {"status": "SUCCESS", "event_id": payload.get("event_id")}


@router.get("/events")
async def get_telemetry_events():
    """Returns stored telemetry events."""
    return in_memory_events


@router.post("/reset")
async def reset_telemetry_state():
    """Resets in-memory telemetry buffer, clears pattern discovery candidates, and clears database records."""
    in_memory_events.clear()
    
    # Clear observer buffer & candidate discovery state
    global_observer = get_global_observer()
    if hasattr(global_observer, "buffer"):
        global_observer.buffer.clear()
        
    try:
        from app.agents.continuous_observer.observer_agent import get_continuous_observer
        c_observer = get_continuous_observer()
        if c_observer:
            if hasattr(c_observer, "discovered_candidates"):
                c_observer.discovered_candidates.clear()
            if hasattr(c_observer, "engine") and hasattr(c_observer.engine, "discovered_candidates"):
                c_observer.engine.discovered_candidates.clear()
    except Exception as e:
        logger.warning(f"Error resetting observer memory: {e}")

    # Clear SQLite DB records
    try:
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            await session.execute(text("DELETE FROM telemetry_events"))
            await session.execute(text("DELETE FROM workflow_candidates"))
            await session.commit()
    except Exception as e:
        logger.warning(f"Error resetting SQLite DB: {e}")

    logger.info("Shadow Mode telemetry & discovery state successfully reset.")
    return {"status": "SUCCESS", "message": "Shadow Mode state reset successfully."}



@router.websocket("/ws/telemetry")
async def telemetry_websocket_endpoint(
    websocket: WebSocket,
    observer: ObserverAgent = Depends(get_global_observer)
):

    await websocket.accept()
    try:
        while True:
            raw_data = await websocket.receive_text()
            await observer.process_raw_event(raw_data)
            await websocket.send_json({"type": "ACK", "status": "processed"})
    except WebSocketDisconnect:
        pass
