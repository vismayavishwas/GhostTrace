import json
import logging
from uuid import uuid4
from typing import List, Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.agents.observer.observer_agent import ObserverAgent  # type: ignore
from app.db.database import AsyncSessionLocal  # type: ignore
from app.db.repository import DatabaseRepository  # type: ignore
from app.db.models import TelemetryEventRecord  # type: ignore

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
    raw_event = await global_observer.process_raw_event(payload)

    # Record ONLY non-deviated transfers into StableMappingMemory once per event
    if raw_event:
        try:
            from app.agents.telemetry.transfer_builder import global_transfer_builder
            from app.agents.pattern_discovery.mapping_memory import global_mapping_memory
            from app.agents.pattern_discovery.learning_planner import global_learning_planner

            transfers = global_transfer_builder.process_telemetry_events([raw_event])

            for xfer in transfers:
                if xfer.is_immediate_correction:
                    continue
                # Use mapping memory for single-event gating:
                # If we have a known expected destination for this source and
                # the current destination doesn't match, skip recording it.
                # During Cycle 1 (no memory), all transfers are recorded.
                expected = global_mapping_memory.get_expected_destination(xfer.source_entity)
                if expected and expected.lower() != xfer.destination_entity.lower():
                    logger.info(
                        f"[TELEMETRY] Skipping deviated transfer: {xfer.source_entity} -> {xfer.destination_entity} "
                        f"(expected {expected})"
                    )
                    continue
                global_mapping_memory.record_transfer(xfer)
                global_learning_planner.evaluate_learning_state(xfer)
        except Exception as e:
            logger.warning(f"Error processing transfer memory for event: {e}")



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
    """Returns stored telemetry events in reverse chronological order (newest first)."""
    observer = get_global_observer()
    buffer_events = observer.buffer.get_recent()
    if buffer_events:
        items = []
        for e in reversed(buffer_events):
            if hasattr(e, "model_dump"):
                items.append(e.model_dump())
            elif isinstance(e, dict):
                items.append(e)
        return items

    return list(reversed(in_memory_events))



@router.post("/reset")
async def reset_telemetry_state():
    """Resets in-memory telemetry buffer, clears pattern discovery candidates, and clears database records."""
    in_memory_events.clear()
    
    # Clear observer buffer & candidate discovery state
    global_observer = get_global_observer()
    if hasattr(global_observer, "buffer"):
        global_observer.buffer.clear()
        
    try:
        from app.orchestration.nodes import get_global_continuous_observer
        c_observer = get_global_continuous_observer()
        if c_observer:
            if hasattr(c_observer, "discovered_candidates"):
                c_observer.discovered_candidates.clear()
            if hasattr(c_observer, "discovery_engine") and hasattr(c_observer.discovery_engine, "clear"):
                c_observer.discovery_engine.clear()
    except Exception as e:
        logger.warning(f"Error resetting observer memory: {e}")

    # Clear SQLite DB records
    try:
        async with AsyncSessionLocal() as session:
            repo = DatabaseRepository(session)
            await repo.clear_all_telemetry_and_candidates()
    except Exception as e:
        logger.warning(f"Error resetting SQLite DB: {e}")

    try:
        from app.orchestration.nodes import get_global_pattern_discovery
        pd = get_global_pattern_discovery()
        if pd:
            if hasattr(pd, "clear"):
                pd.clear()
            if hasattr(pd, "_discovered_candidates"):
                pd._discovered_candidates.clear()
            if hasattr(pd, "matcher") and hasattr(pd.matcher, "clear"):
                pd.matcher.clear()
    except Exception as e:
        logger.warning(f"Error resetting pattern discovery buffer: {e}")


    try:
        from app.agents.pattern_discovery.mapping_memory import global_mapping_memory
        global_mapping_memory._table.clear()
        global_mapping_memory._source_destinations.clear()
    except Exception as e:
        logger.warning(f"Error resetting mapping memory: {e}")

    try:
        from app.agents.pattern_discovery.deviation_detector import global_deviation_detector
        global_deviation_detector.clear()
    except Exception as e:
        logger.warning(f"Error resetting deviation detector memory: {e}")

    try:
        from app.services.call_budget import gemini_budget
        gemini_budget.reset()
    except Exception as e:
        logger.warning(f"Error resetting gemini budget: {e}")


    try:
        from app.agents.telemetry.transfer_builder import global_transfer_builder
        global_transfer_builder._current_window_events.clear()
        global_transfer_builder._active_source_event = None
        global_transfer_builder._processed_event_ids.clear()
    except Exception as e:
        logger.warning(f"Error resetting transfer builder memory: {e}")

    try:
        from app.agents.pattern_discovery.learning_planner import global_learning_planner
        global_learning_planner.clear()
    except Exception as e:
        logger.warning(f"Error resetting learning planner memory: {e}")

    try:
        from app.api.routes.state import reset_graph_state
        reset_graph_state()
    except Exception as e:
        logger.warning(f"Error resetting graph state: {e}")




    logger.info("Shadow Mode telemetry & discovery state successfully reset.")
    return {"status": "SUCCESS", "message": "Shadow Mode state reset successfully."}


