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
            if len(run_set) > 1:
                for src in run_set:
                    is_known = global_correction_memory.is_known_accidental_correction(src, dest_key)

                    if is_known:
                        logger.info(f"Previously confirmed accidental correction pattern matched in memory: {src} -> {dest_key}. Applying confidence penalty for adaptive verification.")
                        reason_text = "Previously confirmed as accidental correction pattern. Lower confidence — verify if workflow intent changed."
                        confidence_penalty = 0.25
                    else:
                        reason_text = "Semantic mapping deviation observed in sequence cycle."
                        confidence_penalty = 0.0

                    deviations.append({
                        "id": f"dev-{len(deviations)+1}",
                        "source_entity": src,
                        "destination_entity": dest_key,
                        "label": f"Field ({src.upper()}) was pasted into Field ({dest_key.upper()})",
                        "reason": reason_text,
                        "confidence_penalty": confidence_penalty,
                        "is_known_memory": is_known
                    })


        logger.info(f"SemanticDeviationDetector evaluated {total_runs} cycles and detected {len(deviations)} semantic deviations.")
        return deviations


semantic_deviation_detector = SemanticDeviationDetector()
