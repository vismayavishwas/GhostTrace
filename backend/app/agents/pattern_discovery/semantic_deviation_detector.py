import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.telemetry import TelemetryEvent
from app.agents.pattern_discovery.correction_memory import global_correction_memory

logger = logging.getLogger("ghosttrace.pattern_discovery.semantic_deviation")


class SemanticDeviationDetector:
    """
    Semantic Deviation Detector.
    Compares observation cycles against baseline stable mappings and persistent CorrectionPatternStore.
    
    Behavior:
    1. If anomalous transfer matches a previously user-confirmed accidental correction in memory -> Auto-filters without prompting.
    2. If an unmatched out-of-baseline transfer occurs (e.g. Source Entity A -> Destination Entity B) -> Flags as a Semantic Deviation for HITL review.
    3. Never alters raw telemetry history.
    """

    def detect_semantic_deviations(
        self,
        occurrences: List[List[TelemetryEvent]],
        all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        deviations: List[Dict[str, Any]] = []
        if not occurrences or len(occurrences) < 2:
            return deviations

        total_runs = len(occurrences)
        run_entity_destinations: Dict[str, Set[str]] = {}
        entity_display_labels: Dict[str, str] = {}

        # 1. Map entity transfers across sequence runs
        for occ in occurrences:
            for evt in occ:
                raw_e = getattr(evt, "raw_event", evt)
                sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "").lower()
                etype = str(getattr(raw_e, "event_type", "ACTION")).upper()

                if "source" in sel:
                    source_key = sel.replace("#source-", "").replace("source-", "")
                    entity_display_labels[source_key] = source_key.upper()

                if "target" in sel and etype == "PASTE":
                    dest_key = sel.replace("#target-", "").replace("target-", "")
                    if dest_key not in run_entity_destinations:
                        run_entity_destinations[dest_key] = set()
                    run_entity_destinations[dest_key].add(dest_key)

        # 2. Check for anomalous out-of-baseline transfers across runs
        for dest_key, run_set in run_entity_destinations.items():
            # If target received conflicting sources or isolated transfers
            if len(run_set) > 1:
                for src in run_set:
                    # Check persistent memory layer first
                    if global_correction_memory.is_known_accidental_correction(src, dest_key):
                        logger.info(f"Auto-filtered known accidental correction pattern from memory: {src} -> {dest_key}")
                        continue

                    deviations.append({
                        "id": f"dev-{len(deviations)+1}",
                        "source_entity": src,
                        "destination_entity": dest_key,
                        "label": f"Field ({src.upper()}) was pasted into Field ({dest_key.upper()})",
                        "reason": f"Semantic mapping deviation observed in sequence cycle",
                        "is_known_memory": False
                    })

        logger.info(f"SemanticDeviationDetector evaluated {total_runs} cycles and detected {len(deviations)} semantic deviations.")
        return deviations


semantic_deviation_detector = SemanticDeviationDetector()
