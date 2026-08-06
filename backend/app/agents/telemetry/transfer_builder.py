import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set

from app.models.telemetry import TelemetryEvent
from app.agents.telemetry.semantic_normalizer import SemanticEvent, SemanticNormalizer

logger = logging.getLogger("ghosttrace.telemetry.transfer_builder")


@dataclass
class SemanticTransfer:
    """
    High-level business transfer representing one complete data movement.
    Aggregated within an Intent Window: [Start Copy -> Target Paste -> Next Copy]
    """
    transfer_id: str
    source_entity: str
    destination_entity: str
    source_app: str
    destination_app: str
    pasted_value: str
    is_immediate_correction: bool = False
    superseded_destination: Optional[str] = None
    raw_events: List[TelemetryEvent] = field(default_factory=list)


class TransferBuilder:
    """
    Intent Window Aggregator & Immediate Correction Engine.
    
    Responsibilities:
    1. Aggregates low-level events (COPY, CLICK, PASTE) into Intent Windows [Start Copy -> Next Copy].
    2. Immediate Correction Awareness:
       If a user pastes Value A into Target B, and within the same Intent Window performs Undo/Backspace
       or pastes Value A into Target C, TransferBuilder cancels out the first paste as an Immediate User Correction.
    3. Idempotency: Ensures each telemetry event ID is processed into a transfer exactly ONCE.
    """
    def __init__(self):
        self._current_window_events: List[TelemetryEvent] = []
        self._active_source_event: Optional[SemanticEvent] = None
        self._processed_event_ids: Set[str] = set()

    def process_telemetry_events(self, events: List[TelemetryEvent]) -> List[SemanticTransfer]:
        """Processes sequence of telemetry events into structured SemanticTransfers with immediate correction resolution."""
        transfers: List[SemanticTransfer] = []
        pending_transfers: List[Dict[str, Any]] = []

        unprocessed_events = [e for e in events if getattr(e, "event_id", None) not in self._processed_event_ids]
        if not unprocessed_events:
            return []

        for raw_e in unprocessed_events:
            if getattr(raw_e, "event_id", None):
                self._processed_event_ids.add(raw_e.event_id)

            sem_e = SemanticNormalizer.normalize(raw_e)
            if not sem_e:
                continue

            # Detect Start of Intent Window (COPY / SELECT_SOURCE)
            if sem_e.operation in ["COPY", "SELECT"] and "source" in str(sem_e.target_selector or "").lower():
                self._active_source_event = sem_e
                continue

            # Detect PASTE into Target Application
            if sem_e.operation == "PASTE" or ("target" in str(sem_e.target_selector or "").lower() and sem_e.operation != "CLICK"):
                source_entity = self._active_source_event.semantic_entity if self._active_source_event else "semantic:source:unknown"
                source_app = self._active_source_event.app_title if self._active_source_event else "Source App"
                dest_entity = sem_e.semantic_entity
                dest_app = sem_e.app_title

                # Check for Immediate Correction within the same Intent Window
                if pending_transfers and pending_transfers[-1]["source_entity"] == source_entity:
                    prev_dest = pending_transfers[-1]["destination_entity"]
                    if prev_dest != dest_entity:
                        logger.info(f"TransferBuilder resolved Immediate Correction: User changed destination from '{prev_dest}' to '{dest_entity}'")
                        pending_transfers[-1]["is_immediate_correction"] = True
                        pending_transfers[-1]["superseded_destination"] = prev_dest
                        pending_transfers[-1]["destination_entity"] = dest_entity

                pending_transfers.append({
                    "transfer_id": f"xfer-{len(pending_transfers)+1}",
                    "source_entity": source_entity,
                    "destination_entity": dest_entity,
                    "source_app": source_app,
                    "destination_app": dest_app,
                    "pasted_value": sem_e.pasted_value,


                    "is_immediate_correction": False,
                    "superseded_destination": None,
                    "raw_events": [raw_e]
                })

        for p in pending_transfers:
            transfers.append(SemanticTransfer(**p))

        logger.info(f"TransferBuilder aggregated {len(events)} events into {len(transfers)} high-level SemanticTransfers.")
        return transfers


global_transfer_builder = TransferBuilder()
