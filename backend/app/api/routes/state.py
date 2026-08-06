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

        
        initial_state = GhostTraceGraphState(
            session_id=current_graph_state["session_id"],
            workflow_id=current_graph_state["workflow_id"],
            telemetry_events=events,
        )

        orchestrator = GhostTraceOrchestrator()
        final_state = await orchestrator.run_graph(initial_state)
        latest_graph_state = final_state
        current_graph_state["active_node"] = str(final_state.current_state.value).upper()
        current_graph_state["execution_status"] = "COMPLETED" if final_state.is_completed else "FAILED"
        logger.info(f"LangGraph State Machine Background Execution Finished. State: {current_graph_state['active_node']}")
    except Exception as e:
        logger.error(f"Error during LangGraph background execution: {e}", exc_info=True)


def get_dynamic_state_data() -> Dict[str, Any]:
    observer = get_global_observer()
    events = observer.buffer.get_recent()

    event_count = len(events) or len(in_memory_events)

    business_process_dict = None
    if event_count < 4:
        confidence = 0.0
        repetition_count = 0
        noise_count = 0
        candidate_name = "Waiting for repeated actions..."
    else:
        repetition_count = max(1, event_count // 4)
        noise_count = max(0, event_count // 6)
        confidence = min(0.97, round(0.50 + (repetition_count * 0.15), 2))

        ref_event = events[-1].model_dump() if events else in_memory_events[-1]
        first_event = events[0].model_dump() if events else in_memory_events[0]
        source_app = ref_event.get("active_tab") or ref_event.get("app_title") or "Source App"
        target_app = first_event.get("active_tab") or first_event.get("app_title") or "Target App"
        candidate_name = f"{source_app} → {target_app}"

        try:
            from app.agents.business_process import business_process_agent
            step_titles = []
            raw_items = events or in_memory_events
            for e in raw_items[:8]:
                evt_type = getattr(e, "event_type", None) or (e.get("event_type") if isinstance(e, dict) else "ACTION")
                selector = getattr(e, "target_selector", None) or (e.get("target_selector") if isinstance(e, dict) else "element")
                step_titles.append(f"{evt_type} on {selector}")

            meta = business_process_agent.analyze_process(candidate_name, step_titles, source_app, target_app, repetition_count=repetition_count)
            business_process_dict = meta.model_dump()
            candidate_name = meta.workflow_name
        except Exception as e:
            logger.warning(f"Error extracting business process metadata: {e}")



    dna_dict = None
    if latest_graph_state and latest_graph_state.workflow_dna:
        dna_dict = latest_graph_state.workflow_dna.model_dump()

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
