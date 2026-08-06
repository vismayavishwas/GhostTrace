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
        else:
            self._table[key] = {
                "source_entity": transfer.source_entity,
                "destination_entity": transfer.destination_entity,
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


    def get_expected_destination(self, source_entity: str) -> Optional[str]:
        """Returns the expected stable destination entity for a given source_entity, if available."""
        src = source_entity.lower()
        if src not in self._source_destinations:
            return None

        # Return destination with highest occurrence count
        sorted_dests = sorted(self._source_destinations[src].items(), key=lambda x: x[1], reverse=True)
        return sorted_dests[0][0] if sorted_dests else None

    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """Returns snapshot of all stored stable mappings."""
        return [
            {"key": f"{k[0]} -> {k[1]}", **v}
            for k, v in self._table.items()
        ]


global_mapping_memory = StableMappingMemory()
