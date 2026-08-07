import asyncio
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
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

    from app.orchestration.nodes import get_global_continuous_observer
    c_observer = get_global_continuous_observer()
    completed_cycles = 0
    if c_observer and hasattr(c_observer, "discovery_engine"):
        completed_cycles = c_observer.discovery_engine.get_completed_cycle_count()

    pd = get_global_pattern_discovery()
    candidates = pd.get_discovered_candidates() if pd else []
    if not candidates and c_observer:
        candidates = c_observer.get_candidates()

    if completed_cycles > 0:
        repetition_count = completed_cycles
    elif candidates:
        repetition_count = max(c.repetition_count for c in candidates)
    else:
        repetition_count = 0

    from app.agents.pattern_discovery.mapping_memory import global_mapping_memory
    confidence, mapping_status = global_mapping_memory.get_overall_semantic_consistency_confidence(repetition_count)






    candidate_name = getattr(candidates[0], "name", None) or getattr(candidates[0], "workflow_name", None) or "Enterprise Cross-App Workflow" if candidates else "Enterprise Cross-App Workflow"


    # Build dynamic field mappings from telemetry transfers in chronological order
    from app.agents.telemetry.transfer_builder import global_transfer_builder
    from app.agents.pattern_discovery.deviation_detector import global_deviation_detector, format_clean_entity_label

    chronological_events = list(reversed(events)) if events else []
    transfers = global_transfer_builder.process_telemetry_events(chronological_events) if chronological_events else []
    field_mappings = []
    for xfer in transfers:
        if xfer.is_immediate_correction:
            continue
        src_lbl = format_clean_entity_label("", xfer.source_entity)
        dest_lbl = format_clean_entity_label("", xfer.destination_entity)
        field_mappings.append({
            "transfer_id": xfer.transfer_id,
            "source_label": src_lbl,
            "destination_label": dest_lbl,
            "source_app": xfer.source_app,
            "destination_app": xfer.destination_app,
            "pasted_value": xfer.pasted_value,
            "display_mapping": f"{src_lbl} → {dest_lbl}"
        })

    # Detect mistake deviations on ANY cycle when transfers exist
    outlier_items = []
    if transfers:
        detected_devs = global_deviation_detector.detect_deviations(transfers)
        outlier_items = detected_devs


    dna_dict = None
    if candidates or field_mappings:
        try:
            from app.agents.workflow_dna.dna_transformer import DNATransformer
            from app.models.workflow import WorkflowCandidate
            transformer = DNATransformer()
            cand = candidates[0] if candidates else WorkflowCandidate(
                candidate_id="cand-dynamic-001",
                name=candidate_name,
                sequence=events,
                repetition_count=max(1, repetition_count),
                confidence_score=confidence
            )
            dna_model = transformer.transform_candidate(cand)
            dna_dict = dna_model.model_dump()
        except Exception as e:
            logger.warning(f"Error creating WorkflowDNA in state: {e}")

    if not dna_dict or not dna_dict.get("metadata", {}).get("field_mappings"):
        if dna_dict:
            dna_dict.setdefault("metadata", {})["field_mappings"] = field_mappings
            dna_dict["field_mappings"] = field_mappings
        else:
            dna_dict = {
                "name": candidate_name,
                "description": "Dynamic semantic workflow mapping human-understood field flows.",
                "field_mappings": field_mappings,
                "metadata": {"field_mappings": field_mappings}
            }

    business_process_dict = None
    if repetition_count >= 1:
        try:
            from app.agents.business_process.business_agent import business_process_agent
            step_strs = [f"{getattr(e, 'event_type', 'ACTION')} on {getattr(e, 'target_selector', 'element')}" for e in events[:5]]
            bp_meta = business_process_agent.analyze_process(
                candidate_name=candidate_name,
                steps=step_strs,
                source_app=field_mappings[0]["source_app"] if field_mappings else "PDF Portal",
                target_app=field_mappings[-1]["destination_app"] if field_mappings else "ERP System",
                repetition_count=repetition_count,
                avg_duration_sec=12.5
            )
            business_process_dict = bp_meta.model_dump()
            _STORED_BUSINESS_PROCESS = business_process_dict
        except Exception as e:
            logger.warning(f"Error calling BusinessProcessAgent: {e}")

    from app.agents.pattern_discovery.learning_planner import global_learning_planner
    lp_conf = getattr(global_learning_planner, "current_confidence", 0.0)

    import os, subprocess
    try:
        build_commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=os.path.dirname(__file__)).decode().strip()
    except Exception:
        build_commit = "75f63e5"

    logger.info(
        f"🔍 [STATE POLL AUDIT] Commit={build_commit} | MappingMemoryConf={confidence:.2f} | "
        f"LearningPlannerConf={lp_conf:.2f} | StateConfidence={round(confidence, 2):.2f} | "
        f"DetectorActiveOutliers={len(outlier_items)} | StateReturnedOutliers={len(outlier_items)}"
    )

    return {
        **current_graph_state,
        "build_commit": build_commit,
        "confidence_score": round(confidence, 2),
        "repetition_count": repetition_count,
        "noise_filtered_count": len([e for e in events if getattr(e, "event_type", "") == "NOISE"]),
        "candidate_name": candidate_name,
        "event_count": event_count,
        "workflow_dna": dna_dict,
        "field_mappings": field_mappings,
        "business_process": business_process_dict,
        "outliers": outlier_items,
    }


