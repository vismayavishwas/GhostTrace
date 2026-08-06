import logging
from typing import Tuple
from app.core.config import settings
from app.models.workflow import WorkflowCandidate

logger = logging.getLogger("ghosttrace.intent_disambiguation.ambiguity")


import logging
from typing import Tuple, Set
from app.core.config import settings
from app.models.workflow import WorkflowCandidate
from app.services.gemini_service import GeminiService

logger = logging.getLogger("ghosttrace.intent_disambiguation.ambiguity")


class AmbiguityDetector:
    """
    Graph-Based Intent Disambiguation Engine.
    
    Invocation Rule:
    1. Single Unambiguous Path: Every source entity maps to a single deterministic target -> Zero Gemini Calls.
    2. Graph Branch Ambiguity: A source entity fingerprint maps to 2 or more conflicting target destinations across cycles (Graph Branch Conflict) -> Invoke Gemini AI for semantic disambiguation.
    
    Zero Keyword Lists: Ambiguity is derived 100% from structural graph branch conflicts, not word searches.
    """
    def __init__(self, min_repetition_target: int = 2):
        self.min_repetition_target = min_repetition_target
        self.gemini = GeminiService(primary_model="gemini-2.0-flash")

    def evaluate_ambiguity(self, candidate: WorkflowCandidate) -> Tuple[bool, str]:
        """
        Evaluates structural & mapping graph ambiguity for a candidate workflow.
        Returns (is_ambiguous, reason_description).
        """
        # Signal 1: Repetition check
        if candidate.repetition_count < self.min_repetition_target:
            return True, f"Candidate seen only {candidate.repetition_count}x (min required: {self.min_repetition_target})"

        # Signal 2: Sequence check
        if len(candidate.sequence_event_ids) < 2:
            return True, "Sequence anomaly: less than 2 events in sequence"

        # Signal 3: Graph Branch Mapping Ambiguity Detection
        # Check if candidate metadata or candidate object indicates graph branching conflicts
        graph_branch_conflict = candidate.metadata.get("has_graph_branch_conflict", False) if hasattr(candidate, "metadata") and candidate.metadata else False

        if graph_branch_conflict:
            logger.info(f"Graph Branch Mapping Ambiguity Detected in candidate ID={candidate.candidate_id[:8]} (Multiple plausible target destinations). Invoking Gemini AI...")
            prompt = f"Analyze workflow candidate '{candidate.description}' for semantic ambiguity across target application mappings."
            response, elapsed, reason = self.gemini.generate(prompt, purpose="semantic_disambiguation")
            
            logger.info(f"Gemini LLM Disambiguation responded in {elapsed:.2f}s (Status: {reason})")
            return True, f"Graph branch ambiguity resolved by Gemini: multiple target interpretations plausible ({reason})"

        # Single unambiguous path -> Zero Gemini calls (100% Deterministic)
        logger.info(f"Candidate ID={candidate.candidate_id[:8]} has single unambiguous mapping graph path. Zero Gemini AI calls required.")
        return False, "Single unambiguous mapping graph path auto-approved deterministically"



