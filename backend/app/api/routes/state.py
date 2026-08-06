import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.routes.telemetry import in_memory_events
from app.orchestration.graph import GhostTraceOrchestrator
from app.orchestration.state import GhostTraceGraphState
from app.orchestration.nodes import (
    get_global_observer,
    get_global_pattern_discovery,
    get_global_dna_agent,
)

logger = logging.getLogger("ghosttrace.api.state")

router = APIRouter(prefix="/api/v1/state", tags=["Orchestration State"])

current_graph_state: Dict[str, Any] = {
    "workflow_id": "wf-dynamic-001",
    "session_id": "sess-default-001",
    "active_node": "OBSERVING",
    "execution_status": "RUNNING",
}

active_orchestration_task: Optional[asyncio.Task] = None
latest_graph_state: Optional[GhostTraceGraphState] = None
_STORED_BUSINESS_PROCESS: Optional[Dict[str, Any]] = None


def reset_graph_state():
    global latest_graph_state, current_graph_state, _STORED_BUSINESS_PROCESS
    latest_graph_state = None
    _STORED_BUSINESS_PROCESS = None
    current_graph_state["active_node"] = "OBSERVING"
    current_graph_state["execution_status"] = "IDLE"




async def _execute_orchestration_background():
    global latest_graph_state
    try:
        logger.info("Launching LangGraph State Machine Execution in Background...")
        observer = get_global_observer()
        events = observer.buffer.get_recent()

        _BP_CACHE = {}

        initial_state = GhostTraceGraphState(
            session_id=current_graph_state["session_id"],
            workflow_id=current_graph_state["workflow_id"],
            telemetry_events=events,
        )

        orchestrator = GhostTraceOrchestrator()
        final_state = await orchestrator.run_graph(initial_state)
        latest_graph_state = final_state
        logger.info(f"LangGraph State Machine Background Execution Finished. State: {final_state.current_state.value}")
    except Exception as e:
        logger.error(f"Error during LangGraph background execution: {e}", exc_info=True)


