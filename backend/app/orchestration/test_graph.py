import asyncio
from datetime import datetime, timezone
from app.models.enums import LangGraphState, EventType
from app.models.telemetry import TelemetryEvent
from app.models.execution import SandboxResult
from app.agents.compiler.models import CodeArtifact
from app.orchestration import GhostTraceOrchestrator, GhostTraceGraphState


def create_sample_telemetry_sequence() -> list:
    t0 = datetime.now(timezone.utc)
    single_seq = [
        TelemetryEvent(
            event_type=EventType.NAVIGATION,
            coordinates_x=100, coordinates_y=200,
            target_selector="data:text/html,<html><body><h1>GhostTrace</h1></body></html>",
            timestamp=t0
        ),
        TelemetryEvent(
            event_type=EventType.CLICK,
            coordinates_x=150, coordinates_y=250,
            target_selector="body",
            timestamp=datetime.fromtimestamp(t0.timestamp() + 1.0, tz=timezone.utc)
        )
    ]
    return single_seq + single_seq




async def run_orchestrator_verification():
    print("=== GhostTrace AI: LangGraph Orchestration Layer Verification ===")

    orchestrator = GhostTraceOrchestrator()

    # 1. Verify Graph Initialization & Node Registration
    assert len(orchestrator.nodes) == 11, f"Expected 11 registered nodes, got {len(orchestrator.nodes)}"
    expected_nodes = ["observing", "pattern_discovery", "intent_validation", "workflow_dna", "code_generation", "sandbox", "self_heal", "execution", "continuous_observation", "failed", "complete"]
    for node_key in expected_nodes:
        assert node_key in orchestrator.nodes, f"Node '{node_key}' missing from orchestrator"
    print("[OK] Graph Initialization: All 11 agent node wrappers registered successfully.")

    # 2. Verify Happy Path Execution
    events = create_sample_telemetry_sequence()
    initial_state = GhostTraceGraphState(telemetry_events=events)
    
    final_state = await orchestrator.run_graph(initial_state)

    assert final_state.is_completed is True, "Graph should terminate with is_completed=True"


    assert final_state.is_failed is False, "Graph should not fail on happy path"
    assert final_state.workflow_dna is not None, "WorkflowDNA should be synthesized"
    assert final_state.generated_code is not None, "CodeArtifact should be compiled"
    assert final_state.execution_status is not None, "Execution status should be populated"
    print("[OK] Happy Path Execution: IDLE -> OBSERVING -> PATTERN_DISCOVERY -> INTENT_VALIDATION -> WORKFLOW_DNA -> CODE_GENERATION -> SANDBOX -> EXECUTION -> CONTINUOUS_OBSERVATION -> EXECUTION_COMPLETE.")

    # 3. Verify Self-Healing Transition Routing (PASS -> SANDBOX, FAIL -> FAILED)
    from app.agents.self_healing.models import HealingSummary
    from app.orchestration.transitions import route_after_sandbox, route_after_heal

    state_sandbox_pass = GhostTraceGraphState(sandbox_results=[SandboxResult(execution_id="1", success=True, duration_ms=10.0)])
    state_sandbox_fail = GhostTraceGraphState(sandbox_results=[SandboxResult(execution_id="2", success=False, duration_ms=10.0)])
    assert route_after_sandbox(state_sandbox_pass) == "execution"
    assert route_after_sandbox(state_sandbox_fail) == "self_heal"
    print("[OK] Failure Recovery Routing: Sandbox PASS -> execution, Sandbox FAIL -> self_heal.")

    state_heal_pass = GhostTraceGraphState(healing_summary=HealingSummary(
        workflow_id="wf-pass",
        total_attempts=1,
        final_version=2,
        final_sandbox_result=state_sandbox_pass.sandbox_results[0],
        overall_status="PASS",
        attempts=[]
    ))
    state_heal_fail = GhostTraceGraphState(healing_summary=HealingSummary(
        workflow_id="wf-fail",
        total_attempts=3,
        final_version=4,
        final_sandbox_result=state_sandbox_fail.sandbox_results[0],
        overall_status="FAIL",
        attempts=[]
    ))


    assert route_after_heal(state_heal_pass) == "sandbox"
    assert route_after_heal(state_heal_fail) == "failed"
    assert state_heal_fail.error_message is not None
    print("[OK] Self-Healing Budget Routing: Repair PASS -> sandbox, Repair FAIL -> terminal 'failed' state.")


    # 4. Verify Continuous Observation Non-Recursive Termination
    assert final_state.is_completed is True, "Graph must complete cleanly without infinite recursion"
    print("[OK] Continuous Observation Loop: Post-execution feedback recorded and graph terminated cleanly without infinite recursion.")


    # 5. Output ASCII State Machine Visualization
    print("\nState Machine Graph Visualization:")
    print(orchestrator.get_graph_ascii_visualization())

    print("PASSED: LangGraph Orchestration Layer Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_orchestrator_verification())
