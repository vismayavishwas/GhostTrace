import inspect
import logging
from typing import Callable, List, Union, Awaitable
from app.agents.compiler.models import CodeArtifact

logger = logging.getLogger("ghosttrace.compiler.publisher")

CodeCallback = Callable[[CodeArtifact], Union[None, Awaitable[None]]]


class CodePublisher:
    """
    Publisher distributing synthesized CodeArtifact objects to downstream subscribers
    (Sandbox Runner, Orchestrator, Monaco Editor Dashboard).
    """
    def __init__(self):
        self._subscribers: List[CodeCallback] = []

    def subscribe(self, callback: CodeCallback) -> None:
        """Registers a subscriber callback to receive CodeArtifacts."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            logger.debug(f"Registered code subscriber: {callback.__name__}")

    def unsubscribe(self, callback: CodeCallback) -> None:
        """Unregisters a subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            logger.debug(f"Unregistered code subscriber: {callback.__name__}")

    async def publish(self, artifact: CodeArtifact) -> None:
        """Publishes a CodeArtifact object to all registered subscribers."""
        for callback in self._subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(artifact)
                else:
                    callback(artifact)
            except Exception as e:
                logger.error(f"Error in code subscriber {callback.__name__}: {e}", exc_info=True)

    def subscriber_count(self) -> int:
        """Returns active subscriber count."""
        return len(self._subscribers)
