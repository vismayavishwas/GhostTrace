import logging
from typing import Optional, Dict, List, Any
from app.models.telemetry import TelemetryEvent
from app.agents.ghost_replay.models import ReplayFrame, ReplaySessionState
from app.agents.ghost_replay.path_extractor import TrajectoryExtractor
from app.agents.ghost_replay.replay_streamer import ReplayStreamer
from app.agents.ghost_replay.publisher import ReplayPublisher

logger = logging.getLogger("ghosttrace.ghost_replay")


class GhostReplayAgent:
    """
    Ghost Replay Agent responsible for extracting normalized timestamped ReplayFrames,
    managing session playback state, enabling skip-to-next-click navigation, and streaming
    frames for client-side smooth animation.
    """
    def __init__(
        self,
        extractor: Optional[TrajectoryExtractor] = None,
        publisher: Optional[ReplayPublisher] = None,
    ):
        self.extractor = extractor or TrajectoryExtractor()
        self.publisher = publisher or ReplayPublisher()
        self._active_streamers: Dict[str, ReplayStreamer] = {}

    def create_replay_session(
        self,
        workflow_id: str,
        events: List[Any]
    ) -> ReplayStreamer:
        """
        Extracts trajectory from telemetry events and creates a ReplayStreamer instance.
        """
        frames = self.extractor.extract_trajectory(events)
        streamer = ReplayStreamer(workflow_id, frames)
        self._active_streamers[workflow_id] = streamer
        
        logger.info(f"GhostReplayAgent created replay session for Workflow ID={workflow_id[:8]} with {len(frames)} frames.")
        return streamer

    def get_streamer(self, workflow_id: str) -> Optional[ReplayStreamer]:
        """Retrieves active ReplayStreamer for a workflow ID."""
        return self._active_streamers.get(workflow_id)

    def get_frames(self, workflow_id: str) -> List[ReplayFrame]:
        """Returns list of ReplayFrames for a given session."""
        streamer = self.get_streamer(workflow_id)
        return streamer.frames if streamer else []
