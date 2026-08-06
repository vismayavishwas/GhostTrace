import logging
from typing import List, Dict, Any, Optional
from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.mapping_memory import global_mapping_memory

logger = logging.getLogger("ghosttrace.pattern_discovery.deviation_detector")


class DeviationDetector:
    """
    100% Dynamic Positional & Mapping Deviation Detector.
    Zero hardcoded field names, zero domain regexes, zero string assumptions.
    
    Algorithm:
    1. Mapping Deviation: Compares Expected Destination for source_entity from Mapping Memory vs Observed Destination.
    2. Sequence Step Deviation: Compares Step i destination against established step i template.
    """
    def __init__(self):
        self._established_sequence_dests: List[str] = []

    def set_sequence_template(self, dest_entities: List[str]):
        """Sets established sequence destination template from workflow discovery."""
        self._established_sequence_dests = [d.lower() for d in dest_entities]

    def detect_deviations(self, transfers: List[SemanticTransfer]) -> List[Dict[str, Any]]:
        """Detects deviations by comparing expected stable mappings & positional step sequence against observed transfers."""
        deviations: List[Dict[str, Any]] = []

        for idx, xfer in enumerate(transfers):
            if xfer.is_immediate_correction:
                continue

            expected_dest = global_mapping_memory.get_expected_destination(xfer.source_entity)
            observed_dest = xfer.destination_entity.lower()

            # Positional Sequence Step Expectation (Step idx in current sequence)
            positional_expected = None
            if idx < len(self._established_sequence_dests):
                positional_expected = self._established_sequence_dests[idx]

            target_expected = expected_dest or positional_expected

            logger.info(
                f"[STAGE 4: DEVIATION_DETECTOR] Comparing Step {idx+1} | Source='{xfer.source_entity}' | "
                f"ExpectedDest='{target_expected or 'NONE'}' | ObservedDest='{observed_dest}'"
            )

            # Pure Entity Key Comparison — 100% Dynamic
            if target_expected and observed_dest != target_expected:
                logger.info(
                    f"🚨 [STAGE 4: DEVIATION_DETECTOR] DEVIATION FLAGGED! | Step={idx+1} | "
                    f"Expected='{target_expected}' != Observed='{observed_dest}'"
                )
                src_token = xfer.source_entity.split(":")[-1].replace("_", " ").title()
                exp_token = target_expected.split(":")[-1].replace("_", " ").title()
                obs_token = observed_dest.split(":")[-1].replace("_", " ").title()

                deviations.append({
                    "id": f"dev-{len(deviations)+1}",
                    "source_entity": xfer.source_entity,
                    "expected_destination": target_expected,
                    "observed_destination": observed_dest,
                    "label": f"Field ({src_token}) pasted into Field ({obs_token}) at Step {idx+1}",
                    "reason": f"Workflow Deviation Mismatch: Expected Step {idx+1} target '{exp_token}' but observed '{obs_token}'",
                    "transfer_id": xfer.transfer_id
                })

        logger.info(f"[STAGE 4: DEVIATION_DETECTOR] Evaluated {len(transfers)} transfers -> Identified {len(deviations)} expectation mismatches.")
        return deviations





global_deviation_detector = DeviationDetector()
