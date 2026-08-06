import inspect
import logging
from typing import Callable, List, Union, Awaitable, Tuple, Optional
from app.agents.ghost_replay.models import ReplayFrame, ReplaySessionState

logger = logging.getLogger("ghosttrace.ghost_replay.publisher")

FrameCallback = Callable[[ReplayFrame], Union[None, Awaitable[None]]]
StateCallback = Callable[[ReplaySessionState], Union[None, Awaitable[None]]]


class ReplayPublisher:
    """
    Publisher distributing timestamped ReplayFrame streams and ReplaySessionState updates
    to downstream subscribers (WebSockets, UI Dashboard).
    """
    def __init__(self):
        self._frame_subscribers: List[FrameCallback] = []
        self._state_subscribers: List[StateCallback] = []

    def subscribe_frame(self, callback: FrameCallback) -> None:
        """Registers a frame subscriber."""
        if callback not in self._frame_subscribers:
            self._frame_subscribers.append(callback)
            logger.debug(f"Registered replay frame subscriber: {callback.__name__}")

    def subscribe_state(self, callback: StateCallback) -> None:
        """Registers a session state subscriber."""
        if callback not in self._state_subscribers:
            self._state_subscribers.append(callback)
            logger.debug(f"Registered replay state subscriber: {callback.__name__}")

    async def publish_frame(self, frame: ReplayFrame) -> None:
        """Publishes a single ReplayFrame."""
        for callback in self._frame_subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(frame)
                else:
                    callback(frame)
            except Exception as e:
                logger.error(f"Error in frame subscriber {callback.__name__}: {e}", exc_info=True)

    async def publish_state(self, state: ReplaySessionState) -> None:
        """Publishes ReplaySessionState updates."""
        for callback in self._state_subscribers:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(state)
                else:
                    callback(state)
            except Exception as e:
                logger.error(f"Error in state subscriber {callback.__name__}: {e}", exc_info=True)

    def frame_subscriber_count(self) -> int:
        return len(self._frame_subscribers)

    def state_subscriber_count(self) -> int:
        return len(self._state_subscribers)