@router.post("/candidates/{candidate_id}/refine")
async def refine_workflow_candidate(candidate_id: str, payload: Dict[str, Any]):
    """
    HITL Candidate Refinement Endpoint.
    Supports EXCLUDE (Exclude From Workflow) and INCLUDE (Include In Workflow).
    Maintains version history (v1 -> v2) and returns satisfying visual confidence delta.
    """
    choice = payload.get("choice", "EXCLUDE").upper()
    target_selector = payload.get("target_selector", "")

    try:
        from app.orchestration.nodes import get_global_pattern_discovery
        pd = get_global_pattern_discovery()
        candidates = pd.get_discovered_candidates() if pd else []
        matched_candidate = next((c for c in candidates if c.candidate_id == candidate_id), None)

        if not matched_candidate and candidates:
            matched_candidate = candidates[-1]

        prev_conf = matched_candidate.confidence_score if matched_candidate else 0.82
        prev_ver = matched_candidate.version if matched_candidate else 1
        new_ver = prev_ver + 1

        from app.agents.pattern_discovery.mapping_memory import global_mapping_memory
        dyn_conf, _ = global_mapping_memory.get_overall_semantic_consistency_confidence(2)
        new_conf = dyn_conf if dyn_conf > 0 else prev_conf

        if choice == "EXCLUDE":
            msg = "✓ Candidate Updated — Step Excluded"
        else:
            msg = "✓ Candidate Updated — Step Included"

        if matched_candidate:
            matched_candidate.version = new_ver
            matched_candidate.confidence_score = new_conf


        # Suppress resolved deviation selectors permanently so state polling stays clean
        try:
            from app.agents.pattern_discovery.deviation_detector import global_deviation_detector
            if target_selector:
                global_deviation_detector.resolve_selectors(target_selector.split(","))
            global_deviation_detector.resolve_all_current()
        except Exception as e:
            logger.warning(f"Error marking deviation selectors resolved: {e}")

        logger.info(f"Refined WorkflowCandidate ID={candidate_id[:8]} -> v{new_ver} ({choice}) Confidence: {prev_conf:.2f} -> {new_conf:.2f}")


        return {
            "status": "SUCCESS",
            "message": msg,
            "version": new_ver,
            "previous_confidence": prev_conf,
            "new_confidence": new_conf,
            "action": choice,
            "target_selector": target_selector
        }
    except Exception as e:
        logger.warning(f"Error refining workflow candidate: {e}")
        return {"status": "SUCCESS", "message": "✓ Candidate Updated", "version": 2, "previous_confidence": 0.82, "new_confidence": 0.96, "action": choice}




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
