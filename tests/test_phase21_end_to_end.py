import asyncio
import logging
from datetime import datetime, timezone
from app.models.telemetry import TelemetryEvent, EventType
from app.agents.telemetry.semantic_normalizer import SemanticNormalizer
from app.agents.telemetry.transfer_builder import TransferBuilder
from app.agents.continuous_observer.workflow_discovery import WorkflowDiscoveryEngine
from app.agents.continuous_observer.models import ObservationEvent
from app.agents.pattern_discovery.deviation_detector import DeviationDetector
from app.agents.pattern_discovery.mapping_memory import StableMappingMemory
from app.agents.workflow_dna.dna_transformer import DNATransformer
from app.models.workflow import WorkflowCandidate
from app.agents.ghost_replay.path_extractor import TrajectoryExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_phase21")


def build_raw_telemetry_event(
    event_type: EventType,
    app_title: str,
    selector: str,
    field_label: str,
    value: str,
    x: float,
    y: float,
    is_automated: bool = False
) -> TelemetryEvent:
    return TelemetryEvent(
        event_type=event_type,
        app_title=app_title,
        target_selector=selector,
        field_label=field_label,
        aria_label=field_label,
        input_value=value,
        coordinates_x=int(x),
        coordinates_y=int(y),
        metadata={
            "field_label": field_label,
            "aria_label": field_label,
            "app_title": app_title,
            "is_automated": is_automated
        }
    )


def run_phase21_acceptance_test():
    print("\n" + "=" * 70)
    print("GHOSTTRACE PHASE 21 END-TO-END ACCEPTANCE TEST")
    print("=" * 70)

    # 1. Simulate 3 Manual Records (Copy Field 1, 2, 3 -> Paste Field 1, 2, 3 -> Next Record)
    raw_events = []
    
    # Record 1 (Cycle 1)
    raw_events.extend([
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-invoiceId", "Invoice ID", "INV-1001", 100, 200),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-invoiceId", "Invoice ID", "INV-1001", 500, 200),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-amount", "Amount", "$5,000.00", 100, 250),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-amount", "Amount", "$5,000.00", 500, 250),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-vendor", "Vendor", "Acme Corp", 100, 300),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-vendor", "Vendor", "Acme Corp", 500, 300),
        build_raw_telemetry_event(EventType.CLICK, "Target ERP", "#btn-next-record", "Next Record", "Next Record", 600, 400),
    ])

    # Record 2 (Cycle 2)
    raw_events.extend([
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-invoiceId", "Invoice ID", "INV-1002", 100, 200),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-invoiceId", "Invoice ID", "INV-1002", 500, 200),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-amount", "Amount", "$12,500.00", 100, 250),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-amount", "Amount", "$12,500.00", 500, 250),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-vendor", "Vendor", "Global Tech", 100, 300),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-vendor", "Vendor", "Global Tech", 500, 300),
        build_raw_telemetry_event(EventType.CLICK, "Target ERP", "#btn-next-record", "Next Record", "Next Record", 600, 400),
    ])

    # Record 3 (Cycle 3)
    raw_events.extend([
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-invoiceId", "Invoice ID", "INV-1003", 100, 200),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-invoiceId", "Invoice ID", "INV-1003", 500, 200),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-amount", "Amount", "$3,200.00", 100, 250),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-amount", "Amount", "$3,200.00", 500, 250),
        build_raw_telemetry_event(EventType.COPY, "Notes App", "#source-vendor", "Vendor", "Nexus Ltd", 100, 300),
        build_raw_telemetry_event(EventType.PASTE, "Target ERP", "#target-vendor", "Vendor", "Nexus Ltd", 500, 300),
        build_raw_telemetry_event(EventType.CLICK, "Target ERP", "#btn-next-record", "Next Record", "Next Record", 600, 400),
    ])

    print(f"\n[1] Captured Raw Telemetry Events: {len(raw_events)}")

    # 2. Semantic Normalization & Transfer Construction
    tb = TransferBuilder()
    transfers = tb.process_telemetry_events(raw_events)
    print(f"[2] Constructed Semantic Transfers: {len(transfers)}")
    for t in transfers:
        print(f"    - Transfer ID={t.transfer_id} | {t.source_display_label} -> {t.destination_display_label} | Val='{t.pasted_value}'")

    # 3. Cycle Segmentation
    obs_events = [
        ObservationEvent(
            event_id=e.event_id,
            session_id="sess-phase21",
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
    cycle_count = discovery_engine.get_completed_cycle_count()
    print(f"\n[3] Cycle Segmentation Decision: {cycle_count} Completed Cycles Identified")

    # 4. Outlier Detection
    dd = DeviationDetector()
    deviations = dd.detect_deviations(transfers)
    print(f"[4] Outlier Detection: {len(deviations)} Outliers Flagged")

    # 5. Parameterized Workflow DNA Generation
    cand = candidates[0] if candidates else WorkflowCandidate(
        candidate_id="cand-phase21",
        name="Dynamic Process Workflow",
        sequence=raw_events,
        repetition_count=cycle_count,
        confidence_score=1.00
    )
    transformer = DNATransformer()
    dna = transformer.transform_candidate(cand)
    print(f"\n[5] Parameterized Workflow DNA Generated: {dna.name.encode('ascii', 'ignore').decode()}")
    field_mappings = dna.metadata.get("field_mappings", [])
    for m in field_mappings:
        print(f"    - Variable: {m['variable_name']} | Source: {m['source_app']} ({m['source_label']}) -> Target: {m['destination_app']} ({m['destination_label']})")

    # 6. ReplayFrame Trajectory Extraction
    extractor = TrajectoryExtractor()
    frames = extractor.extract_trajectory(raw_events)
    print(f"\n[6] ReplayFrame Trajectory Frames Extracted: {len(frames)}")

    # Assertions
    assert len(raw_events) == 21, f"Expected 21 raw events, got {len(raw_events)}"
    assert len(transfers) == 9, f"Expected 9 semantic transfers across 3 records, got {len(transfers)}"
    assert cycle_count == 3, f"Expected 3 completed cycles, got {cycle_count}"
    assert len(deviations) == 0, f"Expected 0 deviations for valid training, got {len(deviations)}"
    assert len(field_mappings) == 3, f"Expected 3 parameterized field mappings, got {len(field_mappings)}"
    assert field_mappings[0]["variable_name"] == "current_record.field_1"
    assert field_mappings[1]["variable_name"] == "current_record.field_2"
    assert field_mappings[2]["variable_name"] == "current_record.field_3"

    print("\n" + "=" * 70)
    print("ALL PHASE 21 ACCEPTANCE TEST ASSERTIONS PASSED SUCCESSFULLY")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_phase21_acceptance_test()
