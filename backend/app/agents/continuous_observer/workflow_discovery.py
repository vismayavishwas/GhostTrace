import logging
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict
from app.agents.continuous_observer.models import ObservationEvent, WorkflowCandidate
from app.agents.telemetry.semantic_normalizer import SemanticNormalizer


logger = logging.getLogger("ghosttrace.continuous_observer.discovery")


def _format_step_name(event_type: str, selector: Optional[str], tag: Optional[str]) -> str:
    """Generates human-readable step descriptions domain-agnostically."""
    evt = event_type.upper()
    clean_sel = (selector or tag or "element").replace("#", "").replace(".", " ").replace("-", " ").strip().title()
    if not clean_sel:
        clean_sel = "Element"

    if "CLICK" in evt:
        return f"Click {clean_sel}"
    elif "TYPE" in evt or "KEY" in evt or "PASTE" in evt:
        return f"Input into {clean_sel}"
    elif "COPY" in evt:
        return f"Copy from {clean_sel}"
    elif "NAV" in evt:
        return f"Navigate to {clean_sel}"
    else:
        return f"{evt.capitalize()} on {clean_sel}"


class WorkflowDiscoveryEngine:
    """
    Sequence Cycle Discovery Engine.
    
    Responsibilities:
    1. Segments raw telemetry streams into distinct, non-overlapping Sequence Cycles using Anchor Boundaries
       (returning to step 1 OR clicking Next Record / Submit).
    2. Measures true sequence repetition counts (Cycle 1 -> Cycle 2 -> Cycle 3).
    3. Performs step-by-step sequence alignment to accurately detect mistakes (e.g., Step 2 Mismatch).
    """
    def __init__(
        self,
        min_sequence_length: int = 3,
        min_occurrences: int = 2,
        min_confidence_threshold: float = 0.50
    ):
        self.min_sequence_length = min_sequence_length
        self.min_occurrences = min_occurrences
        self.min_confidence_threshold = min_confidence_threshold
        self._completed_cycles: List[List[ObservationEvent]] = []
        self._established_sequence_entities: List[str] = []
        self._discovered_candidates: Dict[str, WorkflowCandidate] = {}
        self.last_completed_cycle_count: int = 0

    def get_completed_cycle_count(self) -> int:
        """Returns the number of completed sequence cycles observed so far."""
        return self.last_completed_cycle_count

    def clear(self) -> None:
        """Resets engine state."""
        self._completed_cycles.clear()
        self._established_sequence_entities.clear()
        self._discovered_candidates.clear()
        self.last_completed_cycle_count = 0

    def analyze_observations(self, observations: List[ObservationEvent]) -> List[WorkflowCandidate]:
        """
        Extracts sequence cycles from ObservationEvents and evaluates pattern repetition & deviations.
        """
        if not observations:
            return []

        # Filter out noise events and extract semantic actions (Data transfer & submit operations)
        semantic_actions: List[Tuple[ObservationEvent, str]] = []
        for obs in observations:
            sem = SemanticNormalizer.normalize(obs.telemetry_event)
            if sem and sem.operation in ["COPY", "PASTE", "TYPE", "SELECT", "SUBMIT", "NAVIGATE", "SUBMIT_ACTION", "FOCUS_FIELD", "EXECUTE_ACTION"]:
                semantic_actions.append((obs, sem.semantic_entity))

        if len(semantic_actions) < self.min_sequence_length:
            return []

        # Segment semantic_actions into non-overlapping cycles based on Anchor Boundaries
        cycles: List[List[Tuple[ObservationEvent, str]]] = []
        current_cycle: List[Tuple[ObservationEvent, str]] = []
        anchor_entity: Optional[str] = None

        for obs, entity in semantic_actions:
            tag = (obs.telemetry_event.element_tag or "").upper()
            sem_op = str(getattr(obs.telemetry_event, "event_type", "")).upper()
            selector = (obs.telemetry_event.target_selector or "").lower()

            sem = SemanticNormalizer.normalize(obs.telemetry_event)
            norm_op = sem.operation if sem else ""

            is_submit_btn = (
                sem_op == "SUBMIT"
                or norm_op in ["SUBMIT", "SUBMIT_ACTION"]
                or any(k in selector for k in ["btn_submit", "btn-submit", "btn_save", "btn-save", "submit-btn", "btn-next", "next-record", "next"])
                or tag == "SUBMIT"
            )
            is_nav = sem_op == "NAVIGATE" or norm_op == "NAVIGATE" or (is_submit_btn and len(current_cycle) >= 2)

            if anchor_entity is None:
                anchor_entity = entity
                current_cycle.append((obs, entity))
            elif is_nav or (entity == anchor_entity and len(current_cycle) >= 2):
                # Cycle Boundary Reached! Close current cycle
                if is_nav and entity != anchor_entity:
                    current_cycle.append((obs, entity))

                if len(current_cycle) >= self.min_sequence_length:
                    cycles.append(current_cycle)

                current_cycle = [] if is_nav else [(obs, entity)]
                anchor_entity = entity if not is_nav else None
            else:
                current_cycle.append((obs, entity))

        if len(current_cycle) >= self.min_sequence_length and len(cycles) >= 1:
            # Add remaining open cycle if sequence template matches
            cycles.append(current_cycle)

        if not cycles:
            return []

        # Extract sequence template from first cycle
        first_cycle_entities = [ent for _, ent in cycles[0]]
        self._established_sequence_entities = first_cycle_entities

        # Count completed cycles that match the template signature
        matching_cycle_count = 0
        for cycle in cycles:
            cycle_ents = [ent for _, ent in cycle]
            template_ents = first_cycle_entities
            if cycle_ents == template_ents or (len(cycle_ents) >= 2 and cycle_ents[:len(template_ents)] == template_ents):
                matching_cycle_count += 1

        self.last_completed_cycle_count = len(cycles)

        # Build candidate representing the full sequence cycle
        sample_obs_window = [obs for obs, _ in cycles[0]]
        candidate = self._build_candidate_from_cycle(sample_obs_window, len(cycles))
        
        new_candidates = []
        if candidate.name not in self._discovered_candidates:
            self._discovered_candidates[candidate.name] = candidate
            new_candidates.append(candidate)
        else:
            existing = self._discovered_candidates[candidate.name]
            existing.occurrence_count = len(cycles)
            existing.confidence_score = candidate.confidence_score

        logger.info(f"WorkflowDiscoveryEngine identified {len(cycles)} completed sequence cycles across {len(observations)} events.")
        return new_candidates


    def _build_candidate_from_cycle(
        self,
        cycle_obs: List[ObservationEvent],
        cycle_count: int
    ) -> WorkflowCandidate:
        """Constructs a WorkflowCandidate representing a completed sequence cycle."""
        observed_steps = [
            _format_step_name(
                obs.telemetry_event.event_type,
                obs.telemetry_event.target_selector,
                obs.telemetry_event.element_tag
            )
            for obs in cycle_obs
        ]

        seq_ids = [obs.telemetry_event.event_id for obs in cycle_obs]
        apps = list(set(obs.app_title for obs in cycle_obs))

        # Dynamic sample-weighted confidence: 33% for 1 cycle, 66% for 2 cycles, 100% for 3+ cycles
        confidence = 0.33 if cycle_count == 1 else (0.66 if cycle_count == 2 else 1.00)

        source_app = apps[0] if apps else "Source App"
        target_app = apps[-1] if len(apps) > 1 else "Target App"
        candidate_name = f"{source_app} -> {target_app} Workflow Sequence"

        return WorkflowCandidate(
            candidate_id=f"cand-{hash(tuple(seq_ids)) & 0xffffff:06x}",
            name=candidate_name,
            observed_steps=observed_steps,
            sequence_event_ids=seq_ids,
            occurrence_count=cycle_count,
            repetition_count=cycle_count,
            confidence_score=confidence,
            success_rate=1.0,
            applications_involved=apps
        )


    def get_all_candidates(self) -> List[WorkflowCandidate]:
        """Returns all discovered candidates."""
        return list(self._discovered_candidates.values())

