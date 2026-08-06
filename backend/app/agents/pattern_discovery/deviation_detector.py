import logging
from typing import List, Dict, Any, Optional
from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.mapping_memory import global_mapping_memory

logger = logging.getLogger("ghosttrace.pattern_discovery.deviation_detector")


class DeviationDetector:
    """
    100% Dynamic Positional Sequence Mismatch & Destination Deviation Detector.
    
    Algorithm:
    1. Mapping Memory Check: Compares Expected Destination for source_entity against Observed Destination.
    2. Positional Sequence Step Check: Compares Step i of active run against Step i of established sequence template.
    
    Zero hardcoded strings, zero domain checks ("name", "email", "invoice"), zero regexes.
    Pure structural sequence position and entity equivalence comparison.
    """
    def __init__(self):
        self._established_transfer_sequence: List[Tuple[str, str]] = []

    def detect_deviations(self, transfers: List[SemanticTransfer]) -> List[Dict[str, Any]]:
        """Detects deviations by comparing expected stable mappings and positional step sequence templates against observed transfers."""
        deviations: List[Dict[str, Any]] = []

        # Lock first completed transfer sequence as the established pattern template
        if not self._established_transfer_sequence and len(transfers) >= 2:
            self._established_transfer_sequence = [(x.source_entity.lower(), x.destination_entity.lower()) for x in transfers if not x.is_immediate_correction]

        for idx, xfer in enumerate(transfers):
            if xfer.is_immediate_correction:
                continue

            src = xfer.source_entity.lower()
            observed_dest = xfer.destination_entity.lower()
            expected_dest = global_mapping_memory.get_expected_destination(src)

            logger.info(
                f"[STAGE 4: DEVIATION_DETECTOR] Step {idx+1} | Source='{src}' | "
                f"ExpectedDest='{expected_dest or 'NONE_LOCKED_YET'}' | ObservedDest='{observed_dest}'"
            )

            # 1. Mapping Memory Mismatch Check
            if expected_dest and expected_dest != observed_dest:
                logger.info(
                    f"🚨 [STAGE 4: DEVIATION_DETECTOR] DEVIATION FLAGGED (Mapping Mismatch)! | Source='{src}' | "
                    f"Expected='{expected_dest}' != Observed='{observed_dest}'"
                )
                deviations.append({
                    "id": f"dev-{len(deviations)+1}",
                    "source_entity": xfer.source_entity,
                    "expected_destination": expected_dest,
                    "observed_destination": observed_dest,
                    "label": f"Step {idx+1} Field Mismatch ({src.split(':')[-1]}) → ({observed_dest.split(':')[-1]})",
                    "reason": f"Workflow Mismatch: Expected destination '{expected_dest.split(':')[-1]}' but observed '{observed_dest.split(':')[-1]}'",
                    "transfer_id": xfer.transfer_id
                })
            # 2. Positional Sequence Step Mismatch Check (Step i of active run vs Step i of template)
            elif idx < len(self._established_transfer_sequence):
                exp_seq_src, exp_seq_dest = self._established_transfer_sequence[idx]
                if observed_dest != exp_seq_dest:
                    logger.info(
                        f"🚨 [STAGE 4: DEVIATION_DETECTOR] DEVIATION FLAGGED (Sequence Positional Mismatch)! | Step={idx+1} | "
                        f"ExpectedStepDest='{exp_seq_dest}' != ObservedStepDest='{observed_dest}'"
                    )
                    deviations.append({
                        "id": f"dev-{len(deviations)+1}",
                        "source_entity": xfer.source_entity,
                        "expected_destination": exp_seq_dest,
                        "observed_destination": observed_dest,
                        "label": f"Step {idx+1} Positional Sequence Deviation",
                        "reason": f"Step {idx+1} Sequence Deviation: Expected target '{exp_seq_dest.split(':')[-1]}' but observed '{observed_dest.split(':')[-1]}'",
                        "transfer_id": xfer.transfer_id
                    })

        logger.info(f"[STAGE 4: DEVIATION_DETECTOR] Evaluated {len(transfers)} transfers -> Identified {len(deviations)} expectation mismatches.")
        return deviations





global_deviation_detector = DeviationDetector()
