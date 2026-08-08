"""
10-Transfer Regression Test for Observation Synthesis.

Scenario:
  Cycle 1 (clean):  InvoiceID → InvoiceID, Amount → Amount, Vendor → Vendor
  Cycle 2 (1 mistake): InvoiceID → InvoiceID, Amount → VENDOR (wrong!), Vendor → Vendor
  Cycle 3 (1 mistake): InvoiceID → InvoiceID, Amount → Amount, Vendor → INVOICE_ID (wrong!)

Expected results:
  baseline_sequence = 3 steps (1-cycle template)
  total valid transfers = 9 (no immediate corrections)
  outlier_count = 2  (the 2 wrong-destination transfers)
  approved_workflow = 7  (9 - 2)
  canonical_steps (unique approved) = 3
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.telemetry.transfer_builder import SemanticTransfer
from app.agents.pattern_discovery.deviation_detector import DeviationDetector
from app.agents.pattern_discovery.deviation_detector import format_clean_entity_label

def make_xfer(src_entity, dest_entity, src_app="PDF Invoice Source", dest_app="SAP ERP Financials", idx=0):
    return SemanticTransfer(
        transfer_id=f"xfer-{idx}",
        source_entity=src_entity,
        source_app=src_app,
        destination_entity=dest_entity,
        destination_app=dest_app,
        pasted_value=f"val-{idx}",
        source_display_label=format_clean_entity_label("", src_entity),
        destination_display_label=format_clean_entity_label("", dest_entity),
    )

# Build 9 transfers simulating 3 cycles with 2 mistakes
transfers = [
    # Cycle 1 (clean baseline)
    make_xfer("invoice_id", "invoice_id", idx=1),
    make_xfer("amount", "amount", idx=2),
    make_xfer("vendor", "vendor", idx=3),
    # Cycle 2 (1 mistake: amount → vendor instead of amount → amount)
    make_xfer("invoice_id", "invoice_id", idx=4),
    make_xfer("amount", "vendor", idx=5),       # <-- WRONG DESTINATION
    make_xfer("vendor", "vendor", idx=6),
    # Cycle 3 (1 mistake: vendor → invoice_id instead of vendor → vendor)
    make_xfer("invoice_id", "invoice_id", idx=7),
    make_xfer("amount", "amount", idx=8),
    make_xfer("vendor", "invoice_id", idx=9),    # <-- WRONG DESTINATION
]

print("=" * 70)
print("10-TRANSFER REGRESSION TEST")
print("=" * 70)

detector = DeviationDetector()
deviations = detector.detect_deviations(transfers)

print(f"\n[1] Baseline sequence length: {len(detector.baseline_sequence)}")
assert len(detector.baseline_sequence) == 3, f"FAIL: Expected 3, got {len(detector.baseline_sequence)}"
print(f"    Baseline: {detector.baseline_sequence}")

print(f"\n[2] Total valid transfers: {len([x for x in transfers if not x.is_immediate_correction])}")

print(f"\n[3] Deviations detected: {len(deviations)}")
for d in deviations:
    print(f"    - {d['label']} | Reason: {d['reason']} | TID: {d['transfer_id']}")

assert len(deviations) == 2, f"FAIL: Expected 2 deviations, got {len(deviations)}"

# Build observation_synthesis like state.py does
field_mappings = []
for xfer in transfers:
    if xfer.is_immediate_correction:
        continue
    field_mappings.append({
        "transfer_id": xfer.transfer_id,
        "source_entity": xfer.source_entity,
        "source_label": xfer.source_display_label,
        "source_app": xfer.source_app,
        "destination_entity": xfer.destination_entity,
        "destination_label": xfer.destination_display_label,
        "destination_app": xfer.destination_app,
        "pasted_value": xfer.pasted_value or "",
    })

outlier_tids = {item.get("transfer_id") for item in deviations if item.get("transfer_id")}
approved_workflow = [m for m in field_mappings if m.get("transfer_id") not in outlier_tids]
excluded_outliers = [{**item, "status": "EXCLUDED_FROM_APPROVED_WORKFLOW"} for item in deviations]
outlier_count = len(excluded_outliers)

print(f"\n[4] outlier_count: {outlier_count}")
assert outlier_count == 2, f"FAIL: Expected outlier_count=2, got {outlier_count}"

print(f"\n[5] approved_workflow length: {len(approved_workflow)}")
assert len(approved_workflow) == 7, f"FAIL: Expected 7 approved, got {len(approved_workflow)}"

# Canonical dedup (like frontend does)
seen_keys = set()
canonical = []
for m in approved_workflow:
    key = f"{m['source_app']}::{m['source_label']}::{m['destination_app']}::{m['destination_label']}"
    if key not in seen_keys:
        seen_keys.add(key)
        canonical.append(m)

print(f"\n[6] Canonical 1-cycle LEARNED PATTERN steps: {len(canonical)}")
for c in canonical:
    print(f"    {c['source_label']} -> {c['destination_label']}")
assert len(canonical) == 3, f"FAIL: Expected 3 canonical steps, got {len(canonical)}"

print(f"\n[7] Excluded outliers detail:")
for o in excluded_outliers:
    print(f"    TID={o['transfer_id']} | {o['source_entity']} -> {o['observed_destination']} (expected: {o['expected_destination']}) | Status: {o['status']}")

print("\n" + "=" * 70)
print("ALL ASSERTIONS PASSED")
print("=" * 70)
