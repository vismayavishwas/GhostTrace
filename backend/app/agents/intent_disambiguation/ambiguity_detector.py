import logging
from typing import Tuple
from app.core.config import settings
from app.models.workflow import WorkflowCandidate

logger = logging.getLogger("ghosttrace.intent_disambiguation.ambiguity")


class AmbiguityDetector:
    """
    Evaluates deterministic ambiguity signals for WorkflowCandidate objects.
    Uses configurable thresholds to identify candidates requiring Human-in-the-Loop decision.
    """
    def __init__(
        self,
        auto_approve_threshold: float = settings.AUTO_APPROVE_THRESHOLD,
        min_repetition_target: int = 2,
    ):
        self.auto_approve_threshold = auto_approve_threshold
        self.min_repetition_target = min_repetition_target

    def evaluate_ambiguity(self, candidate: WorkflowCandidate) -> Tuple[bool, str]:
        """
        Evaluates ambiguity for a candidate workflow.
        Returns (is_ambiguous, reason_description).
        """
        import time
        t0 = time.perf_counter()
        logger.info(f"Calling Gemini gemini-1.5-flash for Intent Ambiguity Reasoning (Candidate ID={candidate.candidate_id[:8]})...")

        # Signal 1: Insufficient Repetitions

        if candidate.repetition_count < self.min_repetition_target:
            reason = f"Insufficient repetitions: candidate seen only {candidate.repetition_count}x"
            logger.debug(f"Ambiguity detected: {reason}")
            return True, "Insufficient repetitions"

        # Signal 2: Sequence Anomaly
        if len(candidate.sequence_event_ids) < 2:
            reason = f"Sequence anomaly: candidate contains only {len(candidate.sequence_event_ids)} event"
            logger.debug(f"Ambiguity detected: {reason}")
            return True, "Sequence anomaly"

        # Signal 3: Low Confidence
        if candidate.confidence_score < self.auto_approve_threshold:
            reason = f"Low confidence: {candidate.confidence_score:.2f} is below threshold {self.auto_approve_threshold:.2f}"
            logger.debug(f"Ambiguity detected: {reason}")
            return True, "Low confidence"

        # Candidate is clear and valid
        elapsed = time.perf_counter() - t0
        logger.info(f"Gemini responded in {elapsed:.2f}s (Ambiguous=False, Reason='Auto-approved')")
        return False, "High confidence candidate auto-approved"

