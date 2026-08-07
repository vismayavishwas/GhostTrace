import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, List


from app.models.enums import EventType
from app.models.telemetry import TelemetryEvent
from app.agents.observer.buffer import TelemetryBuffer
from app.agents.observer.publisher import TelemetryPublisher

logger = logging.getLogger("ghosttrace.observer")


class ObserverAgent:
    """
    Observer Agent responsible for ingesting raw perception telemetry,
    normalizing fields, validating against TelemetryEvent schema,
    buffering in memory, and broadcasting to downstream subscribers.
    """
    def __init__(
        self,
        buffer_capacity: int = 1000,
        buffer: Optional[TelemetryBuffer] = None,
        publisher: Optional[TelemetryPublisher] = None,
    ):
        self.buffer: TelemetryBuffer = buffer or TelemetryBuffer(capacity=buffer_capacity)
        self.publisher: TelemetryPublisher = publisher or TelemetryPublisher()
        self._last_event: Optional[TelemetryEvent] = None
        logger.info(f"ObserverAgent initialized with buffer capacity={self.buffer.capacity}")

    def rehydrate_from_records(self, records: List[Dict[str, Any]]) -> List[TelemetryEvent]:
        """Pre-loads recent telemetry records into the ring buffer on backend startup."""
        rehydrated: List[TelemetryEvent] = []
        for rec in records:
            evt = self._normalize_and_validate(rec)
            if evt:
                self.buffer.append(evt)
                rehydrated.append(evt)
        logger.info(f"ObserverAgent rehydrated {len(rehydrated)} events into ring buffer.")
        return rehydrated

    async def process_raw_event(self, raw_input: Union[str, Dict[str, Any]]) -> Optional[TelemetryEvent]:

        """
        Ingests a raw telemetry payload (JSON string or dictionary), normalizes fields,
        validates against TelemetryEvent schema, buffers, and publishes.
        
        Returns validated TelemetryEvent or None if input was malformed.
        """
        raw_dict = self._parse_to_dict(raw_input)
        if raw_dict is None:
            logger.warning("ObserverAgent dropped malformed payload: Could not parse input into dictionary")
            return None

        event = self._normalize_and_validate(raw_dict)
        if event is None:
            logger.warning(f"ObserverAgent dropped invalid event payload: {raw_dict}")
            return None

        # Event Deduplication: Drop synthetic DOM event bubbling clicks on the same element within 250ms
        if self._last_event:
            same_type = (event.event_type == self._last_event.event_type)
            same_target = (event.target_selector == self._last_event.target_selector)
            time_delta = (event.timestamp - self._last_event.timestamp).total_seconds()
            if same_type and same_target and abs(time_delta) < 0.25:
                logger.debug(f"ObserverAgent dropped duplicate bubbling event ID={event.event_id}")
                return None
        self._last_event = event

        # Store in ring buffer
        self.buffer.append(event)
        
        # Broadcast to subscribers
        await self.publisher.publish(event)
        
        logger.debug(f"ObserverAgent processed & published TelemetryEvent ID={event.event_id} Type={event.event_type}")
        return event

    def _parse_to_dict(self, raw_input: Union[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parses string or dictionary inputs into a raw python dictionary."""
        if isinstance(raw_input, dict):
            return raw_input
        if isinstance(raw_input, str):
            try:
                data = json.loads(raw_input)
                if isinstance(data, dict):
                    return data
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    def _normalize_and_validate(self, raw_dict: Dict[str, Any]) -> Optional[TelemetryEvent]:
        """
        Normalizes raw telemetry fields and constructs a validated TelemetryEvent Pydantic instance.
        """
        try:
            # 1. Normalize Event Type
            raw_type = str(raw_dict.get("event_type", raw_dict.get("type", "CLICK"))).upper()
            try:
                event_type = EventType(raw_type)
            except ValueError:
                # Default unknown type mapping fallback
                event_type = EventType.CLICK

            # 2. Normalize Coordinates
            coords_x = raw_dict.get("coordinates_x", raw_dict.get("x"))
            coords_y = raw_dict.get("coordinates_y", raw_dict.get("y"))
            
            # 3. Normalize Timestamp
            raw_ts = raw_dict.get("timestamp")
            timestamp = self._parse_timestamp(raw_ts)

            # 4. Construct TelemetryEvent model
            event = TelemetryEvent(
                event_type=event_type,
                timestamp=timestamp,
                coordinates_x=int(coords_x) if coords_x is not None else None,
                coordinates_y=int(coords_y) if coords_y is not None else None,
                target_selector=raw_dict.get("target_selector", raw_dict.get("selector")),
                element_tag=raw_dict.get("element_tag", raw_dict.get("tag")),
                input_value=raw_dict.get("input_value", raw_dict.get("value")),
                dom_snapshot=raw_dict.get("dom_snapshot", raw_dict.get("html")),
                app_title=raw_dict.get("app_title") or raw_dict.get("title") or "Unknown Application",
                metadata=raw_dict.get("metadata", {})
            )
            return event

        except Exception as e:
            logger.error(f"ObserverAgent normalization failed: {e}", exc_info=False)
            return None

    def _parse_timestamp(self, raw_ts: Any) -> datetime:
        """Parses ISO timestamp strings or numeric timestamps into UTC datetime."""
        if isinstance(raw_ts, str):
            try:
                return datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except ValueError:
                pass
        elif isinstance(raw_ts, (int, float)):
            try:
                return datetime.fromtimestamp(raw_ts, tz=timezone.utc)
            except (ValueError, OSError):
                pass
        return datetime.now(timezone.utc)
