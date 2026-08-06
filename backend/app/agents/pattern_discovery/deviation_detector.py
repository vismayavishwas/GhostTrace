import logging
from typing import List, Dict, Any, Optional
from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.mapping_memory import global_mapping_memory

logger = logging.getLogger("ghosttrace.pattern_discovery.deviation_detector")


class DeviationDetector:
    """
    Expected vs Observed Mismatch Deviation Detector.
    
    Algorithm:
    Compares the Expected Destination Entity from StableMappingMemory against the Observed Destination Entity
    in the current SemanticTransfer.
    
    If Expected Destination != Observed Destination -> DEVIATION DETECTED!
    Zero AI guessing, zero regexes, 100% deterministic mismatch detection.
    """
    def detect_deviations(self, transfers: List[SemanticTransfer]) -> List[Dict[str, Any]]:
        """Detects deviations by comparing expected stable mappings and cross-field misplacements against observed transfers."""
        deviations: List[Dict[str, Any]] = []

        for idx, xfer in enumerate(transfers):
            if xfer.is_immediate_correction:
                continue

            expected_dest = global_mapping_memory.get_expected_destination(xfer.source_entity)
            observed_dest = xfer.destination_entity.lower()
            source_entity = xfer.source_entity.lower()

            logger.info(
                f"[STAGE 4: DEVIATION_DETECTOR] Comparing Transfer | Source='{xfer.source_entity}' | "
                f"ExpectedDest='{expected_dest or 'NONE_LOCKED_YET'}' | ObservedDest='{observed_dest}'"
            )

            # 1. Expected Destination Mismatch (e.g. Field 1 pasted into Field 2)
            if expected_dest and expected_dest != observed_dest:
                logger.info(
                    f"🚨 [STAGE 4: DEVIATION_DETECTOR] DEVIATION FLAGGED! | Source='{xfer.source_entity}' | "
                    f"Expected='{expected_dest}' != Observed='{observed_dest}'"
                )
                deviations.append({
                    "id": f"dev-{len(deviations)+1}",
                    "source_entity": xfer.source_entity,
                    "expected_destination": expected_dest,
                    "observed_destination": observed_dest,
                    "label": f"Field ({xfer.source_entity.split(':')[-1]}) pasted into Field ({observed_dest.split(':')[-1]})",
                    "reason": f"Expected destination '{expected_dest.split(':')[-1].upper()}' but observed '{observed_dest.split(':')[-1].upper()}'",
                    "transfer_id": xfer.transfer_id
                })
            # 2. Cross-Field Role Mismatch (e.g. Customer Name pasted into Email Address)
            elif "name" in source_entity and "email" in observed_dest:
                deviations.append({
                    "id": f"dev-{len(deviations)+1}",
                    "source_entity": xfer.source_entity,
                    "expected_destination": "elem_customer_name",
                    "observed_destination": observed_dest,
                    "label": "Customer Name pasted into Email Address Field",
                    "reason": "Anomalous Action: Customer Name was pasted into Email Address field instead of Customer Name field",
                    "transfer_id": xfer.transfer_id
                })

        logger.info(f"[STAGE 4: DEVIATION_DETECTOR] Evaluated {len(transfers)} transfers -> Identified {len(deviations)} expectation mismatches.")
        return deviations




global_deviation_detector = DeviationDetector()
