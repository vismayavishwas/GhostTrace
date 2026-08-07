import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from app.agents.telemetry.transfer_builder import SemanticTransfer

logger = logging.getLogger("ghosttrace.pattern_discovery.mapping_memory")


class StableMappingMemory:
    """
    Deterministic Stable Mapping Table.
    
    Structure:
    (source_entity, destination_entity) -> {
        "occurrences": int,
        "confidence": float,
        "first_seen": str,
        "last_seen": str,
        "status": "OBSERVED" | "STABLE_LOCKED" | "DEVIATED"
    }
    """
    def __init__(self, min_lock_threshold: int = 3):
        self.min_lock_threshold = min_lock_threshold
        # Key: (source_entity, destination_entity) -> Dict
        self._table: Dict[Tuple[str, str], Dict[str, Any]] = {}
        # Source Entity -> List of mapped destination entities
        self._source_destinations: Dict[str, Dict[str, int]] = {}

    def record_transfer(self, transfer: SemanticTransfer) -> Dict[str, Any]:
        """Records a high-level transfer into the Stable Mapping Memory Table."""
        if transfer.is_immediate_correction:
            logger.info(f"StableMappingMemory skipped superseded transfer: {transfer.source_entity} -> {transfer.superseded_destination}")
            return {}

        src = transfer.source_entity.lower()
        dest = transfer.destination_entity.lower()
        key = (src, dest)
        now_str = datetime.now(timezone.utc).isoformat()

        if src not in self._source_destinations:
            self._source_destinations[src] = {}
        self._source_destinations[src][dest] = self._source_destinations[src].get(dest, 0) + 1

        total_transfers_for_src = sum(self._source_destinations[src].values())
        dest_count = self._source_destinations[src][dest]
        consistency_ratio = dest_count / total_transfers_for_src
        sample_weight = min(1.0, dest_count / self.min_lock_threshold)
        confidence = round(consistency_ratio * sample_weight, 2)

        is_locked = (dest_count >= self.min_lock_threshold) and (len(self._source_destinations[src]) == 1)
        status = "STABLE_LOCKED" if is_locked else ("DEVIATED" if len(self._source_destinations[src]) > 1 else "OBSERVED")


        if key in self._table:
            self._table[key]["occurrences"] += 1
            self._table[key]["confidence"] = confidence
            self._table[key]["last_seen"] = now_str
            self._table[key]["status"] = status
            if getattr(transfer, "source_display_label", None):
                self._table[key]["source_display_label"] = transfer.source_display_label
            if getattr(transfer, "destination_display_label", None):
                self._table[key]["destination_display_label"] = transfer.destination_display_label
        else:
            self._table[key] = {
                "source_entity": transfer.source_entity,
                "source_display_label": getattr(transfer, "source_display_label", "") or transfer.source_entity,
                "source_app": getattr(transfer, "source_app", ""),
                "destination_entity": transfer.destination_entity,
                "destination_display_label": getattr(transfer, "destination_display_label", "") or transfer.destination_entity,
                "destination_app": getattr(transfer, "destination_app", ""),
                "occurrences": 1,
                "confidence": confidence,
                "first_seen": now_str,
                "last_seen": now_str,
                "status": status
            }

        logger.info(
            f"[STAGE 2: MAPPING_MEMORY] Record Transfer | Key=('{src}' -> '{dest}') | "
            f"Occurrences={dest_count} | Confidence={confidence:.2f} | Status={status}"
        )
        logger.info(
            f"[STAGE 2: MAPPING_MEMORY Table Dump] Current Entries ({len(self._table)}): "
            + ", ".join([f"[{v['source_entity']} -> {v['destination_entity']}: Occ={v['occurrences']}, Conf={v['confidence']}, Status={v['status']}]" for v in self._table.values()])
        )
        return self._table[key]


    def get_expected_destination(self, source_entity: str, min_occurrences: int = 1) -> Optional[str]:
        """Returns the expected stable destination entity for a given source_entity, if available and sufficiently observed (at least min_occurrences)."""
        src = source_entity.lower()
        if src in self._source_destinations:
            sorted_dests = sorted(self._source_destinations[src].items(), key=lambda x: x[1], reverse=True)
            if sorted_dests and sorted_dests[0][1] >= min_occurrences:
                return sorted_dests[0][0]

        # Fuzzy / Semantic Field Matching Fallback if exact string match not found:
        from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label
        src_label = format_clean_entity_label("", src).lower()
        src_app = src.split(":")[1] if ":" in src else ""

        for stored_src, dests in self._source_destinations.items():
            stored_src_label = format_clean_entity_label("", stored_src).lower()
            stored_src_app = stored_src.split(":")[1] if ":" in stored_src else ""

            if (src_app == stored_src_app) and (
                src_label == stored_src_label or 
                src_label in stored_src_label or 
                stored_src_label in src_label
            ):
                sorted_dests = sorted(dests.items(), key=lambda x: x[1], reverse=True)
                if sorted_dests and sorted_dests[0][1] >= min_occurrences:
                    return sorted_dests[0][0]

        return None

    def get_overall_semantic_consistency_confidence(self, completed_cycles: int) -> Tuple[float, str]:
        """
        Computes emerging semantic confidence from observed mapping consistency & accumulated cycle evidence.
        No hardcoded fixed percentages assigned to cycle numbers!
        Returns (confidence_score, status_label).
        """
        if completed_cycles < 2 or not self._source_destinations:
            return 0.00, "OBSERVED"

        consistency_scores = []
        for src, dests in self._source_destinations.items():
            total_src = sum(dests.values())
            if total_src > 0:
                top_dest_count = max(dests.values())
                ratio = top_dest_count / total_src
                consistency_scores.append(ratio)

        if not consistency_scores:
            return 0.00, "OBSERVED"

        import math
        avg_consistency = sum(consistency_scores) / len(consistency_scores)
        evidence_weight = 1.0 - math.exp(-0.55 * (completed_cycles - 1))
        
        emerging_confidence = min(1.00, round(avg_consistency * evidence_weight, 2))

        if emerging_confidence >= 0.90 or (completed_cycles >= 3 and avg_consistency >= 0.90):
            return 1.00, "STABLE_LOCKED"
        
        return emerging_confidence, "WATCHING"



global_mapping_memory = StableMappingMemory()

