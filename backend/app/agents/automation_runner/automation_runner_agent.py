import asyncio
import logging
from typing import Optional, Dict, List, Tuple, Any
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult
from app.agents.automation_runner.executor import PlaywrightExecutor
from app.agents.automation_runner.publisher import AutomationPublisher

logger = logging.getLogger("ghosttrace.automation_runner")


class AutomationRunnerAgent:
    """
    Automation Runner Agent responsible for orchestrating production Playwright execution
    for validated CodeArtifact instances, tracking cancellation events, streaming progress updates,
    and enforcing browser lifecycle cleanup.
    """
    def __init__(
        self,
        executor: Optional[PlaywrightExecutor] = None,
        publisher: Optional[AutomationPublisher] = None,
    ):
        self.publisher = publisher or AutomationPublisher()
        self.executor = executor or PlaywrightExecutor(publisher=self.publisher)
        self._active_tokens: Dict[str, asyncio.Event] = {}
        self._execution_history: List[SandboxResult] = []

    async def run_automation(
        self,
        artifact: CodeArtifact,
        input_params: Optional[Dict[str, Any]] = None
    ) -> SandboxResult:
        """
        Executes a validated CodeArtifact in production mode.
        Registers cancellation token and tracks execution history.
        """
        execution_id = artifact.artifact_id
        cancel_token = asyncio.Event()
        self._active_tokens[execution_id] = cancel_token

        logger.info(f"AutomationRunnerAgent starting execution ID={execution_id[:8]} for Workflow ID={artifact.workflow_id[:8]}")

        try:
            result = await self.executor.execute_artifact(
                artifact=artifact,
                input_params=input_params,
                cancellation_token=cancel_token
            )
            self._execution_history.append(result)
            return result
        finally:
            if execution_id in self._active_tokens:
                del self._active_tokens[execution_id]

    def cancel_execution(self, execution_id: str) -> bool:
        """
        Triggers cancellation for an active execution run by setting its cancellation token.
        Returns True if active run was found and flagged, False otherwise.
        """
        if execution_id in self._active_tokens:
            self._active_tokens[execution_id].set()
            logger.info(f"AutomationRunnerAgent flagged cancellation for Execution ID={execution_id[:8]}")
            return True
        logger.warning(f"AutomationRunnerAgent failed to cancel: Execution ID={execution_id[:8]} not active")
        return False

    def get_execution_history(self) -> List[SandboxResult]:
        """Returns history of executed SandboxResult models."""
        return list(self._execution_history)
