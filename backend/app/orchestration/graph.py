import inspect
import logging
from typing import Optional, Dict, Any, Callable
from app.models.enums import LangGraphState
from app.orchestration.state import GhostTraceGraphState
from app.orchestration.nodes import (
    node_observing,
    node_pattern_discovery,
    node_intent_validation,
    node_workflow_dna,
    node_code_generation,
    node_sandbox,
    node_self_heal,
    node_execution,
    node_continuous_observation,
    node_failed,
    node_complete,
)
from app.orchestration.transitions import (
    route_after_sandbox,
    route_after_heal,
    route_after_execution,
    route_after_continuous_observation,
)

logger = logging.getLogger("ghosttrace.orchestration.graph")


class GhostTraceOrchestrator:
    """
    Central LangGraph State Machine Orchestrator for GhostTrace AI.
    Connects existing backend agent modules into a deterministic, non-recursive state-machine.
    Guarantees every execution terminates with EXECUTION_COMPLETE or FAILED.
    """
    def __init__(self):
        self.nodes = {
            "observing": node_observing,
            "pattern_discovery": node_pattern_discovery,
            "intent_validation": node_intent_validation,
            "workflow_dna": node_workflow_dna,
            "code_generation": node_code_generation,
            "sandbox": node_sandbox,
            "self_heal": node_self_heal,
            "execution": node_execution,
            "continuous_observation": node_continuous_observation,
            "failed": node_failed,
            "complete": node_complete,
        }
        logger.info(f"GhostTraceOrchestrator initialized with {len(self.nodes)} registered agent node wrappers.")

    async def run_graph(self, initial_state: GhostTraceGraphState) -> GhostTraceGraphState:
        """
        Executes the state machine graph from initial_state until a terminal state
        (is_completed=True or is_failed=True) is reached.
        """
        state = initial_state
        logger.info(f"Starting GhostTrace AI Graph Execution Session ID={state.session_id[:8]}")

        # Start at OBSERVING
        current_node_key = "observing"

        while not state.is_completed and not state.is_failed:
            node_fn = self.nodes.get(current_node_key)
            if not node_fn:
                state.error_message = f"Node key '{current_node_key}' not registered in orchestrator."
                return node_failed(state)

            logger.info(f"Executing Graph Node: [{current_node_key.upper()}]")
            
            # Execute node (async or sync)
            if inspect.iscoroutinefunction(node_fn):
                state = await node_fn(state)
            else:
                state = node_fn(state)

            # Determine Next Transition
            if current_node_key == "observing":
                current_node_key = "pattern_discovery"
            elif current_node_key == "pattern_discovery":
                current_node_key = "intent_validation"
            elif current_node_key == "intent_validation":
                current_node_key = "workflow_dna"
            elif current_node_key == "workflow_dna":
                current_node_key = "code_generation"
            elif current_node_key == "code_generation":
                current_node_key = "sandbox"
            elif current_node_key == "sandbox":
                current_node_key = route_after_sandbox(state)
            elif current_node_key == "self_heal":
                current_node_key = route_after_heal(state)
            elif current_node_key == "execution":
                current_node_key = route_after_execution(state)
            elif current_node_key == "continuous_observation":
                current_node_key = route_after_continuous_observation(state)
            elif current_node_key == "failed" or current_node_key == "complete":
                break

        logger.info(f"GhostTrace AI Graph Execution Finished. Session ID={state.session_id[:8]} State={state.current_state}")
        return state

    def get_graph_ascii_visualization(self) -> str:
        """Returns textual ASCII visualization of the state machine graph."""
        return """
===================================================================
             GhostTrace AI LangGraph Orchestration Graph
===================================================================

                        [ IDLE ]
                           |
                           v
                     [ OBSERVING ]
                           |
                           v
                  [ PATTERN_DISCOVERY ]
                           |
                           v
                 [ INTENT_VALIDATION ]
                           |
                           v
                    [ WORKFLOW_DNA ]
                           |
                           v
                   [ CODE_GENERATION ]
                           |
                           v
   +-----------------> [ SANDBOX ]
   |                       |
   |              +--------+--------+
   |              v                 v
   |           (FAIL)            (PASS)
   |              |                 |
   |              v                 |
   |        [ SELF_HEAL ]           |
   |              |                 |
   |     +--------+--------+        |
   |     v                 v        |
   |  (REPAIRED)      (EXHAUSTED)   |
   +-- PASS                |        |
                           v        |
                       [ FAILED ]   |
                      (Terminal)    |
                                    v
                              [ EXECUTION ]
                                    |
                                    v
                         [ CONTINUOUS_OBSERVATION ]
                                    |
                                    v
                         [ EXECUTION_COMPLETE ]
                               (Terminal)
===================================================================
"""

