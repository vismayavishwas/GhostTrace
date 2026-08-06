import logging
from app.orchestration.state import GhostTraceGraphState

logger = logging.getLogger("ghosttrace.orchestration.transitions")


def route_after_sandbox(state: GhostTraceGraphState) -> str:
    """
    Evaluates sandbox execution result.
    Routes to 'execution' if validation succeeded (exit code 0).
    Routes to 'self_heal' if validation failed.
    """
    if not state.sandbox_results:
        logger.warning("No sandbox results present. Routing to self_heal.")
        return "self_heal"

    last_result = state.sandbox_results[-1]
    if last_result.success:
        logger.info("Sandbox validation PASSED. Routing to 'execution'.")
        return "execution"
    else:
        logger.warning("Sandbox validation FAILED. Routing to 'self_heal'.")
        return "self_heal"


def route_after_heal(state: GhostTraceGraphState) -> str:
    """
    Evaluates self-healing repair summary.
    Routes to 'sandbox' if repair succeeded ('PASS').
    Routes to terminal 'failed' if repair budget was exhausted ('FAIL').
    """
    if state.healing_summary and state.healing_summary.overall_status == "PASS":
        logger.info("Self-healing repair PASSED. Re-routing to 'sandbox' for re-validation.")
        return "sandbox"
    else:
        logger.error("Self-healing repair budget EXHAUSTED ('FAIL'). Routing to terminal 'failed' state.")
        state.error_message = "Self-healing repair budget exhausted after 3 attempts."
        return "failed"


def route_after_execution(state: GhostTraceGraphState) -> str:
    """Routes completed execution to continuous observation feedback."""
    logger.info("Automation execution finished. Routing to 'continuous_observation'.")
    return "continuous_observation"


def route_after_continuous_observation(state: GhostTraceGraphState) -> str:
    """
    Terminates graph execution cleanly into terminal 'complete' state.
    Prevents infinite recursive loops while logging observer feedback.
    """
    logger.info("Continuous observation feedback recorded. Terminating graph into 'complete'.")
    return "complete"
