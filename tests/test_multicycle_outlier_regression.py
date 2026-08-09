import logging
from app.models.telemetry import TelemetryEvent, EventType
from app.agents.telemetry.semantic_normalizer import SemanticNormalizer
from app.agents.telemetry.transfer_builder import TransferBuilder
from app.agents.continuous_observer.workflow_discovery import WorkflowDiscoveryEngine
from app.agents.continuous_observer.models import ObservationEvent
from app.agents.pattern_discovery.deviation_detector import DeviationDetector
from app.agents.workflow_dna.dna_transformer import DNATransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_multicycle_outlier")


def build_raw_telemetry_event(
    event_type: EventType,
    app_title: str,
    selector: str,
    field_label: str,
    value: str,
    cycle_id: str
) -> TelemetryEvent:
    return TelemetryEvent(
        event_type=event_type,
        app_title=app_title,
        target_selector=selector,
        field_label=field_label,
        aria_label=field_label,
        input_value=value,
        metadata={
            "field_label": field_label,
            "aria_label": field_label,
            "app_title": app_title,
            "cycle_id": cycle_id
        }
    )


def run_reproduction_test():
    print("\n" + "=" * 70)
    print("MULTI-CYCLE OUTLIER REGRESSION TEST — REPRODUCTION")
    print("=" * 70)

    raw_events = []

    # Cycle 1 (Canonical: A, B, C)
    raw_events.extend([
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-a", "Field A", "ValA1", "cycle-1"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-a", "Field A", "ValA1", "cycle-1"),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-b", "Field B", "ValB1", "cycle-1"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-b", "Field B", "ValB1", "cycle-1"),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-c", "Field C", "ValC1", "cycle-1"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-c", "Field C", "ValC1", "cycle-1"),
        build_raw_telemetry_event(EventType.CLICK, "Target ERP", "#btn-next-record", "Next Record", "Next Record", "cycle-1"),
    ])

    # Cycle 2 (Canonical: A, B, C)
    raw_events.extend([
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-a", "Field A", "ValA2", "cycle-2"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-a", "Field A", "ValA2", "cycle-2"),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-b", "Field B", "ValB2", "cycle-2"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-b", "Field B", "ValB2", "cycle-2"),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-c", "Field C", "ValC2", "cycle-2"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-c", "Field C", "ValC2", "cycle-2"),
        build_raw_telemetry_event(EventType.CLICK, "Target ERP", "#btn-next-record", "Next Record", "Next Record", "cycle-2"),
    ])

    # Cycle 3 (INTENTIONAL OUTLIER: Skipped B -> A, C)
    raw_events.extend([
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-a", "Field A", "ValA3", "cycle-3"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-a", "Field A", "ValA3", "cycle-3"),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-c", "Field C", "ValC3", "cycle-3"),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-c", "Field C", "ValC3", "cycle-3"),
        build_raw_telemetry_event(EventType.CLICK, "Target ERP", "#btn-next-record", "Next Record", "Next Record", "cycle-3"),
    ])

    tb = TransferBuilder()
    transfers = tb.process_telemetry_events(raw_events)

    obs_events = [
        ObservationEvent(
            event_id=e.event_id,
            session_id="sess-multicycle",
            timestamp=e.timestamp,
            event_type=e.event_type if isinstance(e.event_type, str) else e.event_type.value,
            app_title=e.app_title,
            target_selector=e.target_selector or "",
            telemetry_event=e
        )
        for e in raw_events
    ]
    discovery_engine = WorkflowDiscoveryEngine()
    candidates = discovery_engine.analyze_observations(obs_events)

    total_cycle_count = discovery_engine.get_completed_cycle_count()

    dd = DeviationDetector()
    deviations = dd.detect_deviations(transfers)

    cand = candidates[0] if candidates else None
    transformer = DNATransformer()
    dna = transformer.transform_candidate(cand) if cand else None
    field_mappings = dna.metadata.get("field_mappings", []) if dna else []

    outlier_cycle_ids = sorted(list({d.get("cycle_id") for d in deviations if d.get("cycle_id")}))
    outlier_count = len(deviations)
    canonical_cycle_count = total_cycle_count - outlier_count

    canonical_sequence = getattr(dd, "baseline_sequence", [])
    variant_sequences = [
        {"cycle_id": cyc_id, "deviations": [d["reason"] for d in deviations if d.get("cycle_id") == cyc_id]}
        for cyc_id in outlier_cycle_ids
    ]

    print(f"\n" + "=" * 50)
    print(f"FINAL METRICS REPORT:")
    print(f"=" * 50)
    print(f"canonical_cycle_count = {canonical_cycle_count}")
    print(f"total_cycle_count     = {total_cycle_count}")
    print(f"outlier_count         = {outlier_count}")
    print(f"outlier_cycle_ids     = {outlier_cycle_ids}")
    print(f"canonical_sequence    = {canonical_sequence}")
    print(f"variant_sequences    = {variant_sequences}")
    print(f"WorkflowDNA field_mappings:")
    for m in field_mappings:
        print(f"  - Variable: {m['variable_name']} | Source: {m['source_app']} ({m['source_label']}) -> Target: {m['destination_app']} ({m['destination_label']})")
    print(f"=" * 50 + "\n")

    assert total_cycle_count == 3, f"Expected total_cycle_count=3, got {total_cycle_count}"
    assert outlier_count == 1, f"Expected outlier_count=1, got {outlier_count}"
    assert canonical_cycle_count == 2, f"Expected canonical_cycle_count=2, got {canonical_cycle_count}"
    assert outlier_cycle_ids == ["cycle-3"], f"Expected outlier_cycle_ids=['cycle-3'], got {outlier_cycle_ids}"


if __name__ == "__main__":
    run_reproduction_test()
