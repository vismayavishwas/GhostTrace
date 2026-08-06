import logging
from typing import Dict, Any
from app.models.enums import LangGraphState, IntentChoice
from app.models.workflow import WorkflowCandidate, IntentDecision
from app.agents.observer.observer_agent import ObserverAgent
from app.agents.pattern_discovery.pattern_discovery_agent import PatternDiscoveryAgent
from app.agents.intent_disambiguation.intent_disambiguation_agent import IntentDisambiguationAgent
from app.agents.workflow_dna.workflow_dna_agent import WorkflowDNAAgent
from app.agents.compiler.compiler_agent import CompilerAgent
from app.agents.sandbox.sandbox_agent import SandboxRunnerAgent
from app.agents.self_healing.self_healing_agent import SelfHealingAgent
from app.agents.automation_runner.automation_runner_agent import AutomationRunnerAgent
from app.agents.continuous_observer.observer_agent import ContinuousObserverAgent
from app.orchestration.state import GhostTraceGraphState

logger = logging.getLogger("ghosttrace.orchestration.nodes")

# Initialize singleton agent module instances
_observer = ObserverAgent()
_pattern_discovery = PatternDiscoveryAgent()
_intent_agent = IntentDisambiguationAgent()
_dna_agent = WorkflowDNAAgent()
_compiler = CompilerAgent()
_sandbox_agent = SandboxRunnerAgent()
_self_healing_agent = SelfHealingAgent()
_automation_runner = AutomationRunnerAgent()
_continuous_observer = ContinuousObserverAgent()

# Wire Pub/Sub Event Bus across agent modules
_observer.publisher.subscribe(_pattern_discovery.on_telemetry_event)
_observer.publisher.subscribe(_continuous_observer.on_telemetry_event)
_pattern_discovery.publisher.subscribe(_intent_agent.evaluate_candidate)
_intent_agent.publisher.subscribe(_dna_agent.on_intent_decision)

_dna_agent.publisher.subscribe(_compiler.compile_dna)
_compiler.publisher.subscribe(_sandbox_agent.run_sandbox)
_sandbox_agent.publisher.subscribe(_self_healing_agent.on_sandbox_result)


def get_global_observer() -> ObserverAgent:
    return _observer

def get_global_pattern_discovery() -> PatternDiscoveryAgent:
    return _pattern_discovery

def get_global_intent_agent() -> IntentDisambiguationAgent:
    return _intent_agent

def get_global_dna_agent() -> WorkflowDNAAgent:
    return _dna_agent

def get_global_compiler() -> CompilerAgent:
    return _compiler

def get_global_sandbox_agent() -> SandboxRunnerAgent:
    return _sandbox_agent

def get_global_self_healing_agent() -> SelfHealingAgent:
    return _self_healing_agent

def get_global_automation_runner() -> AutomationRunnerAgent:
    return _automation_runner

def get_global_continuous_observer() -> ContinuousObserverAgent:
    return _continuous_observer



