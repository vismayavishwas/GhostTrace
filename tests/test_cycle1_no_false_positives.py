"""Test that Cycle 1 (no repeated source) produces ZERO false deviations."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.deviation_detector import DeviationDetector, format_clean_entity_label

def mk(s, d, i):
    return SemanticTransfer(
        transfer_id=f"x-{i}", source_entity=s, source_app="A",
        destination_entity=d, destination_app="B", pasted_value="v",
        source_display_label=format_clean_entity_label("", s),
        destination_display_label=format_clean_entity_label("", d),
    )

det = DeviationDetector()
# Cycle 1 only: 3 unique transfers, no repeated source
t = [mk("invoice_id", "invoice_id", 1), mk("amount", "amount", 2), mk("vendor", "vendor", 3)]
devs = det.detect_deviations(t)
print(f"Cycle1 deviations={len(devs)} baseline_len={len(det.baseline_sequence)}")
assert len(devs) == 0, f"FAIL: Cycle 1 should produce 0 deviations, got {len(devs)}"
assert len(det.baseline_sequence) == 0, "Baseline should NOT be set during Cycle 1 (no repeat)"
print("PASS: Cycle 1 produces 0 false deviations, baseline not set prematurely")
