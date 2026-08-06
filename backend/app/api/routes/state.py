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


def reset_graph_state():
    global latest_graph_state, current_graph_state
    latest_graph_state = None
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
    if candidates:
        repetition_count = max(c.repetition_count for c in candidates)
        confidence = max(c.confidence_score for c in candidates)
    else:
        repetition_count = 0
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


    if event_count > 0:
        ref_event = events[-1]
        first_event = events[0]
        source_app = getattr(ref_event, "active_tab", None) or (ref_event.get("active_tab") if isinstance(ref_event, dict) else "Source App")
        target_app = getattr(first_event, "active_tab", None) or (first_event.get("active_tab") if isinstance(first_event, dict) else "Target App")
        candidate_name = f"{source_app} → {target_app}"

    return {
        **current_graph_state,
        "confidence_score": confidence,
        "repetition_count": repetition_count,
        "noise_filtered_count": noise_count,
        "candidate_name": candidate_name,
        "event_count": event_count,
        "workflow_dna": dna_dict,
        "business_process": business_process_dict,
    }




@router.get("")
async def get_current_state():
    """Returns current orchestrator state & dynamic confidence score."""
    return get_dynamic_state_data()


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
