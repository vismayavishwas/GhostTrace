"""
GhostTrace AI Full End-to-End Workflow Pipeline Integration Test
Verifies complete pipeline lifecycle:
1. Ingesting raw telemetry events across 3 execution cycles.
2. Segmenting sequence cycles & discovering candidate pattern.
3. Detecting deviations and protecting canonical approved workflow steps.
4. Generating 1-cycle Workflow DNA.
5. Extracting ReplayFrame trajectory frames for autonomous execution.
"""

from app.models.telemetry import TelemetryEvent
from app.agents.telemetry.transfer_builder import TransferBuilder
from app.agents.continuous_observer.workflow_discovery import WorkflowDiscoveryEngine
from app.agents.pattern_discovery.deviation_detector import global_deviation_detector
from app.agents.workflow_dna.dna_transformer import DNATransformer
from app.agents.ghost_replay.path_extractor import TrajectoryExtractor


def run_e2e_workflow_pipeline_test():
    # 1. Simulate 3 cycles of raw telemetry events (Invoice ID, Amount, Vendor)
    events = []
    t = 1000.0

    def add_copy_paste(src_sel: str, src_lbl: str, dest_sel: str, dest_lbl: str, val: str, cycle: int):
        nonlocal t
        events.append(TelemetryEvent(
            event_id=f"c{cycle}-copy-{src_sel}",
            event_type="COPY",
            active_tab="Notes App",
            target_selector=f"#{src_sel}",
            input_masked=val,
            coordinates_x=100.0,
            coordinates_y=150.0,
            timestamp=t
        ))
        t += 100.0
        events.append(TelemetryEvent(
            event_id=f"c{cycle}-paste-{dest_sel}",
            event_type="PASTE",
            active_tab="Target ERP",
            target_selector=f"#{dest_sel}",
            input_masked=val,
            coordinates_x=500.0,
            coordinates_y=200.0,
            timestamp=t
        ))
        t += 100.0

    # Cycle 1
    add_copy_paste("inv_id", "Invoice ID", "target_inv", "Invoice ID", "INV-9001", 1)
    add_copy_paste("amt", "Amount", "target_amt", "Amount", "$1,500.00", 1)
    add_copy_paste("vnd", "Vendor", "target_vnd", "Vendor", "Acme Supply", 1)
    events.append(TelemetryEvent(event_id="c1-sub", event_type="SUBMIT", target_selector="#btn-submit", timestamp=t))
    t += 200.0

    # Cycle 2
    add_copy_paste("inv_id", "Invoice ID", "target_inv", "Invoice ID", "INV-9002", 2)
    add_copy_paste("amt", "Amount", "target_amt", "Amount", "$4,200.00", 2)
    add_copy_paste("vnd", "Vendor", "target_vnd", "Vendor", "Global Logistics", 2)
    events.append(TelemetryEvent(event_id="c2-sub", event_type="SUBMIT", target_selector="#btn-submit", timestamp=t))
    t += 200.0

    # Cycle 3 (Contains 1 mistake transfer: Amount -> Vendor)
    add_copy_paste("inv_id", "Invoice ID", "target_inv", "Invoice ID", "INV-9003", 3)
    add_copy_paste("amt", "Amount", "target_vnd", "Vendor", "$4,200.00", 3)  # <-- MISTAKE
    add_copy_paste("amt", "Amount", "target_amt", "Amount", "$4,200.00", 3)
    add_copy_paste("vnd", "Vendor", "target_vnd", "Vendor", "Nexus Corp", 3)
    events.append(TelemetryEvent(event_id="c3-sub", event_type="SUBMIT", target_selector="#btn-submit", timestamp=t))

    # 2. Transfer Construction
    tb = TransferBuilder()
    transfers = tb.process_telemetry_events(events)
    assert len(transfers) >= 9, f"Expected at least 9 transfers, got {len(transfers)}"

    # 3. Discovery Engine
    discovery = WorkflowDiscoveryEngine()
    from app.agents.continuous_observer.models import ObservationEvent
    obs_events = [ObservationEvent(telemetry_event=e, noise_classification="RELEVANT") for e in events]
    candidates = discovery.analyze_observations(obs_events)
    assert len(candidates) >= 1

    cand = candidates[0]
    assert getattr(cand, "repetition_count", cand.occurrence_count) >= 2

    # 4. Deviation Detection
    devs = global_deviation_detector.detect_deviations(transfers, return_all=True)
    assert len(devs) >= 1, f"Expected at least 1 deviation, got {len(devs)}"
    print("DETECTED DEVIATIONS:", devs)

    # 5. Workflow DNA Generation
    transformer = DNATransformer()
    dna = transformer.transform_candidate(cand)
    field_mappings = dna.metadata.get("field_mappings", [])
    assert len(field_mappings) == 3, f"Expected 3 canonical steps, got {len(field_mappings)}"

    # 6. Ghost Replay Trajectory Frames
    extractor = TrajectoryExtractor()
    frames = extractor.extract_trajectory(events)
    assert len(frames) == len(events)

    print("\n==================================================")
    print("FULL E2E PIPELINE INTEGRATION TEST REPORT:")
    print("==================================================")
    print(f"Raw Events Processed   : {len(events)}")
    print(f"Semantic Transfers     : {len(transfers)}")
    rep_cnt = getattr(cand, "repetition_count", cand.occurrence_count)
    print(f"Discovered Cycles      : {rep_cnt}")
    print(f"Deviations Excluded    : {len(devs)} ({devs[0]['label']})")
    print(f"Canonical DNA Steps    : {len(field_mappings)}")
    print(f"Trajectory Frames      : {len(frames)}")
    print("==================================================")
    print("ALL E2E WORKFLOW PIPELINE ASSERTIONS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_e2e_workflow_pipeline_test()
