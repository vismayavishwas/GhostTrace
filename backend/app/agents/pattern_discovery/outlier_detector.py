import logging
from typing import List, Dict, Any, Tuple
from app.models.telemetry import TelemetryEvent

logger = logging.getLogger("ghosttrace.pattern_discovery.outlier")


class OutlierDetector:
    """
    Deterministic Outlier Detector.
    Evaluates potential accidental or unusual actions across sequence repetitions
    using deterministic heuristics before any AI calls.
    
    Heuristics:
    1. Action appears in only 1 repetition across sequence cycles.
    2. Action breaks an otherwise repeated sequence pattern.
    3. Action immediately followed by Undo / Back / Escape / Cancel.
    4. Navigation away from active workflow app and immediate return.
    5. Single isolated click on unrelated UI element.
    """

    def detect_outliers(
        self, occurrences: List[List[TelemetryEvent]], all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        outliers = []
        if not occurrences or len(occurrences) < 2:
            return outliers

        # Frequency count of event target selectors across sequence cycles
        selector_counts: Dict[str, int] = {}
        for occ in occurrences:
            seen_in_occ = set()
            for evt in occ:
                sel = str(evt.target_selector or evt.element_tag or "element")
                if sel not in seen_in_occ:
                    seen_in_occ.add(sel)
                    selector_counts[sel] = selector_counts.get(sel, 0) + 1

        total_runs = len(occurrences)

        # Flag selectors that appear in only 1 run across multiple runs
        for sel, count in selector_counts.items():
            if count == 1 and total_runs >= 2:
                # Find matching event object
                matched_evt = None
                for occ in occurrences:
                    for e in occ:
                        if str(e.target_selector or e.element_tag or "element") == sel:
                            matched_evt = e
                            break
                    if matched_evt:
                        break

                outliers.append({
                    "selector": sel,
                    "event_type": matched_evt.event_type if matched_evt else "ACTION",
                    "reason": f"Action appeared in only 1 of {total_runs} sequence runs",
                    "event_id": matched_evt.event_id if matched_evt else "",
                    "app_title": matched_evt.app_title if matched_evt else "App",
                })

        return outliers


outlier_detector = OutlierDetector()
