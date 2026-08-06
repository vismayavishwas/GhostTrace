from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from app.models.telemetry import TelemetryEvent
import re

def is_semantic_event(event: TelemetryEvent) -> bool:
    """Filters out noise DOM clicks on generic wrapper elements (e.g. span, button, div) to focus on semantic workflow actions."""
    evt_type = str(event.event_type.value if hasattr(event.event_type, "value") else event.event_type).upper()
    selector = str(event.target_selector or "").lower()
    
    # 1. Always include explicit semantic operations
    if any(k in evt_type for k in ["COPY", "PASTE", "TYPE", "SUBMIT"]):
        return True
        
    # 2. Always include specific field selectors
    if any(k in selector for k in ["source", "target", "input", "textarea", "field"]):
        return True
        
    # 3. Exclude generic wrapper click noise (e.g. span, button.rounded-lg, div, #main)
    if any(selector.startswith(k) for k in ["span", "button", "div", "h1", "#main", "body"]):
        return False
        
    return True


def get_event_signature(event: TelemetryEvent) -> Tuple[str, str, str, str]:
    """Generates a structural signature tuple for deterministic comparison with row/index normalization."""
    raw_type = event.event_type.value if hasattr(event.event_type, "value") else (event.event_type.name if hasattr(event.event_type, "name") else str(event.event_type))
    evt_str = str(raw_type).upper()

    raw_selector = str(event.target_selector or "")
    # Normalize dynamic table/row indexes (e.g. tr:nth-child(2) -> tr:nth-child(N), data-row="2" -> data-row="N")
    normalized_selector = re.sub(r"nth-child\(\d+\)", "nth-child(N)", raw_selector)
    normalized_selector = re.sub(r'data-row="\d+"', 'data-row="N"', normalized_selector)
    
    return (
        evt_str,
        normalized_selector,
        str(event.element_tag or "").upper(),
        str(event.app_title or "")
    )


@dataclass
class PatternOccurrence:
    """Stores a detected pattern candidate with event ID references and occurrences."""
    signature_tuple: Tuple[Tuple[str, str, str, str], ...]
    sequence_length: int
    occurrences: List[List[TelemetryEvent]] = field(default_factory=list)
    
    @property
    def repetition_count(self) -> int:
        return len(self.occurrences)
        
    @property
    def latest_event_ids(self) -> List[str]:
        if not self.occurrences:
            return []
        return [e.event_id for e in self.occurrences[-1]]


class PatternMatcher:
    """
    Incremental pattern matcher.
    Evaluates newly arrived events against recent buffer suffixes without full O(n^2) window rescans.
    """
    def __init__(
        self,
        min_sequence_length: int = 2,
        max_sequence_length: int = 10,
        min_repetitions: int = 2
    ):
        self.min_sequence_length = min_sequence_length
        self.max_sequence_length = max_sequence_length
        self.min_repetitions = min_repetitions
        
        # Incremental index: signature_tuple -> list of occurrences
        self._pattern_index: Dict[Tuple[Tuple[str, str, str, str], ...], List[List[TelemetryEvent]]] = {}

    def clear(self):
        """Clears pattern index."""
        self._pattern_index.clear()

    def process_incremental_event(
        self,
        new_event: TelemetryEvent,
        full_window: List[TelemetryEvent]
    ) -> List[PatternOccurrence]:
        """
        Evaluates pattern occurrences ending at new_event incrementally.
        Filters out wrapper noise events to match pure semantic workflow sequences.
        """
        matched_candidates: List[PatternOccurrence] = []
        
        # Filter window to semantic workflow events only
        semantic_window = [e for e in full_window if is_semantic_event(e)]
        n = len(semantic_window)
        
        if n < self.min_sequence_length:
            return matched_candidates

        # Evaluate suffix lengths ending at the latest event
        for length in range(self.min_sequence_length, min(n + 1, self.max_sequence_length + 1)):
            subseq = semantic_window[-length:]
            sig_tuple = tuple(get_event_signature(e) for e in subseq)

            # Record occurrence in index
            if sig_tuple not in self._pattern_index:
                self._pattern_index[sig_tuple] = [subseq]
            else:
                # Check for non-overlapping addition
                existing_occurrences = self._pattern_index[sig_tuple]
                last_occ = existing_occurrences[-1]
                
                # Ensure new subseq starts at or after last occurrence ended
                if subseq[0].timestamp >= last_occ[-1].timestamp and subseq[0].event_id != last_occ[0].event_id:
                    if subseq[0].event_id not in [e.event_id for e in last_occ]:
                        existing_occurrences.append(subseq)

            occurrences = self._pattern_index[sig_tuple]
            if len(occurrences) >= self.min_repetitions:
                matched_candidates.append(
                    PatternOccurrence(
                        signature_tuple=sig_tuple,
                        sequence_length=length,
                        occurrences=occurrences
                    )
                )

        return matched_candidates
