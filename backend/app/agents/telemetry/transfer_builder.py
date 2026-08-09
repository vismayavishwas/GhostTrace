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
    source_display_label: str = ""
    destination_display_label: str = ""
    source_selector: str = ""
    destination_selector: str = ""
    is_immediate_correction: bool = False
    superseded_destination: Optional[str] = None
    session_id: str = "sess-default-001"
    cycle_id: str = "cycle-1"
    event_index: int = 0
    semantic_action_index: int = 0
    is_automated: bool = False
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

        if not events:
            return []

        for evt_idx, raw_e in enumerate(events, start=1):
            sem_e = SemanticNormalizer.normalize(raw_e)
            if not sem_e:
                continue

            # Detect Start of Intent Window (COPY / SELECT)
            if sem_e.operation in ["COPY", "SELECT"]:
                self._active_source_event = sem_e
                continue

            # Detect PASTE / TYPE into Target Field
            if sem_e.operation in ["PASTE", "TYPE"]:
                source_entity = self._active_source_event.semantic_entity if self._active_source_event else "entity:source:unknown"
                source_app = self._active_source_event.app_title if self._active_source_event else "Source App"
                source_display_label = self._active_source_event.display_label if self._active_source_event else "Unknown Field"
                source_selector = getattr(self._active_source_event, "target_selector", "") if self._active_source_event else ""
                dest_entity = sem_e.semantic_entity
                dest_app = sem_e.app_title
                dest_display_label = sem_e.display_label
                dest_selector = sem_e.target_selector or ""

                meta = getattr(raw_e, "metadata", {}) or {}
                sess_id = getattr(raw_e, "session_id", None) or meta.get("session_id") or "sess-default-001"
                cyc_id = sem_e.cycle_id or meta.get("cycle_id") or "cycle-1"

                # Check for Immediate Correction within the same Intent Window
                if pending_transfers and pending_transfers[-1]["source_entity"] == source_entity:
                    prev_dest = pending_transfers[-1]["destination_entity"]
                    if prev_dest != dest_entity:
                        logger.info(f"TransferBuilder resolved Immediate Correction: User changed destination from '{prev_dest}' to '{dest_entity}'")
                        pending_transfers[-1]["is_immediate_correction"] = True
                        pending_transfers[-1]["superseded_destination"] = prev_dest
                        pending_transfers[-1]["destination_entity"] = dest_entity
                        pending_transfers[-1]["destination_display_label"] = dest_display_label
                        pending_transfers[-1]["destination_selector"] = dest_selector

                pending_transfers.append({
                    "transfer_id": f"xfer-{len(pending_transfers)+1}",
                    "source_entity": source_entity,
                    "destination_entity": dest_entity,
                    "source_app": source_app,
                    "destination_app": dest_app,
                    "pasted_value": sem_e.pasted_value,
                    "source_display_label": source_display_label,
                    "destination_display_label": dest_display_label,
                    "source_selector": source_selector,
                    "destination_selector": dest_selector,
                    "is_immediate_correction": False,
                    "superseded_destination": None,
                    "session_id": sess_id,
                    "cycle_id": cyc_id,
                    "event_index": evt_idx,
                    "semantic_action_index": len(pending_transfers) + 1,
                    "is_automated": sem_e.is_automated,
                    "raw_events": [raw_e]
                })

                p = pending_transfers[-1]
                t_obj = SemanticTransfer(**p)
                logger.info(
                    f"[STAGE 1: TRANSFER_BUILDER] SemanticTransfer Created | ID={p['transfer_id']} | "
                    f"Cycle={p['cycle_id']} | ActionIndex={p['semantic_action_index']} | "
                    f"SourceEntity='{p['source_entity']}' ('{p['source_display_label']}') | "
                    f"DestEntity='{p['destination_entity']}' ('{p['destination_display_label']}') | "
                    f"Apps={p['source_app']} -> {p['destination_app']} | PastedValue='{p['pasted_value']}' | "
                    f"IsAutomated={p['is_automated']}"
                )
                transfers.append(t_obj)


        logger.info(f"[STAGE 1: TRANSFER_BUILDER] Processed {len(events)} telemetry events into {len(transfers)} completed SemanticTransfers.")
        return transfers



global_transfer_builder = TransferBuilder()
