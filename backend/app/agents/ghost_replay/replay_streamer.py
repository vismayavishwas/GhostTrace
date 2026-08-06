import logging
from typing import List, Optional, Tuple, Dict, Any
from app.agents.ghost_replay.models import ReplayFrame, ReplaySessionState

logger = logging.getLogger("ghosttrace.ghost_replay.streamer")

VALID_SPEEDS = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]


class ReplayStreamer:
    """
    Manages session playback state, timeline seeking, speed multiplier scaling (0.25x to 4x),
    and fast-forwarding ('Skip to Next Click') for ghost replay visual demonstrations.
    """
    def __init__(self, workflow_id: str, frames: List[ReplayFrame]):
        self.workflow_id = workflow_id
        self.frames: List[ReplayFrame] = sorted(frames, key=lambda f: f.timestamp_ms)
        self.total_duration_ms: float = self.frames[-1].timestamp_ms if self.frames else 0.0
        
        self.state = ReplaySessionState(
            workflow_id=workflow_id,
            status="IDLE",
            speed_multiplier=1.0,
            current_time_ms=0.0,
            total_duration_ms=self.total_duration_ms,
            total_frames=len(self.frames),
            current_frame_index=0
        )

    def play(self) -> ReplaySessionState:
        """Starts or resumes playback."""
        self.state.status = "PLAYING"
        logger.info(f"ReplayStreamer started session ID={self.state.session_id[:8]} at {self.state.current_time_ms}ms")
        return self.state

    def pause(self) -> ReplaySessionState:
        """Pauses playback."""
        self.state.status = "PAUSED"
        logger.info(f"ReplayStreamer paused session ID={self.state.session_id[:8]} at {self.state.current_time_ms}ms")
        return self.state

    def stop(self) -> ReplaySessionState:
        """Stops playback and resets scrubber position to 0ms."""
        self.state.status = "STOPPED"
        self.state.current_time_ms = 0.0
        self.state.current_frame_index = 0
        logger.info(f"ReplayStreamer stopped session ID={self.state.session_id[:8]}")
        return self.state

    def set_speed(self, multiplier: float) -> ReplaySessionState:
        """Sets playback speed multiplier (0.25x, 0.5x, 1.0x, 1.5x, 2.0x, 4.0x)."""
        if multiplier in VALID_SPEEDS:
            self.state.speed_multiplier = multiplier
        else:
            # Clamp to nearest valid speed
            self.state.speed_multiplier = min(VALID_SPEEDS, key=lambda s: abs(s - multiplier))
        
        logger.info(f"ReplayStreamer set speed to {self.state.speed_multiplier}x")
        return self.state

    def seek_to_time(self, target_time_ms: float) -> Tuple[ReplaySessionState, Optional[ReplayFrame]]:
        """Seeks to a specific timestamp in milliseconds and returns closest active ReplayFrame."""
        clamped_time = max(0.0, min(self.total_duration_ms, target_time_ms))
        self.state.current_time_ms = clamped_time

        active_frame = self._get_frame_at_time(clamped_time)
        if active_frame:
            self.state.current_frame_index = active_frame.frame_index

        logger.debug(f"ReplayStreamer seeked to {clamped_time}ms (Frame index {self.state.current_frame_index})")
        return self.state, active_frame

    def skip_to_next_click(self) -> Tuple[ReplaySessionState, Optional[ReplayFrame]]:
        """
        Fast-forwards directly to the timestamp of the next click frame (is_click == True).
        Allows demo users to skip idle mouse movements smoothly.
        """
        current_idx = self.state.current_frame_index
        next_click_frame: Optional[ReplayFrame] = None

        for frame in self.frames[current_idx + 1:]:
            if frame.is_click:
                next_click_frame = frame
                break

        if next_click_frame:
            return self.seek_to_time(next_click_frame.timestamp_ms)
        else:
            # If no further click events exist, jump to end of sequence
            return self.seek_to_time(self.total_duration_ms)

    def _get_frame_at_time(self, time_ms: float) -> Optional[ReplayFrame]:
        """Finds closest ReplayFrame at or before time_ms."""
        if not self.frames:
            return None
        
        active = self.frames[0]
        for frame in self.frames:
            if frame.timestamp_ms <= time_ms:
                active = frame
            else:
                break
        return active
