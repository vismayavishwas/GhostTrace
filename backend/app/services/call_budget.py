import logging
from typing import Dict

logger = logging.getLogger("ghosttrace.gemini.budget")

class GeminiCallBudget:
    """
    Per-workflow Gemini Call Budget Manager.
    Guarantees each workflow triggers Gemini at most ONCE for:
      - 'intent' (IntentDisambiguationAgent)
      - 'business' (BusinessProcessAgent)
      - 'repair' (SelfHealingAgent)
    Prevents repeated LLM calls during frontend polling or state updates.
    """
    def __init__(self):
        self._calls: Dict[str, Dict[str, bool]] = {}

    def can_call(self, workflow_id: str, purpose: str) -> bool:
        if workflow_id not in self._calls:
            self._calls[workflow_id] = {"intent": False, "business": False, "repair": False}
        
        has_called = self._calls[workflow_id].get(purpose, False)
        if has_called:
            logger.info(f"Gemini call budget already fulfilled for workflow '{workflow_id}' ({purpose}). Skipping duplicate API call.")
            return False
        return True

    def mark_called(self, workflow_id: str, purpose: str):
        if workflow_id not in self._calls:
            self._calls[workflow_id] = {"intent": False, "business": False, "repair": False}
        self._calls[workflow_id][purpose] = True
        logger.info(f"Gemini call budget updated: workflow '{workflow_id}' marked as called for '{purpose}'.")

    def reset(self):
        self._calls.clear()
        logger.info("Gemini call budget reset.")

gemini_budget = GeminiCallBudget()
