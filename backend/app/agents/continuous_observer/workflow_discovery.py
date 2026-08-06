import logging
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict
from app.agents.continuous_observer.models import ObservationEvent, WorkflowCandidate

logger = logging.getLogger("ghosttrace.continuous_observer.discovery")


def _format_step_name(event_type: str, selector: Optional[str], tag: Optional[str]) -> str:
    """Generates human-readable step descriptions."""
    evt = str(event_type).upper()
    sel = selector or tag or "element"
    
    if "CLICK" in evt:
        if "login" in sel.lower():
            return "Login Button Click"
        elif "search" in sel.lower():
            return "Search Input Focus"
        elif "submit" in sel.lower():
            return "Submit Action"
        return f"Click {sel}"
    elif "TYPE" in evt or "KEY" in evt:
        if "search" in sel.lower():
            return "Enter Search Keyword"
        elif "user" in sel.lower() or "input" in sel.lower():
            return "Enter Form Details"
        return f"Enter Input in {sel}"
    elif "NAV" in evt:
        return "Navigate Workspace"
    else:
        return f"{evt.title()} on {sel}"


class WorkflowDiscoveryEngine:
    """
    Deterministic sequence matching engine that incrementally evaluates observation events,
    clusters recurring n-gram patterns, calculates confidence scores and success rates,
    and produces WorkflowCandidate instances.
    """
    def __init__(
        self,
        min_sequence_length: int = 2,
        max_sequence_length: int = 5,
        min_occurrences: int = 2,
        min_confidence_threshold: float = 0.60
    ):
        self.min_sequence_length = min_sequence_length
        self.max_sequence_length = max_sequence_length
        self.min_occurrences = min_occurrences
        self.min_confidence_threshold = min_confidence_threshold
        self._pattern_counts: Dict[Tuple[str, ...], List[List[ObservationEvent]]] = defaultdict(list)
        self._discovered_candidates: Dict[str, WorkflowCandidate] = {}

    def analyze_observations(self, observations: List[ObservationEvent]) -> List[WorkflowCandidate]:
        """
        Analyzes a sequence of ObservationEvents and returns newly discovered or updated WorkflowCandidates.
        """
        if len(observations) < self.min_sequence_length:
            return []

        new_candidates: List[WorkflowCandidate] = []

        # Extract n-grams of lengths between min and max sequence length
        n = len(observations)
        for seq_len in range(self.min_sequence_length, min(self.max_sequence_length + 1, n + 1)):
            for i in range(n - seq_len + 1):
                window = observations[i : i + seq_len]
                sig_tuple = tuple(
                    f"{obs.telemetry_event.event_type}:{obs.telemetry_event.target_selector or obs.telemetry_event.element_tag or 'element'}"
                    for obs in window
                )

                self._pattern_counts[sig_tuple].append(window)

        # Evaluate clustered patterns
        for sig_tuple, occurrences in self._pattern_counts.items():
            count = len(occurrences)
            if count >= self.min_occurrences:
                candidate = self._build_candidate(sig_tuple, occurrences)
                if candidate.confidence_score >= self.min_confidence_threshold:
                    if candidate.name not in self._discovered_candidates:
                        self._discovered_candidates[candidate.name] = candidate
                        new_candidates.append(candidate)
                    else:
                        # Update existing candidate stats
                        existing = self._discovered_candidates[candidate.name]
                        existing.occurrence_count = max(existing.occurrence_count, count)
                        existing.confidence_score = max(existing.confidence_score, candidate.confidence_score)
                        existing.success_rate = candidate.success_rate

        logger.info(f"WorkflowDiscoveryEngine evaluated {len(observations)} events and identified {len(new_candidates)} new WorkflowCandidates.")
        return new_candidates

    def _build_candidate(
        self,
        sig_tuple: Tuple[str, ...],
        occurrences: List[List[ObservationEvent]]
    ) -> WorkflowCandidate:
        """Constructs a WorkflowCandidate with confidence score and success rate metrics."""
        first_window = occurrences[0]
        
        # Build human-readable step names
        observed_steps = [
            _format_step_name(
                obs.telemetry_event.event_type,
                obs.telemetry_event.target_selector,
                obs.telemetry_event.element_tag
            )
            for obs in first_window
        ]

        # Extract sequence event IDs
        seq_ids = [obs.telemetry_event.event_id for obs in first_window]

        # Calculate success rate
        total_obs = sum(len(w) for w in occurrences)
        successful_obs = sum(sum(1 for obs in w if obs.success_signal) for w in occurrences)
        success_rate = round(successful_obs / total_obs, 2) if total_obs > 0 else 1.0

        # Calculate confidence score based on repetition count and consistency
        count = len(occurrences)
        confidence = min(0.98, round(0.50 + (count * 0.10) + (success_rate * 0.20), 2))

        # Extract unique applications
        apps = list(set(obs.app_title for w in occurrences for obs in w))

        # Build Candidate Name (e.g. 'Product Search Flow')
        if len(observed_steps) >= 3 and "Login" in observed_steps[0] and "Search" in observed_steps[1]:
            candidate_name = "Product Search Flow"
        elif any("Login" in s for s in observed_steps):
            candidate_name = "Authentication Workflow"
        else:
            candidate_name = f"Recurring {observed_steps[0]} Pattern"

        return WorkflowCandidate(
            name=candidate_name,
            observed_steps=observed_steps,
            sequence_event_ids=seq_ids,
            occurrence_count=count,
            confidence_score=confidence,
            success_rate=success_rate,
            applications_involved=apps
        )

    def get_all_candidates(self) -> List[WorkflowCandidate]:
        """Returns all discovered candidates."""
        return list(self._discovered_candidates.values())