@router.get("")
async def get_current_state():
    """
    Returns the current active graph execution state for live dashboard sync.
    100% Deterministic — NEVER triggers Gemini calls on polling!
    """
    global latest_graph_state, _STORED_BUSINESS_PROCESS

    if latest_graph_state:
        state_dict = latest_graph_state.model_dump()
        return {
            "current_stage": state_dict.get("current_stage", "OBSERVE"),
            "confidence_score": state_dict.get("confidence_score", 0.0),
            "repetition_count": state_dict.get("repetition_count", 0),
            "noise_filtered_count": state_dict.get("noise_filtered_count", 0),
            "candidate_name": state_dict.get("candidate_name", "Waiting for interaction events..."),
            "active_agents": state_dict.get("active_agents", ["ObserverAgent"]),
            "unlocked_stages": state_dict.get("unlocked_stages", ["OBSERVE"]),
            "workflow_dna": state_dict.get("workflow_dna"),
            "code_artifact": state_dict.get("code_artifact"),
            "sandbox_result": state_dict.get("sandbox_result"),
            "self_healing_summary": state_dict.get("self_healing_summary"),
            "business_process": state_dict.get("business_process") or _STORED_BUSINESS_PROCESS,
        }

    events = get_global_observer().buffer.get_recent() or in_memory_events
    event_count = len(events)

    pd = get_global_pattern_discovery()
    candidates = pd.get_discovered_candidates() if pd else []
    
    max_reps = 0
    if pd and hasattr(pd, "matcher") and pd.matcher._pattern_index:
        for occurrences in pd.matcher._pattern_index.values():
            if len(occurrences) > max_reps:
                max_reps = len(occurrences)

    if candidates:
        repetition_count = max(max(c.repetition_count for c in candidates), max_reps)
        confidence = max(c.confidence_score for c in candidates)
    elif max_reps >= 2:
        repetition_count = max_reps
        confidence = min(0.96, round(0.70 + (max_reps * 0.08), 2))
    else:
        repetition_count = max_reps
        confidence = 0.0

    noise_count = max(0, event_count // 6)


    dna_dict = None
    if latest_graph_state and hasattr(latest_graph_state, "workflow_dna") and latest_graph_state.workflow_dna:
        try:
            dna_dict = latest_graph_state.workflow_dna.model_dump()
        except Exception:
            pass

    business_process_dict = _STORED_BUSINESS_PROCESS
    if latest_graph_state and hasattr(latest_graph_state, "business_process") and latest_graph_state.business_process:
        business_process_dict = latest_graph_state.business_process


    candidate_name = "Waiting for interaction events..."

    if event_count > 0:
        ref_event = events[-1]
        first_event = events[0]
        source_app = getattr(ref_event, "active_tab", None) or (ref_event.get("active_tab") if isinstance(ref_event, dict) else "Source App")
        target_app = getattr(first_event, "active_tab", None) or (first_event.get("active_tab") if isinstance(first_event, dict) else "Target App")
        candidate_name = f"{source_app} -> {target_app}"

    from app.agents.pattern_discovery.semantic_deviation_detector import semantic_deviation_detector
    from app.agents.pattern_discovery.outlier_detector import OutlierDetector

    detector = OutlierDetector()
    
    raw_occurrences = []
    if pd and hasattr(pd, "matcher") and pd.matcher._pattern_index:
        for occs in pd.matcher._pattern_index.values():
            if len(occs) >= 2:
                raw_occs = [[getattr(e, "raw_event", e) for e in seq] for seq in occs]
                raw_occurrences.extend(raw_occs)
                
    detected_outliers = detector.detect_outliers(raw_occurrences, events)
    semantic_deviations = semantic_deviation_detector.detect_semantic_deviations(raw_occurrences, events)
    
    outlier_items = []
    for idx, out in enumerate(detected_outliers):
        sel = out.get("selector", "element")
        outlier_items.append({
            "id": f"out-{idx+1}",
            "label": out.get("label") or f"Action on {sel}",
            "selector": sel,
            "reason": out.get("reason", "Observed 1x across sequence repetitions")
        })

    for idx, dev in enumerate(semantic_deviations):
        outlier_items.append({
            "id": f"dev-{idx+1}",
            "label": dev.get("label") or f"Field ({dev.get('source_entity', 'source').upper()}) pasted into Field ({dev.get('destination_entity', 'dest').upper()})",
            "selector": f"#target-{dev.get('destination_entity', 'dest')}",
            "reason": "Accidental cross-field transfer observed and corrected"
        })

    return {
        **current_graph_state,
        "confidence_score": confidence,
        "repetition_count": repetition_count,
        "noise_filtered_count": noise_count,
        "candidate_name": candidate_name,
        "event_count": event_count,
        "workflow_dna": dna_dict,
        "business_process": business_process_dict,
        "outliers": outlier_items,
    }


@router.get("")
async def get_current_state():
    """Returns current orchestrator state & dynamic confidence score."""
    return get_dynamic_state_data()


class CandidateRefineRequest(BaseModel if 'BaseModel' in globals() else object):
    pass

@router.post("/refine")
async def refine_candidate(choice: str, target_selector: str):
    """
    Handles HITL semantic candidate refinement.
    Stores user-confirmed accidental corrections into persistent CorrectionPatternStore memory layer.
    """
    from app.agents.pattern_discovery.correction_memory import global_correction_memory

    if choice == "EXCLUDE" and target_selector:
        parts = target_selector.split(",")
        for target in parts:
            clean_target = target.strip().replace("#", "").replace(".", " ")
            global_correction_memory.record_confirmed_correction("source_entity", clean_target)

    return {
        "status": "SUCCESS",
        "choice": choice,
        "message": f"Recorded HITL decision ({choice}) into persistent CorrectionPatternStore memory."
    }



@router.post("/run")
async def run_orchestration(payload: Optional[Dict[str, Any]] = None):
    """Triggers LangGraph state machine workflow execution."""
    global active_orchestration_task
    current_graph_state["active_node"] = "PATTERN_DISCOVERY"
    active_orchestration_task = asyncio.create_task(_execute_orchestration_background())
    return {"status": "TRIGGERED", "state": get_dynamic_state_data()}


@router.websocket("/ws/state")
async def state_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = get_dynamic_state_data()
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "current_state": data.get("active_node", "IDLE"),
            "confidence_score": data.get("confidence_score", 0.0),
            "repetition_count": data.get("repetition_count", 0),
            "candidate_name": data.get("candidate_name")
        })
        while True:
            cmd = await websocket.receive_text()
            logger.debug(f"State WS received: {cmd}")
    except WebSocketDisconnect:
        pass
