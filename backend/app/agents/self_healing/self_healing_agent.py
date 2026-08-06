import logging
from typing import Optional, List, Tuple
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult
from app.agents.sandbox.runner import SubprocessRunner
from app.agents.sandbox.publisher import SandboxPublisher
from app.agents.self_healing.models import HealingRecord, HealingSummary, FailureDiagnosis
from app.agents.self_healing.diagnoser import FailureDiagnoser
from app.agents.self_healing.gemini_repair import GeminiRepairEngine
from app.agents.self_healing.publisher import HealingPublisher

logger = logging.getLogger("ghosttrace.self_healing")


class SelfHealingAgent:
    """
    Self-Healing Agent responsible for diagnosing sandbox failures, isolating error tracebacks
    with FailureDiagnoser, generating versioned CodeArtifacts (v1 -> v2 -> v3) via GeminiRepairEngine,
    re-running sandbox validation, and maintaining a complete repair evolution history.
    """
    def __init__(
        self,
        diagnoser: Optional[FailureDiagnoser] = None,
        repair_engine: Optional[GeminiRepairEngine] = None,
        runner: Optional[SubprocessRunner] = None,
        sandbox_publisher: Optional[SandboxPublisher] = None,
        publisher: Optional[HealingPublisher] = None,
    ):
        self.diagnoser = diagnoser or FailureDiagnoser()
        self.repair_engine = repair_engine or GeminiRepairEngine()
        self.runner = runner or SubprocessRunner()
        self.publisher = publisher or HealingPublisher()

        if sandbox_publisher:
            sandbox_publisher.subscribe(self.on_sandbox_result)
            logger.info("SelfHealingAgent subscribed to SandboxPublisher")

    async def on_sandbox_result(
        self,
        result: SandboxResult,
        artifact: Optional[CodeArtifact] = None
    ) -> Optional[HealingSummary]:
        """Callback executed upon receiving a SandboxResult from the Sandbox Runner."""
        if result.success or artifact is None:
            logger.debug(f"SelfHealingAgent skipped: Sandbox result passed or artifact is None.")
            return None

        summary, _, _ = await self.heal_artifact(result, artifact)
        return summary

    async def heal_artifact(
        self,
        initial_result: SandboxResult,
        initial_artifact: CodeArtifact,
        max_attempts: int = 3
    ) -> Tuple[HealingSummary, SandboxResult, CodeArtifact]:
        """
        Executes self-healing loop for up to max_attempts.
        Preserves original CodeArtifact untouched and creates versioned artifacts (v2, v3, etc.).
        Returns (HealingSummary, final_sandbox_result, final_code_artifact).
        """
        logger.info(
            f"SelfHealingAgent initiated healing loop for Artifact ID={initial_artifact.artifact_id[:8]} "
            f"MaxAttempts={max_attempts}"
        )

        current_artifact = initial_artifact
        current_result = initial_result
        repair_history: List[HealingRecord] = []

        for attempt in range(1, max_attempts + 1):
            failing_ver = current_artifact.metadata.get("version", attempt)
            logger.info(f"--- Self-Healing Attempt {attempt}/{max_attempts} (Failing Version v{failing_ver}) ---")

            # 1. Diagnose Failure (Separated Diagnosis)
            diagnosis: FailureDiagnosis = self.diagnoser.diagnose_failure(current_result, current_artifact)

            # 2. Synthesize Repaired Versioned CodeArtifact
            repaired_artifact, model_log = self.repair_engine.repair_code(diagnosis, current_artifact)
            repaired_ver = repaired_artifact.metadata.get("version", failing_ver + 1)

            # 3. Re-execute Repaired Code in Isolated Sandbox
            new_result = await self.runner.execute_artifact(repaired_artifact)




            # 4. Record Healing Audit
            record = HealingRecord(
                attempt_number=attempt,
                workflow_id=current_artifact.workflow_id,
                failing_artifact_id=current_artifact.artifact_id,
                repaired_artifact_id=repaired_artifact.artifact_id,
                failing_version=failing_ver,
                repaired_version=repaired_ver,
                failing_line=diagnosis.failing_line,
                failing_step_name=diagnosis.failing_step_name,
                original_traceback=current_result.error_traceback or current_result.stderr,
                patched_traceback=None if new_result.success else (new_result.error_traceback or new_result.stderr),
                repair_prompt=diagnosis.repair_prompt,
                model_output=model_log,
                status="PASS" if new_result.success else "FAIL"
            )

            repair_history.append(record)

            # Broadcast healing record and versioned artifact
            await self.publisher.publish(record, repaired_artifact)

            if new_result.success:
                logger.info(
                    f"🎉 Self-Healing PASSED on Attempt {attempt}/{max_attempts}! "
                    f"Version v{repaired_ver} (Artifact ID={repaired_artifact.artifact_id[:8]}) executed successfully."
                )
                summary = HealingSummary(
                    workflow_id=current_artifact.workflow_id,
                    overall_status="PASS",
                    total_attempts=attempt,
                    final_version=repaired_ver,
                    repair_history=repair_history,
                    final_sandbox_result=new_result
                )
                return summary, new_result, repaired_artifact

            # If execution failed again, prepare for next iteration
            logger.warning(
                f"Attempt {attempt}/{max_attempts} (v{repaired_ver}) failed. "
                f"Preparing retry..."
            )
            current_artifact = repaired_artifact
            current_result = new_result

        # Max retries budget exhausted
        logger.error(
            f"[FAILED] Self-Healing EXHAUSTED after {max_attempts} attempts. "
            f"Final version v{current_artifact.metadata.get('version', max_attempts+1)} failed."
        )


        final_summary = HealingSummary(
            workflow_id=initial_artifact.workflow_id,
            overall_status="FAIL",
            total_attempts=max_attempts,
            final_version=current_artifact.metadata.get("version", max_attempts + 1),
            repair_history=repair_history,
            final_sandbox_result=current_result
        )

        return final_summary, current_result, current_artifact
