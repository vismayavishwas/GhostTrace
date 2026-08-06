import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.telemetry import TelemetryEvent

logger = logging.getLogger("ghosttrace.pattern_discovery.outlier")


class OutlierDetector:
    """
    Deterministic Outlier Detector.
    Evaluates accidental, anomalous, or out-of-sequence user actions across telemetry events.
    
    Detection Rules:
    1. Out-of-Pattern Actions: Events in telemetry buffer that do NOT belong to the repeating pattern cycle.
    2. Frequency Anomalies: Actions appearing in only 1 of N sequence runs.
    3. Unexpected UI Interactions: Isolated clicks/pastes on non-target UI elements.
    """

    def detect_outliers(
        self, occurrences: List[List[TelemetryEvent]], all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        outliers: List[Dict[str, Any]] = []
        if not all_events:
            return outliers

        # Collect event signatures & IDs that belong to the core repeating pattern cycle
        pattern_event_ids: Set[str] = set()
        pattern_signatures: Set[Tuple[str, str]] = set()

        if occurrences and len(occurrences) >= 2:
            for occ in occurrences:
                for evt in occ:
                    raw_e = getattr(evt, "raw_event", evt)
                    evt_id = str(getattr(raw_e, "event_id", "") or "")
                    if evt_id:
                        pattern_event_ids.add(evt_id)
                    
                    sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "element")
                    etype = str(getattr(raw_e, "event_type", "CLICK"))
                    pattern_signatures.add((etype, sel))

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
    Deterministic Outlier Detector.
    Evaluates accidental, anomalous, or out-of-sequence user actions across telemetry events.
    """

    def detect_outliers(
        self, occurrences: List[List[TelemetryEvent]], all_events: List[TelemetryEvent]
    ) -> List[Dict[str, Any]]:
        outliers: List[Dict[str, Any]] = []
        if not all_events:
            return outliers

        # Collect event signatures & IDs that belong to the core repeating pattern cycle
        pattern_event_ids: Set[str] = set()
        pattern_signatures: Set[Tuple[str, str]] = set()

        if occurrences and len(occurrences) >= 2:
            for occ in occurrences:
                for evt in occ:
                    raw_e = getattr(evt, "raw_event", evt)
                    evt_id = str(getattr(raw_e, "event_id", "") or "")
                    if evt_id:
                        pattern_event_ids.add(evt_id)
                    
                    sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "element")
                    etype = str(getattr(raw_e, "event_type", "CLICK"))
                    pattern_signatures.add((etype, sel))

        # Inspect all telemetry events in the observation buffer for anomalies
        seen_outlier_selectors: Set[str] = set()

        for evt in all_events:
            raw_e = getattr(evt, "raw_event", evt)
            evt_id = str(getattr(raw_e, "event_id", "") or "")
            sel = str(getattr(raw_e, "target_selector", None) or getattr(raw_e, "element_tag", None) or "element")
            etype = str(getattr(raw_e, "event_type", "CLICK"))
            app_title = str(getattr(raw_e, "app_title", None) or getattr(raw_e, "active_tab", None) or "App")

            # Check if this event was outside the matched repeating pattern cycles
            is_outside_pattern = (evt_id and evt_id not in pattern_event_ids) or ((etype, sel) not in pattern_signatures)

            if is_outside_pattern and sel not in seen_outlier_selectors:
                seen_outlier_selectors.add(sel)
                
                label = format_human_label(etype, sel, app_title)

                outliers.append({
                    "id": f"out-{len(outliers)+1}",
                    "selector": sel,
                    "event_type": etype,
                    "label": label,
                    "reason": f"Anomalous action observed outside 6-step repeating pattern",
                    "event_id": evt_id,
                    "app_title": app_title,
                })

        logger.info(f"OutlierDetector evaluated {len(all_events)} events and flagged {len(outliers)} anomalous actions.")
        return outliers



outlier_detector = OutlierDetector()

