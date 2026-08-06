import inspect
import logging
from typing import Callable, List, Union, Awaitable, Tuple, Optional
from app.agents.automation_runner.progress import ExecutionProgress
from app.models.execution import SandboxResult

logger = logging.getLogger("ghosttrace.automation_runner.publisher")

ProgressCallback = Callable[[ExecutionProgress], Union[None, Awaitable[None]]]
ResultCallback = Callable[[SandboxResult], Union[None, Awaitable[None]]]


class AutomationPublisher:
    """
    Publisher emitting real-time ExecutionProgress events and final SandboxResults
    to downstream subscribers (Dashboard UI, Orchestrator, Analytics).
    """
    def __init__(self):
        self._progress_subscribers: List[ProgressCallback] = []
        self._result_subscribers: List[ResultCallback] = []

    def subscribe_progress(self, callback: ProgressCallback) -> None:
        """Registers a progress update subscriber callback."""
        if callback not in self._progress_subscribers:
            self._progress_subscribers.append(callback)
            logger.debug(f"Registered progress subscriber: {callback.__name__}")

    def subscribe_result(self, callback: ResultCallback) -> None:
        """Registers a final result subscriber callback."""
        if callback not in self._result_subscribers:
            self._result_subscribers.append(callback)
            logger.debug(f"Registered result subscriber: {callback.__name__}")

    async def publish_progress(self, progress: ExecutionProgress) -> None:
        """Publishes an ExecutionProgress event to subscribers."""
        for callback in self._progress_subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(progress)
                else:
                    callback(progress)
            except Exception as e:
                logger.error(f"Error in progress subscriber {callback.__name__}: {e}", exc_info=True)

    async def publish_result(self, result: SandboxResult) -> None:
        """Publishes final SandboxResult to subscribers."""
        for callback in self._result_subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in result subscriber {callback.__name__}: {e}", exc_info=True)

    def progress_subscriber_count(self) -> int:
        """Returns active progress subscribers count."""
        return len(self._progress_subscribers)

    def result_subscriber_count(self) -> int:
        """Returns active result subscribers count."""
        return len(self._result_subscribers)
