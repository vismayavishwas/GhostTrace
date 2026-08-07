import logging
from typing import List, Dict, Any, Set, Tuple
from app.models.enums import EventType
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate, WorkflowDNA, WorkflowDNAStep

logger = logging.getLogger("ghosttrace.workflow_dna.transformer")

class DNATransformer:
    """
    ⭐ Pure Renderer of Learned Semantic Workflow Graph ⭐
    Transforms TelemetryEvents & SemanticTransfers into a 100% dynamic WorkflowDNA graph.
    Never infers, assumes, or templates field/app names or business steps.
    Consumes SemanticEvent canonical attributes directly from SemanticNormalizer.
    """

    def transform_candidate(self, candidate: WorkflowCandidate) -> WorkflowDNA:
        events = candidate.sequence or []
        steps: List[WorkflowDNAStep] = []
        apps_involved: Set[str] = set()
        inputs_schema: Dict[str, Any] = {}

        from app.agents.telemetry.transfer_builder import global_transfer_builder
        from app.agents.telemetry.semantic_normalizer import SemanticNormalizer
        from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label

        transfers = global_transfer_builder.process_telemetry_events(events) if events else []
        field_mappings: List[Dict[str, Any]] = []

        for xfer in transfers:
            if xfer.is_immediate_correction:
                continue

            src_app = xfer.source_app or "Unknown Application"
            dest_app = xfer.destination_app or "Unknown Application"
            src_lbl = format_clean_entity_label("", xfer.source_entity) or "Unknown Field"
            dest_lbl = format_clean_entity_label("", xfer.destination_entity) or "Unknown Field"

            if src_app != "Unknown Application": apps_involved.add(src_app)
            if dest_app != "Unknown Application": apps_involved.add(dest_app)

            field_mappings.append({
                "transfer_id": xfer.transfer_id,
                "source_entity": xfer.source_entity,
                "source_label": src_lbl,
                "source_app": src_app,
                "destination_entity": xfer.destination_entity,
                "destination_label": dest_lbl,
                "destination_app": dest_app,
                "pasted_value": xfer.pasted_value or "",
                "display_mapping": f"{src_lbl} → {dest_lbl}",
                "full_mapping_title": f"{src_app} ({src_lbl}) ➔ {dest_app} ({dest_lbl})"
            })

        for idx, event in enumerate(events, start=1):
            sem_event = SemanticNormalizer.normalize(event)
            if sem_event:
                app_title = sem_event.app_title or "Unknown Application"
                lbl = sem_event.display_label or "Unknown Field"
                op = (sem_event.operation or "ACTION").upper()

                if "COPY" in op:
                    action_name = f"Copy {lbl} ({app_title})"
                elif "PASTE" in op or "TYPE" in op:
                    action_name = f"Paste into {lbl} ({app_title})"
                elif "CLICK" in op:
                    action_name = f"Click {lbl} ({app_title})"
                else:
                    action_name = f"{op.capitalize()} {lbl} ({app_title})"
            else:
                app_title = getattr(event, "app_title", None) or "Unknown Application"
                raw_target = getattr(event, "target_selector", None) or getattr(event, "element_tag", None) or "Unknown Field"
                clean_target = str(raw_target).replace("#", "").replace(".", " ").strip()
                action_name = f"{getattr(event, 'event_type', 'ACTION')} on {clean_target}"

            if app_title and app_title != "Unknown Application":
                apps_involved.add(app_title)

            parameters: Dict[str, Any] = {}
            if getattr(event, "input_value", None) is not None:
                param_key = f"input_step_{idx}"
                parameters["value"] = event.input_value
                parameters["placeholder_key"] = param_key
                inputs_schema[param_key] = {
                    "type": "string",
                    "description": f"Input value for step {idx} ({action_name})",
                    "default": event.input_value,
                }

            raw_sel = (getattr(event, "target_selector", None) or "").lower()
            for m in field_mappings:
                if any(k in raw_sel for k in [m["source_label"].lower().replace(" ", ""), m["destination_label"].lower().replace(" ", "")] if k):
                    parameters.update(m)
                    break

            fallback_selectors = []
            if getattr(event, "element_tag", None):
                fallback_selectors.append(f"{event.element_tag.lower()}")
            if getattr(event, "target_selector", None):
                fallback_selectors.append(f"//{event.target_selector.replace('#', '')}")

            step = WorkflowDNAStep(
                step_number=idx,
                action_name=action_name,
                target_app=app_title,
                selector=getattr(event, "target_selector", None) or f"<{getattr(event, 'element_tag', None) or 'element'}>",
                fallback_selectors=fallback_selectors,
                parameters=parameters
            )
            steps.append(step)

        app_list = sorted(list(apps_involved))
        if not app_list:
            app_list = ["Unknown Application"]

        primary_app = app_list[0]
        target_app = app_list[-1] if len(app_list) > 1 else primary_app
        workflow_title = f"{primary_app} → {target_app} Data Flow" if primary_app != target_app else f"{primary_app} Workflow"
        workflow_desc = (
            f"Observed semantic workflow mapping {len(field_mappings)} field transfer(s) and {len(steps)} chronological step(s) "
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

        logger.debug(f"DNATransformer rendered WorkflowDNA ID={dna.workflow_id[:8]} with {len(steps)} steps and {len(field_mappings)} mappings")
        return dna


