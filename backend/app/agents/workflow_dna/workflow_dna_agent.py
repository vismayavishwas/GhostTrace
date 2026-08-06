import logging
from typing import Optional, List
from app.models.enums import IntentChoice
from app.models.workflow import IntentDecision, WorkflowCandidate, WorkflowDNA
from app.agents.intent_disambiguation.publisher import DecisionPublisher
from app.agents.workflow_dna.dna_transformer import DNATransformer
from app.agents.workflow_dna.publisher import DNAPublisher

logger = logging.getLogger("ghosttrace.workflow_dna")


class WorkflowDNAAgent:
    """
    Workflow DNA Agent responsible for consuming approved WorkflowCandidates,
    applying deterministic semantic transformation rules, synthesizing WorkflowDNA models,
    and publishing them to downstream compilers.
    """
    def __init__(
        self,
        transformer: Optional[DNATransformer] = None,
        decision_publisher: Optional[DecisionPublisher] = None,
        publisher: Optional[DNAPublisher] = None,
    ):
        self.transformer = transformer or DNATransformer()
        self.publisher = publisher or DNAPublisher()
        self._history: List[WorkflowDNA] = []

        if decision_publisher:
            decision_publisher.subscribe(self.on_intent_decision)
            logger.info("WorkflowDNAAgent subscribed to DecisionPublisher")

    async def on_intent_decision(
        self,
        decision: IntentDecision,
        candidate: Optional[WorkflowCandidate] = None
    ) -> Optional[WorkflowDNA]:
        """
        Callback executed when a decision is published.
        Extracts WorkflowDNA if decision choice is APPROVED or BRANCH.
        """
        if decision.choice not in [IntentChoice.APPROVED, IntentChoice.BRANCH]:
            logger.debug(f"WorkflowDNAAgent ignored decision choice '{decision.choice}'")
            return None

        if candidate is None or not candidate.sequence:
            logger.warning(f"WorkflowDNAAgent received decision ID={decision.decision_id} without candidate sequence")
            return None

        return await self.extract_dna(candidate)

    async def extract_dna(self, candidate: WorkflowCandidate) -> WorkflowDNA:
        """
        Transforms a WorkflowCandidate into WorkflowDNA, saves in history, and publishes.
        """
        dna = self.transformer.transform_candidate(candidate)
        self._history.append(dna)

        logger.info(
            f"WorkflowDNAAgent extracted WorkflowDNA ID={dna.workflow_id[:8]} "
            f"Steps={len(dna.steps)} Apps={dna.applications_involved}"
        )
        
        await self.publisher.publish(dna)
        return dna

    def get_extracted_dna_list(self) -> List[WorkflowDNA]:
        """Returns history of extracted WorkflowDNA instances."""
        return list(self._history)
