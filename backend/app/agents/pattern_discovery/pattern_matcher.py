from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from app.models.telemetry import TelemetryEvent
from app.agents.telemetry.semantic_normalizer import SemanticEvent, SemanticNormalizer
import re

def get_semantic_signature(event: Any) -> Tuple[str, str, str, str]:
    """Generates a structural signature tuple for normalized semantic events."""
    evt_type = getattr(event, "semantic_type", None) or getattr(event, "event_type", "ACTION")
    evt_str = str(evt_type.value if hasattr(evt_type, "value") else evt_type).upper()

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
    """Stores a detected pattern candidate with normalized event ID references and occurrences."""
    signature_tuple: Tuple[Tuple[str, str, str, str], ...]
    sequence_length: int
    occurrences: List[List[Any]] = field(default_factory=list)
    
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
    Operates strictly on normalized SemanticEvent sequences for domain-agnostic workflow pattern discovery.
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
        self._pattern_index: Dict[Tuple[Tuple[str, str, str, str], ...], List[List[Any]]] = {}

    def clear(self):
        """Clears pattern index."""
        self._pattern_index.clear()

    def process_incremental_event(
        self,
        new_raw_event: TelemetryEvent,
        full_raw_window: List[TelemetryEvent]
    ) -> List[PatternOccurrence]:
        """
        Evaluates pattern occurrences incrementally by normalizing raw telemetry window into SemanticEvents.
        """
        matched_candidates: List[PatternOccurrence] = []
        
        # 1. Pipeline Stage: Normalize raw telemetry window into business SemanticEvents
        semantic_window: List[SemanticEvent] = []
        for raw_e in full_raw_window:
            sem_e = SemanticNormalizer.normalize(raw_e)
            if sem_e is not None:
                semantic_window.append(sem_e)
                
        n = len(semantic_window)
        if n < self.min_sequence_length:
            return matched_candidates

        # 2. Evaluate suffix lengths ending at the latest normalized semantic event
        for length in range(self.min_sequence_length, min(n + 1, self.max_sequence_length + 1)):
            subseq = semantic_window[-length:]
            sig_tuple = tuple(get_semantic_signature(e) for e in subseq)

            # Record occurrence in index
            if sig_tuple not in self._pattern_index:
                self._pattern_index[sig_tuple] = [subseq]
            else:
                existing_occurrences = self._pattern_index[sig_tuple]
                last_occ = existing_occurrences[-1]
                
                # Non-overlapping occurrence check
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
