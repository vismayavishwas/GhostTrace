import asyncio
import os
from typing import Optional
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult
from app.agents.compiler.publisher import CodePublisher
from app.agents.sandbox import SandboxRunnerAgent, SubprocessRunner, SandboxPublisher


def create_test_artifact(code_str: str, name: str = "Test Script") -> CodeArtifact:
    return CodeArtifact(
        workflow_id="wf-test-12345",
        source_code=code_str,
        step_map={1: {"action_name": "Test Action", "line_start": 1, "line_end": 5}},
        metadata={"name": name}
    )


async def run_sandbox_verification():
    print("=== GhostTrace AI: Sandbox Runner Agent Verification ===")

    code_pub = CodePublisher()
    sandbox_pub = SandboxPublisher()
    agent = SandboxRunnerAgent(code_publisher=code_pub, publisher=sandbox_pub)

    published_results = []

    async def sample_sandbox_subscriber(result: SandboxResult, artifact: Optional[CodeArtifact]):
        published_results.append((result, artifact))
        art_id = artifact.artifact_id[:8] if artifact else "None"
        print(f"   [Sandbox Subscriber Received] Result ID={result.execution_id[:8]} Success={result.success} Duration={result.duration_ms}ms Artifact={art_id}")

    sandbox_pub.subscribe(sample_sandbox_subscriber)
    assert sandbox_pub.subscriber_count() == 1, "Subscriber registration failed"

    # 1. Test Successful Subprocess Execution
    success_code = """
import sys
print("GHOSTTRACE_SANDBOX_SUCCESS_OUTPUT")
sys.exit(0)
"""
    artifact_1 = create_test_artifact(success_code, "Successful Script")
    await code_pub.publish(artifact_1)

    assert len(published_results) == 1, "SandboxResult should be emitted on completion"
    res_1, art_1 = published_results[0]
    
    assert res_1.success is True, "Successful execution failed"
    assert "GHOSTTRACE_SANDBOX_SUCCESS_OUTPUT" in res_1.stdout, f"Stdout mismatch: {res_1.stdout}"
    assert res_1.stderr == "", f"Stderr should be empty: {res_1.stderr}"
    assert len(res_1.artifacts) >= 1, "Temporary script path should be recorded in artifacts"
    assert art_1.artifact_id == artifact_1.artifact_id, "Artifact reference mismatch"
    print("[OK] Successful Execution: Exit code 0, stdout captured, empty stderr, script path preserved.")

    # 2. Test Failed Subprocess Execution (Captured Traceback & Failing Line)
    published_results.clear()
    fail_code = """
import sys
def failing_function():
    raise ValueError("Simulated Sandbox Runtime Exception")

failing_function()
"""
    artifact_2 = create_test_artifact(fail_code, "Failing Script")
    res_2 = await agent.run_sandbox(artifact_2)

    assert res_2.success is False, "Failed execution should report success=False"
    assert "ValueError: Simulated Sandbox Runtime Exception" in res_2.stderr, f"Stderr mismatch: {res_2.stderr}"
    assert res_2.error_traceback is not None, "Error traceback should be captured"
    assert res_2.failing_line is not None, "Failing line number should be parsed"
    assert len(res_2.artifacts) >= 1, "Temp script path should be preserved in artifacts"
    print(f"[OK] Failed Execution: Non-zero exit code captured, traceback on line {res_2.failing_line} recorded.")

    # 3. Test Infinite Loop & Process Timeout Termination
    published_results.clear()
    loop_code = """
import time
print("Loop started...")
while True:
    time.sleep(0.05)
"""
    artifact_3 = create_test_artifact(loop_code, "Hanging Script")
    res_3 = await agent.run_sandbox(artifact_3, timeout_sec=1.2)

    assert res_3.success is False, "Timeout execution should report success=False"
    assert "ExecutionTimedOutError" in res_3.stderr, f"Timeout stderr mismatch: {res_3.stderr}"
    print("[OK] Timeout Termination: Hanging process terminated gracefully by timeout.")

    # 4. Test SandboxResult JSON Serialization
    json_output = res_1.model_dump_json(indent=2)
    assert '"execution_id"' in json_output
    assert '"success"' in json_output
    assert '"artifacts"' in json_output
    print("[OK] JSON Serialization: SandboxResult model serializes to clean JSON matching schema.")

    print("\nPASSED: Sandbox Runner Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_sandbox_verification())
