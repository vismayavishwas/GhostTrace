import logging
from typing import List
from app.agents.pattern_discovery.pattern_matcher import PatternOccurrence
from app.models.telemetry import TelemetryEvent

logger = logging.getLogger("ghosttrace.pattern_discovery.scorer")


class ConfidenceScorer:
    """
    Computes deterministic confidence scores (0.0 - 1.0) for PatternOccurrence candidates.
    Combines Repetition Frequency, Structural Consistency, and Timing Delta Tolerance.
    """
    def __init__(
        self,
        target_repetitions: int = 3,
        delta_tolerance_sec: float = 2.0,
        freq_weight: float = 0.40,
        struct_weight: float = 0.40,
        timing_weight: float = 0.20,
    ):
        self.target_repetitions = max(1, target_repetitions)
        self.delta_tolerance_sec = max(0.1, delta_tolerance_sec)
        self.freq_weight = freq_weight
        self.struct_weight = struct_weight
        self.timing_weight = timing_weight

    def calculate_score(self, occurrence: PatternOccurrence) -> float:
        """
        Calculates confidence score for a pattern candidate.
        """
        if not occurrence.occurrences or len(occurrence.occurrences) < 1:
            return 0.0

        # 1. Repetition Frequency Score (0.0 - 1.0)
        rep_count = occurrence.repetition_count
        freq_score = min(1.0, rep_count / self.target_repetitions)

        # 2. Structural Consistency Score (0.0 - 1.0)
        struct_score = self._calculate_structural_consistency(occurrence.occurrences)

        # 3. Timing Delta Tolerance Score (0.0 - 1.0)
        timing_score = self._calculate_timing_tolerance(occurrence.occurrences)

        # Weighted sum
        total_score = (
            (freq_score * self.freq_weight) +
            (struct_score * self.struct_weight) +
            (timing_score * self.timing_weight)
        )
        
        score_bounded = round(min(1.0, max(0.0, total_score)), 4)
        logger.debug(
            f"Candidate length={occurrence.sequence_length} reps={rep_count} "
            f"Scores: Freq={freq_score:.2f}, Struct={struct_score:.2f}, Timing={timing_score:.2f} -> Total={score_bounded}"
        )
        return score_bounded

    def _calculate_structural_consistency(self, occurrences: List[List[TelemetryEvent]]) -> float:
        """Checks structural field consistency across all repetition instances."""
        if len(occurrences) <= 1:
            return 1.0

        base_seq = occurrences[0]
        matches = 0
        total_checks = 0

        for occ in occurrences[1:]:
            for e1, e2 in zip(base_seq, occ):
                total_checks += 3
                if e1.event_type == e2.event_type:
                    matches += 1
                if (e1.target_selector or "") == (e2.target_selector or ""):
                    matches += 1
                if (e1.app_title or "") == (e2.app_title or ""):
                    matches += 1

        return matches / total_checks if total_checks > 0 else 1.0

    def _calculate_timing_tolerance(self, occurrences: List[List[TelemetryEvent]]) -> float:
        """
        Compares inter-event time deltas across repetitions within configurable tolerance.
        """
        if len(occurrences) <= 1:
            return 1.0

        seq_len = len(occurrences[0])
        if seq_len < 2:
            return 1.0

        # Calculate time deltas for base occurrence
        base_deltas = [
            abs((occurrences[0][i+1].timestamp - occurrences[0][i].timestamp).total_seconds())
            for i in range(seq_len - 1)
        ]

        total_deltas = 0
        valid_deltas = 0

        for occ in occurrences[1:]:
            occ_deltas = [
                abs((occ[i+1].timestamp - occ[i].timestamp).total_seconds())
                for i in range(min(len(occ) - 1, len(base_deltas)))
            ]
            for d_base, d_occ in zip(base_deltas, occ_deltas):
                total_deltas += 1
                if abs(d_base - d_occ) <= self.delta_tolerance_sec:
                    valid_deltas += 1

        return valid_deltas / total_deltas if total_deltas > 0 else 1.0
