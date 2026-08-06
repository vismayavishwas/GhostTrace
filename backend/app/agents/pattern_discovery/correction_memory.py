import logging
from typing import Dict, Any, List, Set, Tuple
from datetime import datetime

logger = logging.getLogger("ghosttrace.pattern_discovery.correction_memory")


class CorrectionPatternStore:
    """
    Persistent Memory Layer for confirmed user accidental correction patterns.
    
    Structure:
    (source_entity, wrong_destination) -> {
        "correction_count": int,
        "first_seen": str,
        "last_seen": str,
        "user_confirmed_accidental": bool
    }
    
    Intelligent Behavior:
    When a user confirms a mistake ("Was this accidental? Yes"), GhostTrace stores the exact tuple.
    If the mistake recurs in future cycles (even months later), GhostTrace immediately recognizes it
    as a previously confirmed accidental correction pattern, skipping redundant prompts and auto-filtering.
    """
    def __init__(self):
        # In-memory store: (source_entity, wrong_destination) -> Metadata dict
        self._memory: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def record_confirmed_correction(self, source_entity: str, wrong_destination: str) -> None:
        """Stores a user-confirmed accidental correction pattern in persistent memory."""
        key = (source_entity.lower(), wrong_destination.lower())
        now_str = datetime.utcnow().isoformat()

        if key in self._memory:
            self._memory[key]["correction_count"] += 1
            self._memory[key]["last_seen"] = now_str
        else:
            self._memory[key] = {
                "source_entity": source_entity,
                "wrong_destination": wrong_destination,
                "correction_count": 1,
                "first_seen": now_str,
                "last_seen": now_str,
                "user_confirmed_accidental": True
            }

        logger.info(f"CorrectionPatternStore recorded confirmed accidental pattern: {source_entity} -> {wrong_destination}")

    def is_known_accidental_correction(self, source_entity: str, wrong_destination: str) -> bool:
        """Checks whether a source_entity -> wrong_destination transfer is a previously confirmed accidental correction."""
        key = (source_entity.lower(), wrong_destination.lower())
        return key in self._memory and self._memory[key].get("user_confirmed_accidental", False)

    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Returns snapshot of all stored correction patterns."""
        return [
            {
                "source_entity": k[0],
                "wrong_destination": k[1],
                **v
            }
            for k, v in self._memory.items()
        ]


global_correction_memory = CorrectionPatternStore()
