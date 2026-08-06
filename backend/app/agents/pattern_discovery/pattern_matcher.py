from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from app.models.telemetry import TelemetryEvent
from app.agents.telemetry.semantic_normalizer import SemanticEvent, SemanticNormalizer
import re

def get_semantic_signature(event: Any) -> Tuple[str, str, str]:
    """
    Generates a purely semantic signature tuple for pattern discovery.
    100% decoupled from DOM target_selector strings (zero selector comparison).
    """
    op = getattr(event, "operation", None) or getattr(event, "semantic_type", "ACTION")
    op_str = str(op.value if hasattr(op, "value") else op).upper()

    entity = getattr(event, "semantic_entity", None) or "semantic:unknown"
    app = getattr(event, "app_title", None) or "App"
    
    return (
        op_str,
        str(entity),
        str(app)
    )



@dataclass
class PatternOccurrence:
    """Stores a detected pattern candidate with normalized event ID references and occurrences."""
    signature_tuple: Tuple[Tuple[str, str, str], ...]
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
    Evaluates semantic workflow event sequences and sub-sequences to discover repeating cross-application
    interaction patterns with high resilience to human click order.
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
        self._pattern_index: Dict[Tuple[Tuple[str, str, str], ...], List[List[Any]]] = {}


    def clear(self):
        """Clears pattern index."""
        self._pattern_index.clear()

    def process_incremental_event(
        self,
        new_raw_event: TelemetryEvent,
        full_raw_window: List[TelemetryEvent]
    ) -> List[PatternOccurrence]:
        """
        Evaluates pattern occurrences incrementally across semantic event subsequences.
        Returns all matched pattern occurrences meeting minimum repetition thresholds.
        """
        matched_candidates: List[PatternOccurrence] = []
        
        # 1. Normalize raw telemetry window into business SemanticEvents
        semantic_window: List[SemanticEvent] = []
        for raw_e in full_raw_window:
            sem_e = SemanticNormalizer.normalize(raw_e)
            if sem_e is not None:
                semantic_window.append(sem_e)
                
        n = len(semantic_window)
        if n < self.min_sequence_length:
            return matched_candidates

        # 2. Evaluate suffix lengths ending at the latest normalized semantic event (lengths 2 to max_sequence_length)
        for length in range(self.min_sequence_length, min(n + 1, self.max_sequence_length + 1)):
            subseq = semantic_window[-length:]
            sig_tuple = tuple(get_semantic_signature(e) for e in subseq)

            # Record occurrence in index
            if sig_tuple not in self._pattern_index:
                self._pattern_index[sig_tuple] = [subseq]
            else:
                existing_occurrences = self._pattern_index[sig_tuple]
                last_occ = existing_occurrences[-1]
                
                # Check for non-overlapping occurrence using event_id disjoint sets
                last_event_ids = set(e.event_id for e in last_occ)
                curr_event_ids = set(e.event_id for e in subseq)
                
                if not last_event_ids.intersection(curr_event_ids):
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
