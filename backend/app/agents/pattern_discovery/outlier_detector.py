import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.telemetry import TelemetryEvent
from app.services.gemini_service import GeminiService

from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label

logger = logging.getLogger("ghosttrace.pattern_discovery.outlier")


def format_human_label(event_type: str, selector: str, app_title: str) -> str:
    clean_sel = format_clean_entity_label(selector.replace("#", "").replace(".", " ").replace("-", " "))
    if not clean_sel or clean_sel == "Field":
        clean_sel = "UI Element"

    etype_str = event_type.upper()
    if "COPY" in etype_str:
        return f"Copied {clean_sel} from {app_title}"
    elif "PASTE" in etype_str or "TYPE" in etype_str:
        return f"Pasted into {clean_sel} in {app_title}"
    
    return f"{event_type.capitalize()} on {clean_sel}"


class OutlierDetector:
    """
    Context-Aware Multi-Signal Outlier Detector.
    Evaluates: Expected Mapping + Observed Mapping + Learning State + Repetition Frequency.
    """

    def detect_outliers(
        self, occurrences: List[List[TelemetryEvent]], all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        from app.agents.telemetry.semantic_normalizer import SemanticNormalizer
        from app.agents.pattern_discovery.mapping_memory import global_mapping_memory

        outliers: List[Dict[str, Any]] = []
        if not occurrences or len(occurrences) < 2:
            return outliers

        total_runs = len(occurrences)
        run_entity_counts: Dict[str, int] = {}
        entity_sample_events: Dict[str, TelemetryEvent] = {}

        # 1. Evaluate Expected vs Observed Mappings from Stable Mapping Memory
        for occ in occurrences:
            active_source = None
            for evt in occ:
                raw_e = getattr(evt, "raw_event", evt)
                sem = SemanticNormalizer.normalize(raw_e)
                if not sem:
                    continue

                entity_key = sem.semantic_entity
                entity_sample_events[entity_key] = raw_e

                if sem.operation in ["COPY", "SELECT"]:
                    active_source = sem.semantic_entity
                elif sem.operation in ["PASTE", "TYPE"] and active_source:
                    expected = global_mapping_memory.get_expected_destination(active_source)
                    observed = sem.semantic_entity.lower()
                    
                    if expected and expected.lower() != observed:
                        sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "element")
                        app_title = str(getattr(raw_e, "app_title", None) or getattr(raw_e, "active_tab", None) or "App")
                        label = format_human_label(sem.operation, sel, app_title)
                        exp_clean = format_clean_entity_label("", expected)
                        obs_clean = format_clean_entity_label("", observed)
                        outliers.append({
                            "id": f"out-map-{len(outliers)+1}",
                            "selector": sel,
                            "event_type": sem.operation,
                            "label": label,
                            "reason": f"Expected mapping mismatch: Expected '{exp_clean}' but observed '{obs_clean}'",
                            "app_title": app_title,
                        })

                if entity_key not in run_entity_counts:
                    run_entity_counts[entity_key] = 0
                run_entity_counts[entity_key] += 1

        # 2. Auxiliary Frequency Mining: Flag isolated actions occurring in only 1 run out of N
        for entity_key, run_count in run_entity_counts.items():
            if run_count == 1 and total_runs >= 2:
                sample_e = entity_sample_events.get(entity_key)
                sel = str(getattr(sample_e, "target_selector", None) or getattr(sample_e, "element_tag", None) or "element") if sample_e else "element"
                if not any(o["selector"] == sel for o in outliers):
                    etype = str(getattr(sample_e, "event_type", "ACTION")) if sample_e else "ACTION"
                    app_title = str(getattr(sample_e, "app_title", None) or getattr(sample_e, "active_tab", None) or "App") if sample_e else "App"
                    label = format_human_label(etype, sel, app_title)

                    outliers.append({
                        "id": f"out-freq-{len(outliers)+1}",
                        "selector": sel,
                        "event_type": etype,
                        "label": label,
                        "reason": f"Isolated action observed in 1 of {total_runs} sequence runs",
                        "app_title": app_title,
                    })

        logger.info(
            f"OutlierDetector evaluated {total_runs} repetition runs "
            f"and flagged {len(outliers)} multi-signal outliers."
        )

        return outliers


outlier_detector = OutlierDetector()


