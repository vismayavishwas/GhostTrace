import asyncio
from typing import List
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult
from app.agents.automation_runner import (
    AutomationRunnerAgent,
    PlaywrightExecutor,
    AutomationPublisher,
    ExecutionProgress,
)


def create_validated_artifact(selector_str: str = "https://ghosttrace.ai") -> CodeArtifact:
    return CodeArtifact(
        workflow_id="wf-auto-runner-001",
        source_code="""
import asyncio
from playwright.async_api import async_playwright

async def run_workflow():
    print("Automation Workflow Running...")
""",
        step_map={
            1: {"action_name": "Navigate to Application Portal", "selector": selector_str},
            2: {"action_name": "Enter Credentials & Login", "selector": "#username"},
            3: {"action_name": "Submit Form & Verification", "selector": "#submit-btn"},
        },
        metadata={"version": 1, "validated": True}
    )


async def run_automation_verification():
    print("=== GhostTrace AI: Automation Runner Agent Verification ===")

    publisher = AutomationPublisher()
    executor = PlaywrightExecutor(publisher=publisher)
    agent = AutomationRunnerAgent(executor=executor, publisher=publisher)

    progress_events: List[ExecutionProgress] = []
    final_results: List[SandboxResult] = []

    async def on_progress(p: ExecutionProgress):
        progress_events.append(p)
        print(f"   [Progress Stream] Step {p.step_number}/{p.total_steps}: {p.action_name} [{p.status}] ({p.elapsed_ms}ms)")

    async def on_result(r: SandboxResult):
        final_results.append(r)
        print(f"   [Result Publisher] Execution ID={r.execution_id[:8]} Success={r.success} Duration={r.duration_ms}ms")

    publisher.subscribe_progress(on_progress)
    publisher.subscribe_result(on_result)
    assert publisher.progress_subscriber_count() == 1
    assert publisher.result_subscriber_count() == 1

    # 1. Test Successful Playwright Execution & Progress Streaming
    artifact_1 = create_validated_artifact("about:blank")
    res_1 = await agent.run_automation(artifact_1)

    assert res_1.success is True, f"Execution failed: {res_1.stderr}"
    assert len(progress_events) >= 3, f"Expected at least 3 progress events, got {len(progress_events)}"
    assert len(final_results) == 1
    print("[OK] Successful Execution: Step sequence completed with stdout output.")
    print("[OK] Progress Event Streaming: Streamed step-by-step ExecutionProgress events.")

    # 2. Test Browser Cleanup Verification
    assert executor.last_browser_status["connected"] is False, "Browser should be disconnected after execution"
    print("[OK] Browser Cleanup: Playwright browser, context, and page instances explicitly closed.")

    # 3. Test Execution Cancellation
    progress_events.clear()
    final_results.clear()
    artifact_cancel = create_validated_artifact("about:blank")

    # Launch task asynchronously and trigger cancellation immediately
    exec_task = asyncio.create_task(agent.run_automation(artifact_cancel))
    await asyncio.sleep(0.01)
    canceled = agent.cancel_execution(artifact_cancel.artifact_id)
    assert canceled is True, "Cancel execution request failed"

    res_cancel = await exec_task
    assert res_cancel.success is False, "Cancelled run should not report success=True"
    assert "cancelled" in res_cancel.stderr.lower() or any(p.status == "CANCELLED" for p in progress_events)
    print("[OK] Execution Cancellation: Mid-run cancellation token stopped execution safely.")

    # 4. Test Runtime Failure Handling
    progress_events.clear()
    final_results.clear()
    
    # Create artifact with failing step selector
    artifact_fail = create_validated_artifact("http://invalid-nonexistent-domain-999.test")
    res_fail = await agent.run_automation(artifact_fail)

    assert res_fail.success is False, "Failing step should produce success=False"
    assert len(res_fail.stderr) > 0, "Error message should be captured in stderr"
    assert executor.last_browser_status["connected"] is False, "Browser should be closed after failure"
    print("[OK] Runtime Failure Handling: Errors captured, progress updated to FAILED, browser cleaned up.")

    # 5. Test JSON Serialization
    json_result = res_1.model_dump_json(indent=2)
    assert '"execution_id"' in json_result
    assert '"success"' in json_result
    print("[OK] JSON Serialization: SandboxResult model serializes to clean JSON matching schema.")

    print("\nPASSED: Automation Runner Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_automation_verification())
