import inspect
import logging
from typing import Callable, List, Union, Awaitable, Tuple, Optional
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult

logger = logging.getLogger("ghosttrace.sandbox.publisher")

# Sandbox callback accepts SandboxResult and optional CodeArtifact
SandboxCallback = Callable[[SandboxResult, Optional[CodeArtifact]], Union[None, Awaitable[None]]]


class SandboxPublisher:
    """
    Publisher distributing SandboxResult objects and associated CodeArtifact metadata to subscribers
    (Self-Healing Agent, Production Worker, Orchestrator, Dashboard).
    """
    def __init__(self):
        self._subscribers: List[SandboxCallback] = []

    def subscribe(self, callback: SandboxCallback) -> None:
        """Registers a sandbox subscriber callback."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered sandbox subscriber: {callback.__name__}")

    def unsubscribe(self, callback: SandboxCallback) -> None:
        """Unregisters a subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered sandbox subscriber: {callback.__name__}")

    async def publish(self, result: SandboxResult, artifact: Optional[CodeArtifact] = None) -> None:
        """Publishes SandboxResult and CodeArtifact to subscribers."""
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(result, artifact)
                else:
                    callback(result, artifact)
            except Exception as e:
                logger.error(f"Error in sandbox subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns subscriber count."""
        return len(self._subscribers)
