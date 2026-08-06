import logging
from typing import List, Dict, Any, Set
from app.models.telemetry import TelemetryEvent

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
        field_name = "Form Field"

    if "source" in sel_lower:
        return f"Copied {field_name} from Source App"
    elif "target" in sel_lower:
        return f"Pasted {field_name} into {app_title}"
    elif "button" in sel_lower:
        if "emerald" in sel_lower or "cyan" in sel_lower or "next" in sel_lower:
            return f"Clicked Next Record Button in {app_title}"
        return f"Clicked Action Button in {app_title}"
    elif "span" in sel_lower or "div" in sel_lower:
        return f"Clicked Workspace Area in {app_title}"
    elif event_type == "COPY":
        return f"Copied text from {app_title}"
    elif event_type == "PASTE":
        return f"Pasted text into {app_title}"
    
    return f"{event_type.capitalize()} action in {app_title}"


class OutlierDetector:
    """
    Context-Aware Outlier Detector.
    Strictly evaluates stray or anomalous actions that deviate from the core repeating pattern cycle.
    Valid steps in the repeating workflow sequence are NEVER flagged as outliers.
    """

    def detect_outliers(
        self, occurrences: List[List[TelemetryEvent]], all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        outliers: List[Dict[str, Any]] = []
        if not all_events or not occurrences or len(occurrences) < 2:
            return outliers

        # 1. Build set of target selectors that form the core repeating workflow sequence
        core_pattern_selectors: Set[str] = set()
        for occ in occurrences:
            for evt in occ:
                raw_e = getattr(evt, "raw_event", evt)
                sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "")
                if sel:
                    core_pattern_selectors.add(sel)

        # 2. Identify stray events in the observation buffer whose target selector is NOT in core pattern
        seen_stray_selectors: Set[str] = set()

        for evt in all_events:
            raw_e = getattr(evt, "raw_event", evt)
            sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "")
            etype = str(getattr(raw_e, "event_type", "CLICK"))
            app_title = str(getattr(raw_e, "app_title", None) or getattr(raw_e, "active_tab", None) or "App")

            if not sel:
                continue

            # Event is an outlier ONLY if its selector is NOT part of the repeating core pattern
            if sel not in core_pattern_selectors and sel not in seen_stray_selectors:
                seen_stray_selectors.add(sel)
                label = format_human_label(etype, sel, app_title)

                outliers.append({
                    "id": f"out-{len(outliers)+1}",
                    "selector": sel,
                    "event_type": etype,
                    "label": label,
                    "reason": f"Anomalous action observed outside core workflow cycle",
                    "event_id": str(getattr(raw_e, "event_id", "") or ""),
                    "app_title": app_title,
                })

        logger.info(
            f"OutlierDetector evaluated {len(all_events)} events against {len(core_pattern_selectors)} pattern selectors. "
            f"Flagged {len(outliers)} stray outliers."
        )
        return outliers


outlier_detector = OutlierDetector()


