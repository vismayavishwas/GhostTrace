import logging
from typing import Dict, Any, List, Optional, Tuple
from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.mapping_memory import global_mapping_memory


logger = logging.getLogger("ghosttrace.pattern_discovery.learning_planner")


class LearningPlanner:
    """
    Learning Planner State Machine.
    Decides learning progression based on deterministic mapping memory evidence.
    
    States:
    1. OBSERVING (1 run): "Do I know enough? No. Keep observing."
    2. WATCHING (2 to N-1 runs): "Seen 2-3x. Keep watching."
    3. LOCKED (min_lock_threshold consistent runs, default 3): "Zero conflicts & consistent observations. Lock mapping."
    4. RELEARNING (conflict detected): "User changed mapping. Decrease confidence & relearn."
    """
    def __init__(self, min_lock_threshold: int = 3):
        self.min_lock_threshold = min_lock_threshold

    def evaluate_learning_state(self, transfer: SemanticTransfer) -> Tuple[str, str, float]:
        """
        Evaluates the learning state for a transfer.
        Returns (state, action_decision, confidence_score).
        """
        src = transfer.source_entity.lower()
        dest = transfer.destination_entity.lower()

        # Check existing mappings in StableMappingMemory
        all_dests = global_mapping_memory._source_destinations.get(src, {})
        occurrences = all_dests.get(dest, 0) + 1
        total_for_src = sum(all_dests.values()) + 1

        has_conflict = len(all_dests) > 1 or (len(all_dests) == 1 and dest not in all_dests)

        if has_conflict:
            confidence = round(occurrences / total_for_src, 2)
            logger.info(f"[STAGE 3: LEARNING_PLANNER] State Transition -> RELEARNING | Key='{src}' -> '{dest}' | Conflict Detected | Confidence={confidence}")
            return "RELEARNING", "Conflict observed. Decrease confidence & relearn mapping.", confidence

        if occurrences >= self.min_lock_threshold:
            logger.info(f"[STAGE 3: LEARNING_PLANNER] State Transition -> STABLE_LOCKED 🔒 | Key='{src}' -> '{dest}' | Occurrences={occurrences} >= {self.min_lock_threshold} | Confidence=1.00")
            return "LOCKED", f"Consistent observations ({occurrences}x). Lock mapping.", 1.0

        if occurrences >= 2:
            confidence = round(occurrences / self.min_lock_threshold, 2)
            logger.info(f"[STAGE 3: LEARNING_PLANNER] State Transition -> WATCHING 👁️ | Key='{src}' -> '{dest}' | Occurrences={occurrences} | Confidence={confidence:.2f}")
            return "WATCHING", f"Seen {occurrences}x. Accumulating confidence.", confidence

        logger.info(f"[STAGE 3: LEARNING_PLANNER] State Transition -> OBSERVING | Key='{src}' -> '{dest}' | Initial Observation | Confidence=0.33")
        return "OBSERVING", "Initial observation. Keep watching.", 0.33



global_learning_planner = LearningPlanner()
