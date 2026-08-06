import asyncio
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult
from app.agents.sandbox.runner import SubprocessRunner
from app.agents.self_healing import (
    SelfHealingAgent,
    FailureDiagnoser,
    GeminiRepairEngine,
    HealingRecord,
    HealingSummary,
    HealingPublisher,
)


def create_artifact_v1(code_str: str, name: str = "Test Script") -> CodeArtifact:
    return CodeArtifact(
        workflow_id="wf-heal-test-999",
        source_code=code_str,
        step_map={
            1: {
                "action_name": "Navigate to ERP",
                "function_name": "step_1_navigate",
                "selector": "#non-existent-btn",
                "line_start": 4,
                "line_end": 10
            }
        },
        metadata={"name": name, "version": 1}
    )


async def run_self_healing_verification():
    print("=== GhostTrace AI: Self-Healing Agent Verification ===")

    runner = SubprocessRunner()
    publisher = HealingPublisher()
    agent = SelfHealingAgent(runner=runner, publisher=publisher)

    published_records = []

    async def sample_healing_subscriber(record: HealingRecord, artifact: CodeArtifact):
        published_records.append((record, artifact))
        print(f"   [Healing Subscriber Received] Record ID={record.record_id[:8]} Attempt={record.attempt_number} Version={record.failing_version}->{record.repaired_version} Status={record.status}")

    publisher.subscribe(sample_healing_subscriber)
    assert publisher.subscriber_count() == 1, "Subscriber registration failed"

    # 1. Test Syntax Error Self-Healing (v1 -> v2 PASS)
    syntax_fail_code = """
import sys
async def step_1_navigate((page:
    sys.exit(0)
"""

    artifact_v1 = create_artifact_v1(syntax_fail_code, "Syntax Error Script")
    initial_res = await runner.execute_artifact(artifact_v1)
    assert initial_res.success is False

    summary_1, final_res_1, final_art_1 = await agent.heal_artifact(initial_res, artifact_v1, max_attempts=3)
    assert summary_1.overall_status == "PASS", f"Syntax error healing failed: {summary_1.overall_status}"


    assert summary_1.final_version == 2, f"Expected version 2, got {summary_1.final_version}"
    assert len(summary_1.repair_history) == 1
    assert artifact_v1.metadata["version"] == 1, "Original artifact v1 was modified!"
    print("[OK] Syntax Error Repair: Artifact v1 -> v2 resolved successfully, v1 preserved untouched.")

    # 2. Test Missing Selector Self-Healing (v1 -> v2 PASS)
    published_records.clear()
    selector_fail_code = """
import sys
target_sel = "#non-existent-btn"
if "non-existent" in target_sel:
    raise Exception("PlaywrightTimeoutError: selector '#non-existent-btn' not found")
sys.exit(0)
"""

    artifact_selector_v1 = create_artifact_v1(selector_fail_code, "Selector Error Script")
    initial_res_2 = await runner.execute_artifact(artifact_selector_v1)
    assert initial_res_2.success is False

    summary_2, final_res_2, final_art_2 = await agent.heal_artifact(initial_res_2, artifact_selector_v1, max_attempts=3)
    assert summary_2.overall_status == "PASS", "Selector error healing failed"


    assert summary_2.final_version == 2
    assert summary_2.repair_history[0].failing_step_name == "Navigate to ERP"
    print("[OK] Missing Selector Repair: Line traceback matched step_map to 'Navigate to ERP', selector replaced in v2.")

    # 3. Test Timeout Error Self-Healing (v1 -> v2 PASS)
    published_records.clear()
    timeout_fail_code = """
import sys
timeout = 30000
if timeout == 30000:
    sys.exit("ExecutionTimedOutError: Subprocess timed out after 30000ms")
sys.exit(0)
"""
    artifact_timeout_v1 = create_artifact_v1(timeout_fail_code, "Timeout Error Script")
    initial_res_3 = await runner.execute_artifact(artifact_timeout_v1)
    assert initial_res_3.success is False

    summary_3, final_res_3, final_art_3 = await agent.heal_artifact(initial_res_3, artifact_timeout_v1, max_attempts=3)
    
    assert summary_3.overall_status == "PASS", "Timeout error healing failed"
    assert "timeout = 60000" in final_art_3.source_code or "60000" in final_art_3.source_code
    print("[OK] Timeout Error Repair: Timeout parameters updated in v2 and sandbox passed.")


    # 4. Test Max Retry Budget Exceeded (3 retries -> FAIL)
    published_records.clear()
    unfixable_code = """
import sys
print("Permanent Failure")
sys.exit("Unfixable Error")
"""
    artifact_unfixable_v1 = create_artifact_v1(unfixable_code, "Unfixable Script")
    initial_res_4 = await runner.execute_artifact(artifact_unfixable_v1)
    assert initial_res_4.success is False

    summary_4, final_res_4, final_art_4 = await agent.heal_artifact(initial_res_4, artifact_unfixable_v1, max_attempts=3)
    
    assert summary_4.overall_status == "FAIL", "Unfixable script should result in FAIL summary"
    assert summary_4.total_attempts == 3, f"Expected 3 retries, executed {summary_4.total_attempts}"
    assert len(summary_4.repair_history) == 3
    assert len(published_records) == 3, f"Expected 3 published records, got {len(published_records)}"
    print("[OK] Max Retry Budget: Exactly 3 repair attempts executed (v1 -> v2 -> v3 -> v4), history preserved, FAIL returned.")

    print("\nPASSED: Self-Healing Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_self_healing_verification())