async def get_dynamic_state_data():
    """Alias for state calculation used by websocket and triggers."""
    return await get_current_state()


class CandidateRefinePayload(BaseModel):
    choice: str = "EXCLUDE"
    target_selector: str = ""

@router.post("/refine")
async def refine_candidate(payload: CandidateRefinePayload):
    """
    Handles HITL semantic candidate refinement.
    Resolves active deviations in global_deviation_detector and stores user-confirmed accidental corrections into persistent CorrectionPatternStore memory layer.
    """
    choice = str(payload.choice or "EXCLUDE").upper()
    target_selector = str(payload.target_selector or "")


    from app.agents.pattern_discovery.correction_memory import global_correction_memory
    from app.agents.pattern_discovery.deviation_detector import global_deviation_detector
    from app.agents.pattern_discovery.mapping_memory import global_mapping_memory

    if target_selector:
        global_deviation_detector.resolve_selectors(target_selector.split(","))
    global_deviation_detector.resolve_all_current()

    if choice == "EXCLUDE" and target_selector:
        parts = target_selector.split(",")
        for target in parts:
            clean_target = target.strip().replace("#", "").replace(".", " ")
            global_correction_memory.record_confirmed_correction("source_entity", clean_target)

    dyn_conf, _ = global_mapping_memory.get_overall_semantic_consistency_confidence(2)

    logger.info(
        f"✨ [STATE REFINE HITL] Handled choice={choice} on selector='{target_selector}'. "
        f"Updated confidence: {dyn_conf:.2f}. Active resolved_selectors count: {len(global_deviation_detector.resolved_selectors)}"
    )

    return {
        "status": "SUCCESS",
        "choice": choice,
        "action": choice,
        "target_selector": target_selector,
        "new_confidence": dyn_conf,
        "version": 2,
        "outliers": [],
        "message": f"Recorded HITL decision ({choice}) into persistent CorrectionPatternStore & resolved active deviations."
    }





@router.post("/run")
async def run_orchestration(payload: Optional[Dict[str, Any]] = None):
    """Triggers LangGraph state machine workflow execution."""
    global active_orchestration_task
    current_graph_state["active_node"] = "PATTERN_DISCOVERY"
    active_orchestration_task = asyncio.create_task(_execute_orchestration_background())
    state_data = await get_dynamic_state_data()
    return {"status": "TRIGGERED", "state": state_data}


@router.websocket("/ws/state")
async def state_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await get_dynamic_state_data()
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
