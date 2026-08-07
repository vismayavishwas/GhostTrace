from enum import Enum


class LangGraphState(str, Enum):
    """
    Deterministic states for the GhostTrace AI LangGraph state machine.
    """
    IDLE = "IDLE"
    OBSERVING = "OBSERVING"
    PATTERN_DISCOVERY = "PATTERN_DISCOVERY"
    INTENT_VALIDATION = "INTENT_VALIDATION"
    WORKFLOW_DNA = "WORKFLOW_DNA"
    CODE_GENERATION = "CODE_GENERATION"
    SANDBOX = "SANDBOX"
    SELF_HEAL = "SELF_HEAL"
    EXECUTION = "EXECUTION"
    CONTINUOUS_OBSERVATION = "CONTINUOUS_OBSERVATION"


class AgentStatus(str, Enum):
    """
    Status values for agents and background workers.
    """
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class EventType(str, Enum):
    """
    Categories of captured user perception telemetry events.
    """
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    TYPE = "TYPE"
    KEYPRESS = "KEYPRESS"
    SCROLL = "SCROLL"
    DOM_MUTATION = "DOM_MUTATION"
    APP_SWITCH = "APP_SWITCH"
    NAVIGATION = "NAVIGATION"
    COPY = "COPY"
    PASTE = "PASTE"
    SELECT = "SELECT"
    SUBMIT = "SUBMIT"


class IntentChoice(str, Enum):
    """
    Human-in-the-loop intent classification choices.
    """
    MISTAKE = "MISTAKE"
    BRANCH = "BRANCH"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
