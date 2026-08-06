import logging
from typing import Optional, List, Dict, Tuple
from app.models.enums import IntentChoice
from app.models.workflow import WorkflowCandidate, IntentDecision
from app.agents.pattern_discovery.publisher import CandidatePublisher
from app.agents.intent_disambiguation.ambiguity_detector import AmbiguityDetector
from app.agents.intent_disambiguation.publisher import DecisionPublisher

logger = logging.getLogger("ghosttrace.intent_disambiguation")


class IntentDisambiguationAgent:
    """
    Intent Disambiguation Agent responsible for detecting candidate ambiguities,
    creating HITL decision requests with diagnostic reasons, and handling user resolutions
    (MISTAKE, BRANCH, APPROVED).
    """
    def __init__(
        self,
        ambiguity_detector: Optional[AmbiguityDetector] = None,
        candidate_publisher: Optional[CandidatePublisher] = None,
        publisher: Optional[DecisionPublisher] = None,
    ):
        self.detector = ambiguity_detector or AmbiguityDetector()
        self.publisher = publisher or DecisionPublisher()
        
        # Pending HITL decision store: decision_id -> (IntentDecision, WorkflowCandidate)
        self._pending_store: Dict[str, Tuple[IntentDecision, WorkflowCandidate]] = {}

        if candidate_publisher:
            candidate_publisher.subscribe(self.on_workflow_candidate)
            logger.info("IntentDisambiguationAgent subscribed to CandidatePublisher")

    async def on_workflow_candidate(self, candidate: WorkflowCandidate) -> IntentDecision:
        """Callback executed upon receiving a WorkflowCandidate from Pattern Discovery."""
        return await self.evaluate_candidate(candidate)

    async def evaluate_candidate(self, candidate: WorkflowCandidate) -> IntentDecision:
        """
        Evaluates a candidate workflow. If clear, auto-approves and publishes candidate.
        If ambiguous, creates a pending HITL decision request with the exact diagnostic reason.
        """
        is_ambiguous, reason = self.detector.evaluate_ambiguity(candidate)

        if not is_ambiguous:
            # Auto-approve high-confidence candidate
            decision = IntentDecision(
                candidate_id=candidate.candidate_id,
                choice=IntentChoice.APPROVED,
                reason="Auto-approved: High confidence candidate"
            )
            logger.info(
                f"IntentDisambiguationAgent auto-approved Candidate ID={candidate.candidate_id[:8]} "
                f"Confidence={candidate.confidence_score:.2f}"
            )
            await self.publisher.publish(decision, candidate)
            return decision

        # Create pending decision request
        return self.create_decision_request(candidate, reason)

    def create_decision_request(self, candidate: WorkflowCandidate, reason: str) -> IntentDecision:
        """
        Creates a pending IntentDecision request carrying the ambiguity reason for the HITL UI.
        Pauses candidate execution until user responds.
        """
        decision = IntentDecision(
            candidate_id=candidate.candidate_id,
            choice=IntentChoice.REJECTED,  # Initial unapproved status until user responds
            reason=reason
        )
        self._pending_store[decision.decision_id] = (decision, candidate)
        
        logger.info(
            f"IntentDisambiguationAgent created pending decision ID={decision.decision_id[:8]} "
            f"Reason='{reason}' for Candidate ID={candidate.candidate_id[:8]}"
        )
        return decision

    async def receive_decision(
        self,
        decision_id: str,
        choice: IntentChoice,
        feedback_comment: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Tuple[IntentDecision, Optional[WorkflowCandidate]]:
        """
        Processes human-in-the-loop decision choice (MISTAKE, BRANCH, APPROVED).
        Publishes resolved decision and WorkflowCandidate to downstream consumers.
        """
        effective_comment = feedback_comment or comment
        if decision_id not in self._pending_store:
            raise KeyError(f"Pending decision request ID '{decision_id}' not found.")

        pending_decision, candidate = self._pending_store.pop(decision_id)
        
        # Update decision choice and comment
        resolved_decision = IntentDecision(
            decision_id=pending_decision.decision_id,
            candidate_id=pending_decision.candidate_id,
            choice=choice,
            reason=pending_decision.reason,
            feedback_comment=effective_comment
        )


        if choice == IntentChoice.MISTAKE:
            logger.info(f"User classified Candidate ID={candidate.candidate_id[:8]} as MISTAKE. Candidate discarded.")
            await self.publisher.publish(resolved_decision, None)
            return resolved_decision, None

        elif choice == IntentChoice.BRANCH:
            logger.info(f"User classified Candidate ID={candidate.candidate_id[:8]} as new WORKFLOW BRANCH.")
            candidate.description = f"[Branch] {candidate.description}"
            await self.publisher.publish(resolved_decision, candidate)
            return resolved_decision, candidate

        elif choice == IntentChoice.APPROVED:
            logger.info(f"User APPROVED Candidate ID={candidate.candidate_id[:8]}. Forwarding to next stage.")
            await self.publisher.publish(resolved_decision, candidate)
            return resolved_decision, candidate

        else:
            logger.warning(f"Unrecognized intent choice '{choice}' for Decision ID={decision_id}")
            return resolved_decision, None

    def get_pending_decisions(self) -> List[IntentDecision]:
        """Returns all currently pending decision requests."""
        return [pair[0] for pair in self._pending_store.values()]

    def get_pending_candidate(self, decision_id: str) -> Optional[WorkflowCandidate]:
        """Retrieves candidate associated with a pending decision ID."""
        pair = self._pending_store.get(decision_id)
        return pair[1] if pair else None
