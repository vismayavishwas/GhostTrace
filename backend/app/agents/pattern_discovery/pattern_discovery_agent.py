import logging
from typing import Optional, List, Dict, Set, Any
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate
from app.agents.observer.publisher import TelemetryPublisher
from app.agents.pattern_discovery.sequence_buffer import SequenceBuffer
from app.agents.pattern_discovery.pattern_matcher import PatternMatcher, PatternOccurrence
from app.agents.pattern_discovery.confidence_scorer import ConfidenceScorer
from app.agents.pattern_discovery.publisher import CandidatePublisher

logger = logging.getLogger("ghosttrace.pattern_discovery")


class PatternDiscoveryAgent:
    """
    Pattern Discovery Agent responsible for consuming telemetry event streams,
    detecting recurring action sequences incrementally, scoring candidate confidence,
    and publishing WorkflowCandidate objects.
    """
    def __init__(
        self,
        window_size: int = 50,
        min_repetitions: int = 2,
        confidence_threshold: float = 0.70,
        delta_tolerance_sec: float = 2.0,
        observer_publisher: Optional[TelemetryPublisher] = None,
        publisher: Optional[CandidatePublisher] = None,
    ):
        self.confidence_threshold = confidence_threshold
        self.buffer = SequenceBuffer(window_size=window_size)
        self.matcher = PatternMatcher(min_repetitions=min_repetitions)
        self.scorer = ConfidenceScorer(
            target_repetitions=min_repetitions + 1,
            delta_tolerance_sec=delta_tolerance_sec
        )
        self.publisher = publisher or CandidatePublisher()
        
        # Emitted candidates tracker to avoid duplicate emissions
        self._emitted_signatures: Set[str] = set()
        self._discovered_candidates: List[WorkflowCandidate] = []

        if observer_publisher:
            observer_publisher.subscribe(self.on_telemetry_event)
            logger.info("PatternDiscoveryAgent subscribed to TelemetryPublisher")


    async def on_telemetry_event(self, event: TelemetryEvent) -> List[WorkflowCandidate]:
        """
        Callback handler executed upon receiving a new TelemetryEvent.
        Evaluates incremental pattern candidates and publishes qualified WorkflowCandidate objects.
        """
        # 1. Add event to sliding window
        self.buffer.add_event(event)
        
        # 2. Incremental pattern evaluation
        occurrences: List[PatternOccurrence] = self.matcher.process_incremental_event(
            new_raw_event=event,
            full_raw_window=self.buffer.get_window()
        )

        
        newly_emitted_candidates: List[WorkflowCandidate] = []

        for occ in occurrences:
            score = self.scorer.calculate_score(occ)
            
            if occ.repetition_count >= 2 or score >= self.confidence_threshold:
                latest_occ_events = occ.occurrences[-1]
                latest_seq = [getattr(e, "raw_event", e) for e in latest_occ_events]
                event_ids = [e.event_id for e in latest_seq]


                
                # Signature key for deduplication
                sig_key = f"{occ.signature_tuple}_{occ.repetition_count}"
                if sig_key in self._emitted_signatures:
                    continue
                
                self._emitted_signatures.add(sig_key)
                
                first_app = latest_seq[0].app_title if latest_seq else "Application"
                desc = f"Detected {len(latest_seq)}-step workflow pattern in {first_app} (seen {occ.repetition_count}x)"
                
                candidate = WorkflowCandidate(
                    sequence_event_ids=event_ids,
                    sequence=latest_seq,
                    confidence_score=score,
                    repetition_count=occ.repetition_count,
                    description=desc
                )
                
                logger.info(
                    f"PatternDiscoveryAgent emitted WorkflowCandidate ID={candidate.candidate_id[:8]} "
                    f"Confidence={score:.2f} Reps={occ.repetition_count}"
                )
                
                await self.publisher.publish(candidate)
                self._discovered_candidates.append(candidate)
                newly_emitted_candidates.append(candidate)

        return newly_emitted_candidates

    def get_discovered_candidates(self) -> List[WorkflowCandidate]:
        """Returns snapshot of discovered workflow candidates."""
        return list(self._discovered_candidates)


    def clear(self) -> None:
        """Resets the agent's buffer, matcher index, and emitted signatures."""
        self.buffer.clear()
        self.matcher.clear()
        self._emitted_signatures.clear()

