import logging
from typing import List, Union, Dict, Any
from app.models.telemetry import TelemetryEvent
from app.agents.ghost_replay.models import ReplayFrame

logger = logging.getLogger("ghosttrace.ghost_replay.extractor")


class TrajectoryExtractor:
    """
    Extracts ordered, timestamped ReplayFrame objects from raw telemetry sequences.
    Preserves viewport dimensions, scroll offsets, and unique frame IDs for client-side interpolation.
    """
    def extract_trajectory(
        self,
        events: List[Union[TelemetryEvent, Dict[str, Any]]]
    ) -> List[ReplayFrame]:
        """
        Translates a list of TelemetryEvent instances or dictionaries into normalized ReplayFrames.
        """
        if not events:
            return []

        frames: List[ReplayFrame] = []
        
        # Sort events by timestamp if available
        def get_ts(e: Union[TelemetryEvent, Dict[str, Any]]) -> float:
            if isinstance(e, TelemetryEvent):
                return e.timestamp.timestamp() * 1000.0 if e.timestamp else 0.0
            elif isinstance(e, dict):
                ts = e.get("timestamp", 0)
                if isinstance(ts, (int, float)):
                    return float(ts)
                return 0.0
            return 0.0

        sorted_events = sorted(events, key=get_ts)
        start_ts = get_ts(sorted_events[0])

        for idx, event in enumerate(sorted_events):
            if isinstance(event, TelemetryEvent):
                raw_ts = event.timestamp.timestamp() * 1000.0 if event.timestamp else start_ts
                rel_ts = max(0.0, raw_ts - start_ts)
                
                meta = event.metadata or {}
                evt_type = event.event_type if isinstance(event.event_type, str) else event.event_type.value
                is_click = (str(evt_type).upper() == "CLICK")

                x_val = float(event.coordinates_x if event.coordinates_x is not None else getattr(event, "x", 0.0))
                y_val = float(event.coordinates_y if event.coordinates_y is not None else getattr(event, "y", 0.0))

                frame = ReplayFrame(
                    frame_index=idx,
                    timestamp_ms=round(rel_ts, 2),
                    x=x_val,
                    y=y_val,
                    viewport_width=int(meta.get("viewport_width", 1920)),
                    viewport_height=int(meta.get("viewport_height", 1080)),
                    scroll_x=float(meta.get("scroll_x", 0.0)),
                    scroll_y=float(meta.get("scroll_y", 0.0)),
                    event_type=str(evt_type),
                    target_selector=event.target_selector,
                    element_tag=event.element_tag,
                    is_click=is_click,
                    text_value=event.input_value
                )
            else:
                # Handle dictionary payload
                raw_ts = float(event.get("timestamp", start_ts))
                rel_ts = max(0.0, raw_ts - start_ts)
                evt_type = str(event.get("event_type", "mousemove"))
                is_click = (evt_type.upper() == "CLICK" or event.get("is_click", False))
                meta = event.get("metadata", event.get("element_metadata", {}))

                frame = ReplayFrame(
                    frame_index=idx,
                    timestamp_ms=round(rel_ts, 2),
                    x=float(event.get("coordinates_x", event.get("x", 0.0))),
                    y=float(event.get("coordinates_y", event.get("y", 0.0))),
                    viewport_width=int(meta.get("viewport_width", 1920)),
                    viewport_height=int(meta.get("viewport_height", 1080)),
                    scroll_x=float(meta.get("scroll_x", 0.0)),
                    scroll_y=float(meta.get("scroll_y", 0.0)),
                    event_type=evt_type,
                    target_selector=event.get("target_selector"),
                    element_tag=event.get("element_tag"),
                    is_click=is_click,
                    text_value=event.get("input_value", event.get("value"))
                )

            frames.append(frame)

        logger.info(f"TrajectoryExtractor extracted {len(frames)} ReplayFrame objects spanning {frames[-1].timestamp_ms if frames else 0}ms.")
        return frames
