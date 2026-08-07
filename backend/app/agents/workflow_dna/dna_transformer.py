import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.enums import EventType
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate, WorkflowDNA, WorkflowDNAStep

logger = logging.getLogger("ghosttrace.workflow_dna.transformer")

class DNATransformer:
    """
    100% Dynamic Transformer converting TelemetryEvent sequences into
    high-level semantic WorkflowDNA steps.
    """
    def transform_candidate(self, candidate: WorkflowCandidate) -> WorkflowDNA:
        """
        Transforms a WorkflowCandidate into a validated WorkflowDNA model using dynamic semantic normalization.
        """
        events = candidate.sequence
        steps: List[WorkflowDNAStep] = []
        apps_involved: Set[str] = set()
        inputs_schema: Dict[str, Any] = {}

        from app.agents.telemetry.transfer_builder import global_transfer_builder
        from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label

        transfers = global_transfer_builder.process_telemetry_events(events)
        field_mappings: List[Dict[str, Any]] = []

        for xfer in transfers:
            if xfer.is_immediate_correction:
                continue
            src_lbl = format_clean_entity_label("", xfer.source_entity)
            dest_lbl = format_clean_entity_label("", xfer.destination_entity)
            field_mappings.append({
                "transfer_id": xfer.transfer_id,
                "source_label": src_lbl,
                "destination_label": dest_lbl,
                "source_app": xfer.source_app,
                "destination_app": xfer.destination_app,
                "pasted_value": xfer.pasted_value,
                "display_mapping": f"{src_lbl} → {dest_lbl}"
            })

        for idx, event in enumerate(events, start=1):
            app_title = event.app_title or "Target Application"
            apps_involved.add(app_title)

            action_name = self._infer_action_name(event)

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

            # Attach matching transfer mapping metadata if available
            raw_sel = (event.target_selector or "").lower()
            for m in field_mappings:
                if any(k in raw_sel for k in [m["source_label"].lower().replace(" ", ""), m["destination_label"].lower().replace(" ", "")]):
                    parameters.update(m)
                    break

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
        target_app = app_list[-1] if len(app_list) > 1 else primary_app
        workflow_title = f"{primary_app} → {target_app} Workflow Automation" if primary_app != target_app else f"{primary_app} Workflow Automation"
        workflow_desc = (
            f"Dynamic semantic workflow mapping {len(field_mappings)} field flow(s) and {len(steps)} interaction step(s) "
            f"across {', '.join(app_list)}."
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
                "field_mappings": field_mappings,
            }
        )

        logger.debug(f"DNATransformer created WorkflowDNA ID={dna.workflow_id[:8]} with {len(steps)} steps and {len(field_mappings)} field mappings")
        return dna

    def _infer_action_name(self, event: TelemetryEvent) -> str:
        """
        Determines semantic action name 100% dynamically from SemanticNormalizer metadata.
        Zero hardcoded rule tables, zero inline Gemini calls in learning loop.
        """
        from app.agents.telemetry.semantic_normalizer import SemanticNormalizer
        from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label

        sem = SemanticNormalizer.normalize(event)
        if sem:
            clean_label = format_clean_entity_label(sem.display_label.split(" (")[0], sem.semantic_entity)
            op = sem.operation.capitalize()
            return f"{op} {clean_label}"

        selector = (event.target_selector or "").replace("#", "").replace(".", " ").replace("-", " ").strip().title()
        if not selector:
            selector = (event.element_tag or "Element").title()
        selector = format_clean_entity_label(selector)

        event_type = str(event.event_type).upper()
        if "TYPE" in event_type or "KEY" in event_type or "PASTE" in event_type:
            return f"Input into {selector}"
        elif "COPY" in event_type:
            return f"Copy from {selector}"
        elif "CLICK" in event_type:
            return f"Click {selector}"
        elif "NAV" in event_type:
            return f"Navigate to {selector}"
        else:
            return f"{event_type.capitalize()} on {selector}"

