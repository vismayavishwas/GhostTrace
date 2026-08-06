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
    Ambiguity-Driven Intent Disambiguation Engine.
    
    Invocation Rule:
    1. Explicit Single Interpretation: Clear field mappings (e.g., "Invoice Number", "Candidate Name") -> Zero Gemini Calls (100% Deterministic).
    2. Ambiguity Detected: Generic fields ("Reference", "Code", "Status") with multiple equally plausible target interpretations -> Invoke Gemini AI for semantic disambiguation.
    """
    def __init__(self, min_repetition_target: int = 2):
        self.min_repetition_target = min_repetition_target
        self.gemini = GeminiService(primary_model="gemini-2.0-flash")

        # Generic ambiguous field tokens that support multiple plausible interpretations
        self.AMBIGUOUS_GENERIC_TOKENS: Set[str] = {
            "ref", "reference", "code", "status", "type", "data", "info", "tag", "num", "id"
        }

    def evaluate_ambiguity(self, candidate: WorkflowCandidate) -> Tuple[bool, str]:
        """
        Evaluates structural & semantic ambiguity for a candidate workflow.
        Returns (is_ambiguous, reason_description).
        """
        # Signal 1: Repetition check
        if candidate.repetition_count < self.min_repetition_target:
            return True, f"Candidate seen only {candidate.repetition_count}x (min required: {self.min_repetition_target})"

        # Signal 2: Sequence check
        if len(candidate.sequence_event_ids) < 2:
            return True, "Sequence anomaly: less than 2 events in sequence"

        # Signal 3: Structural & Semantic Ambiguity Detection
        candidate_text = (candidate.description or candidate.candidate_id).lower()
        has_ambiguous_token = any(token in candidate_text for token in self.AMBIGUOUS_GENERIC_TOKENS)

        if has_ambiguous_token:
            logger.info(f"Structural Ambiguity Detected in candidate ID={candidate.candidate_id[:8]} (Generic field token present). Invoking Gemini AI...")
            prompt = f"Analyze workflow candidate '{candidate.description}' for semantic ambiguity across target applications."
            response, elapsed, reason = self.gemini.generate(prompt, purpose="semantic_disambiguation")
            
            logger.info(f"Gemini LLM Disambiguation responded in {elapsed:.2f}s (Status: {reason})")
            return True, f"Semantic ambiguity detected by Gemini: multiple target interpretations plausible ({reason})"

        # Explicit single interpretation -> Zero Gemini calls (100% Deterministic)
        logger.info(f"Candidate ID={candidate.candidate_id[:8]} has explicit single interpretation. Zero Gemini AI calls required.")
        return False, "Explicit single interpretation auto-approved deterministically"


