import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.enums import EventType
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate, WorkflowDNA, WorkflowDNAStep

logger = logging.getLogger("ghosttrace.workflow_dna.transformer")

# Deterministic keyword to action name rules
SELECTOR_ACTION_RULES: List[Tuple[str, str]] = [
    ("submit", "Submit Form"),
    ("save", "Save Record"),
    ("search", "Search Records"),
    ("login", "Authenticate User"),
    ("nav", "Navigate Workspace"),
    ("invoice", "Process Invoice"),
    ("input", "Enter Input Data"),
    ("btn", "Execute Action"),
    ("button", "Click Button"),
    ("link", "Follow Link"),
    ("a", "Navigate Link"),
]


class DNATransformer:
    """
    Deterministic rule-based transformer converting TelemetryEvent sequences into
    high-level semantic WorkflowDNA steps.
    """
    def transform_candidate(self, candidate: WorkflowCandidate) -> WorkflowDNA:
        """
        Transforms a WorkflowCandidate into a validated WorkflowDNA model using rule-based mappings.
        """
        events = candidate.sequence
        steps: List[WorkflowDNAStep] = []
        apps_involved: Set[str] = set()
        inputs_schema: Dict[str, Any] = {}

        for idx, event in enumerate(events, start=1):
            app_title = event.app_title or "Target Application"
            apps_involved.add(app_title)

            # 1. Infer Action Name deterministically
            action_name = self._infer_action_name(event)

            # 2. Extract Parameters & Inputs
            parameters: Dict[str, Any] = {}
            if event.input_value is not None:
                param_key = f"input_step_{idx}"
                parameters["value"] = event.input_value
                parameters["placeholder_key"] = param_key
                inputs_schema[param_key] = {
                    "type": "string",
                    "description": f"Input value for step {idx} ({action_name})",
                    "default": event.input_value,
                }

            # 3. Create WorkflowDNAStep
            fallback_selectors = []
            if event.element_tag:
                fallback_selectors.append(f"{event.element_tag.lower()}")
            if event.target_selector:
                fallback_selectors.append(f"//{event.target_selector.replace('#', '')}")

            step = WorkflowDNAStep(
                step_number=idx,
                action_name=action_name,
                target_app=app_title,
                selector=event.target_selector or f"<{event.element_tag or 'element'}>",
                fallback_selectors=fallback_selectors,
                parameters=parameters
            )
            steps.append(step)

        # Build primary workflow title and description
        app_list = sorted(list(apps_involved))
        primary_app = app_list[0] if app_list else "Application"
        workflow_title = f"{primary_app} Workflow Automation"
        workflow_desc = (
            f"Deterministic workflow spanning {len(steps)} steps across "
            f"{', '.join(app_list)}."
        )

        output_schema = {
            "status": "string",
            "execution_result": "object",
            "completed_steps": len(steps),
        }

        dna = WorkflowDNA(
            name=workflow_title,
            description=workflow_desc,
            steps=steps,
            inputs_schema=inputs_schema,
            output_schema=output_schema,
            applications_involved=app_list,
            confidence_score=candidate.confidence_score,
            metadata={
                "candidate_id": candidate.candidate_id,
                "repetition_count": candidate.repetition_count,
                "sequence_event_ids": candidate.sequence_event_ids,
            }
        )

        logger.debug(f"DNATransformer created WorkflowDNA ID={dna.workflow_id[:8]} with {len(steps)} steps")
        return dna

    def _infer_action_name(self, event: TelemetryEvent) -> str:
        """
        Determines high-level semantic action name using a hybrid architecture:
        1. High-confidence deterministic rule match -> Instant return.
        2. Low-confidence complex selector (e.g. div:nth-child(7) > span) -> Gemini model inference.
        """
        selector = (event.target_selector or "").lower()
        tag = (event.element_tag or "").lower()
        event_type = str(event.event_type).upper()

        # Step 1: High-Confidence Deterministic Rule Matching
        for keyword, semantic_name in SELECTOR_ACTION_RULES:
            if keyword in selector or keyword in tag:
                return f"{semantic_name} ({event.app_title})"

        # Step 2: Low-Confidence Unrecognized Complex Selector -> Call Gemini Service
        if len(selector) > 15 or "nth-child" in selector or ">" in selector:
            from app.services.gemini_service import gemini_service
            prompt = (
                f"Analyze this DOM element selector and event type to generate a concise, human-readable action name (3-5 words).\n"
                f"Application: {event.app_title}\n"
                f"Event Type: {event_type}\n"
                f"Selector: {event.target_selector}\n"
                f"Element Tag: {event.element_tag}\n"
                f"Output only the action name title."
            )
            def rule_fallback():
                return f"Click Element {selector[:15]} ({event.app_title})"

            gemini_name, elapsed, status = gemini_service.generate(
                prompt=prompt,
                purpose="semantic_action_inference",
                fallback_fn=rule_fallback
            )
            if gemini_name and not status.startswith("FALLBACK"):
                return f"{gemini_name} ({event.app_title})"

        # Step 3: Standard Fallback Action Rules
        if event_type in ["TYPE", "KEYPRESS"]:
            return f"Enter Input Data ({event.app_title})"
        elif event_type in ["CLICK", "DOUBLE_CLICK"]:
            return f"Click Target ({event.app_title})"
        elif event_type == "NAVIGATION":
            return f"Navigate Page ({event.app_title})"
        else:
            return f"Perform {event_type} ({event.app_title})"

