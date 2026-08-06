import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.telemetry import TelemetryEvent
from app.services.gemini_service import GeminiService

logger = logging.getLogger("ghosttrace.pattern_discovery.outlier")


def format_human_label(event_type: str, selector: str, app_title: str) -> str:
    sel_lower = selector.lower()
    
    if "f1" in sel_lower or "invoiceid" in sel_lower or "name" in sel_lower or "customer" in sel_lower:
        field_name = "Record ID / Candidate Name"
    elif "f2" in sel_lower or "amount" in sel_lower or "cgpa" in sel_lower or "email" in sel_lower:
        field_name = "Amount / Contact Info"
    elif "f3" in sel_lower or "vendor" in sel_lower or "experience" in sel_lower or "dealsize" in sel_lower:
        field_name = "Vendor Name / Deal Size"
    else:
        field_name = selector.replace("#", "").replace(".", " ")

    if "source" in sel_lower:
        return f"Copied {field_name} from Source App"
    elif "target" in sel_lower:
        return f"Pasted {field_name} into {app_title}"
    elif event_type == "COPY":
        return f"Copied text from {app_title}"
    elif event_type == "PASTE":
        return f"Pasted text into {app_title}"
    
    return f"{event_type.capitalize()} on {field_name}"


class OutlierDetector:
    """
    Context-Aware Outlier Detector using Frequency Mining & Gemini AI Reasoning.
    
    Evaluation Rules:
    1. Pattern Core: Selectors appearing consistently across sequence cycles are Core Pattern Steps.
    2. Anomalous Outlier: A business target action that appears in ONLY 1 run (isolated mistake).
    3. Noise Filtering: Raw DOM element click noise (spans, container divs) is excluded from business workflow outliers.
    """

    def __init__(self):
        self.gemini = GeminiService(primary_model="gemini-2.0-flash")

    def detect_outliers(
        self, occurrences: List[List[TelemetryEvent]], all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        outliers: List[Dict[str, Any]] = []
        if not occurrences or len(occurrences) < 2:
            return outliers

        total_runs = len(occurrences)

        # Count frequency of target selectors across sequence repetition runs
        run_selector_counts: Dict[str, int] = {}
        selector_sample_events: Dict[str, TelemetryEvent] = {}

        for occ in occurrences:
            seen_in_run: Set[str] = set()
            for evt in occ:
                raw_e = getattr(evt, "raw_event", evt)
                sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "")

                # Focus strictly on business form fields and actions (source, target, inputs, buttons)
                if sel and any(k in sel.lower() for k in ["source", "target", "f1", "f2", "f3", "input", "button"]):
                    selector_sample_events[sel] = raw_e
                    if sel not in seen_in_run:
                        seen_in_run.add(sel)
                        run_selector_counts[sel] = run_selector_counts.get(sel, 0) + 1

        # Identify selectors that appear in ONLY 1 run out of N total sequence runs (Isolated Mistakes)
        for sel, run_count in run_selector_counts.items():
            if run_count == 1 and total_runs >= 2:
                sample_e = selector_sample_events.get(sel)
                etype = str(getattr(sample_e, "event_type", "ACTION")) if sample_e else "ACTION"
                app_title = str(getattr(sample_e, "app_title", None) or getattr(sample_e, "active_tab", None) or "App") if sample_e else "App"

                label = format_human_label(etype, sel, app_title)

                outliers.append({
                    "id": f"out-{len(outliers)+1}",
                    "selector": sel,
                    "event_type": etype,
                    "label": label,
                    "reason": f"Isolated action observed in 1 of {total_runs} sequence runs",
                    "app_title": app_title,
                })

        logger.info(
            f"OutlierDetector evaluated {total_runs} repetition runs ({len(run_selector_counts)} distinct target selectors) "
            f"and flagged {len(outliers)} dynamic anomalous outliers."
        )

        return outliers


outlier_detector = OutlierDetector()


