import pytest
from app.models.telemetry import TelemetryEvent
from app.agents.telemetry.semantic_normalizer import SemanticNormalizer
from app.agents.telemetry.transfer_builder import TransferBuilder

def test_semantic_normalizer_copy_paste():
    """Test normalizing raw COPY and PASTE telemetry events."""
    copy_evt = TelemetryEvent(
        event_type="COPY",
        target_selector="#source-invoiceId",
        input_value="INV-2026-9841",
        field_label="Invoice ID",
        app_title="PDF INVOICE SOURCE"
    )
    norm_copy = SemanticNormalizer.normalize(copy_evt)
    assert norm_copy is not None
    assert norm_copy.operation == "COPY"
    assert norm_copy.pasted_value == "INV-2026-9841"

    paste_evt = TelemetryEvent(
        event_type="PASTE",
        target_selector="#target-invoiceId",
        input_value="INV-2026-9841",
        field_label="Invoice ID",
        app_title="SAP ERP FINANCIALS"
    )
    norm_paste = SemanticNormalizer.normalize(paste_evt)
    assert norm_paste is not None
    assert norm_paste.operation == "PASTE"

def test_transfer_builder_intent_window():
    """Test TransferBuilder aggregates COPY -> PASTE into a completed SemanticTransfer."""
    tb = TransferBuilder()

    events = [
        TelemetryEvent(
            event_type="COPY",
            target_selector="#source-invoiceId",
            input_value="INV-2026-9841",
            field_label="Invoice ID",
            app_title="PDF INVOICE SOURCE"
        ),
        TelemetryEvent(
            event_type="PASTE",
            target_selector="#target-invoiceId",
            input_value="INV-2026-9841",
            field_label="Invoice ID",
            app_title="SAP ERP FINANCIALS"
        )
    ]

    transfers = tb.process_telemetry_events(events)
    assert len(transfers) == 1
    xfer = transfers[0]
    assert xfer.source_app == "PDF INVOICE SOURCE"
    assert xfer.destination_app == "SAP ERP FINANCIALS"
    assert xfer.pasted_value == "INV-2026-9841"
    assert xfer.is_immediate_correction is False

def test_transfer_builder_immediate_correction():
    """Test TransferBuilder marks immediate user correction when pasting to wrong destination then right destination."""
    tb = TransferBuilder()

    events = [
        TelemetryEvent(
            event_type="COPY",
            target_selector="#source-invoiceId",
            input_value="INV-2026-9841",
            field_label="Invoice ID",
            app_title="PDF INVOICE SOURCE"
        ),
        # Wrong paste
        TelemetryEvent(
            event_type="PASTE",
            target_selector="#target-amount",
            input_value="INV-2026-9841",
            field_label="Amount",
            app_title="SAP ERP FINANCIALS"
        ),
        # Immediate corrected paste
        TelemetryEvent(
            event_type="PASTE",
            target_selector="#target-invoiceId",
            input_value="INV-2026-9841",
            field_label="Invoice ID",
            app_title="SAP ERP FINANCIALS"
        )
    ]

    transfers = tb.process_telemetry_events(events)
    assert len(transfers) >= 1
    # First transfer should be flagged as immediate correction
    first_xfer = transfers[0]
    assert first_xfer.is_immediate_correction is True