async def node_observing(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """OBSERVING Node: Ingests raw telemetry events into observer buffer."""
    logger.info(f"Node [OBSERVING]: Processing {len(state.telemetry_events)} telemetry events.")
    state.current_state = LangGraphState.OBSERVING
    for event in state.telemetry_events:
        await _observer.process_raw_event(event.model_dump())
    return state


async def node_pattern_discovery(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """PATTERN_DISCOVERY Node: Identifies recurring action sequence candidates."""
    logger.info("Node [PATTERN_DISCOVERY]: Evaluating observation window for recurring workflow candidates.")
    state.current_state = LangGraphState.PATTERN_DISCOVERY
    
    # Process events through pattern discovery agent
    for event in state.telemetry_events:
        candidates = await _pattern_discovery.on_telemetry_event(event)
        if candidates:
            state.discovered_candidates.extend(candidates)

    if not state.discovered_candidates and state.telemetry_events:
        # Fallback candidate creation if explicit n-gram hasn't reached threshold
        step_names = [f"Step {i+1}: {e.event_type} on {e.target_selector or 'element'}" for i, e in enumerate(state.telemetry_events)]
        fallback_candidate = WorkflowCandidate(
            name="Discovered User Workflow",
            observed_steps=step_names,
            sequence_event_ids=[e.event_id for e in state.telemetry_events],
            sequence=state.telemetry_events,
            occurrence_count=2,
            confidence_score=0.90,
            success_rate=1.0
        )
        state.discovered_candidates.append(fallback_candidate)

    if state.discovered_candidates:
        state.workflow_id = state.discovered_candidates[0].candidate_id
    return state


async def node_intent_validation(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """INTENT_VALIDATION Node: Evaluates ambiguity and validates candidate intent."""
    logger.info("Node [INTENT_VALIDATION]: Validating workflow candidate intent.")
    state.current_state = LangGraphState.INTENT_VALIDATION
    
    if state.discovered_candidates:
        cand = state.discovered_candidates[0]
        decision = await _intent_agent.evaluate_candidate(cand)
        state.validated_intent = decision
    else:
        state.validated_intent = IntentDecision(
            workflow_id=state.workflow_id or "wf-default",
            choice=IntentChoice.APPROVED,
            reason="Default auto-approved"
        )
    return state


async def node_workflow_dna(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """WORKFLOW_DNA Node: Synthesizes high-level business WorkflowDNA model."""
    logger.info("Node [WORKFLOW_DNA]: Synthesizing structured WorkflowDNA.")
    state.current_state = LangGraphState.WORKFLOW_DNA
    
    if state.discovered_candidates and state.validated_intent:
        cand = state.discovered_candidates[0]
        if not cand.sequence:
            cand.sequence = state.telemetry_events
        dna = await _dna_agent.extract_dna(cand)
        state.workflow_dna = dna
        state.workflow_id = dna.workflow_id
    return state


async def node_code_generation(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """CODE_GENERATION Node: Compiles modular Playwright Python code."""
    logger.info("Node [CODE_GENERATION]: Compiling modular Playwright Python CodeArtifact.")
    state.current_state = LangGraphState.CODE_GENERATION
    
    if state.workflow_dna:
        artifact = await _compiler.compile_dna(state.workflow_dna)
        state.generated_code = artifact
    return state


async def node_sandbox(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """SANDBOX Node: Validates code execution inside an isolated subprocess."""
    logger.info("Node [SANDBOX]: Executing isolated sandbox validation.")
    state.current_state = LangGraphState.SANDBOX
    
    if state.generated_code:
        result = await _sandbox_agent.run_sandbox(state.generated_code)
        state.sandbox_results.append(result)
    return state


async def node_self_heal(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """SELF_HEAL Node: Diagnoses sandbox failures and synthesizes versioned repairs (v1 -> v2 -> v3)."""
    logger.info("Node [SELF_HEAL]: Initiating self-healing repair loop.")
    state.current_state = LangGraphState.SELF_HEAL
    
    if state.sandbox_results and state.generated_code:
        last_result = state.sandbox_results[-1]
        summary, final_result, repaired_artifact = await _self_healing_agent.heal_artifact(
            last_result,
            state.generated_code,
            max_attempts=3
        )
        state.healing_summary = summary
        state.generated_code = repaired_artifact
        state.sandbox_results.append(final_result)
    return state


async def node_execution(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """EXECUTION Node: Executes production Playwright automation workflow."""
    logger.info("Node [EXECUTION]: Executing production automation workflow.")
    state.current_state = LangGraphState.EXECUTION
    
    if state.generated_code:
        exec_result = await _automation_runner.run_automation(state.generated_code)
        state.execution_status = exec_result
    return state


async def node_continuous_observation(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """CONTINUOUS_OBSERVATION Node: Pushes post-execution feedback into continuous observer."""
    logger.info("Node [CONTINUOUS_OBSERVATION]: Pushing post-execution feedback into continuous observer.")
    state.current_state = LangGraphState.CONTINUOUS_OBSERVATION
    
    if state.telemetry_events:
        for evt in state.telemetry_events:
            obs_candidates = await _continuous_observer.process_telemetry_event(evt)
            if obs_candidates:
                state.discovered_candidates.extend(obs_candidates)
        state.observation_feedback = _continuous_observer.get_notifications()
    return state


def node_failed(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """Terminal FAILED State: Marks graph as failed with error message."""
    logger.error(f"Node [FAILED]: Terminal failure - {state.error_message}")
    state.is_failed = True
    state.is_completed = False
    return state


def node_complete(state: GhostTraceGraphState) -> GhostTraceGraphState:
    """Terminal EXECUTION_COMPLETE State: Marks graph as successfully completed."""
    logger.info("Node [EXECUTION_COMPLETE]: Terminal completion successfully reached.")
    state.is_completed = True
    state.is_failed = False
    return state
