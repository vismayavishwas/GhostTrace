import logging
from typing import Optional, List, Tuple
from app.agents.compiler.models import CodeArtifact
from app.agents.compiler.publisher import CodePublisher
from app.models.execution import SandboxResult
from app.agents.sandbox.runner import SubprocessRunner
from app.agents.sandbox.publisher import SandboxPublisher

logger = logging.getLogger("ghosttrace.sandbox")


class SandboxRunnerAgent:
    """
    Sandbox Runner Agent responsible for executing CodeArtifact objects in isolated
    subprocesses, managing execution timeouts, capturing stdout/stderr/tracebacks,
    recording script file artifacts, and broadcasting SandboxResults.
    """
    def __init__(
        self,
        runner: Optional[SubprocessRunner] = None,
        code_publisher: Optional[CodePublisher] = None,
        publisher: Optional[SandboxPublisher] = None,
    ):
        self.runner = runner or SubprocessRunner()
        self.publisher = publisher or SandboxPublisher()
        self._execution_history: List[Tuple[SandboxResult, CodeArtifact]] = []

        if code_publisher:
            code_publisher.subscribe(self.on_code_artifact)
            logger.info("SandboxRunnerAgent subscribed to CodePublisher")

    async def on_code_artifact(self, artifact: CodeArtifact) -> SandboxResult:
        """Callback executed upon receiving a CodeArtifact from the Compiler Agent."""
        return await self.run_sandbox(artifact)

    async def run_sandbox(
        self,
        artifact: CodeArtifact,
        timeout_sec: Optional[float] = None
    ) -> SandboxResult:
        """
        Executes a CodeArtifact in the isolated subprocess runner and broadcasts the result.
        """
        logger.info(f"SandboxRunnerAgent executing Artifact ID={artifact.artifact_id[:8]} for Workflow ID={artifact.workflow_id[:8]}")

        result = await self.runner.execute_artifact(artifact, timeout_sec=timeout_sec)
        self._execution_history.append((result, artifact))

        # Broadcast SandboxResult and CodeArtifact to subscribers (Self-Healing / Execution)
        await self.publisher.publish(result, artifact)
        return result

    def get_execution_history(self) -> List[Tuple[SandboxResult, CodeArtifact]]:
        """Returns execution history of (SandboxResult, CodeArtifact) pairs."""
        return list(self._execution_history)
