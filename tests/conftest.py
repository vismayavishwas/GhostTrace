import sys
import os
from pathlib import Path

# Ensure backend root is on sys.path
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.routes.telemetry import in_memory_events, reset_telemetry_state

@pytest_asyncio.fixture
async def async_client():
    """Async HTTPX Test Client for FastAPI endpoint testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def reset_state_before_test():
    """Resets in-memory telemetry buffer and state before every test."""
    await reset_telemetry_state()
    in_memory_events.clear()
    yield

@pytest.fixture
def sample_telemetry_payload():
    """Fixture providing a standard Finance telemetry event payload."""
    return {
        "event_type": "PASTE",
        "active_tab": "SAP ERP FINANCIALS",
        "url": "http://localhost:3000/demo",
        "target_selector": "#target-invoiceId",
        "element_tag": "INPUT",
        "field_label": "Invoice ID",
        "input_value": "INV-2026-9841",
        "app_title": "SAP ERP FINANCIALS",
        "cycle_id": "cycle-1",
        "domain": "FINANCE",
        "workflow_domain": "FINANCE",
        "metadata": {
            "is_sandbox": True,
            "field_label": "Invoice ID",
            "app_title": "SAP ERP FINANCIALS",
            "cycle_id": "cycle-1",
            "domain": "FINANCE",
            "workflow_domain": "FINANCE"
        }
    }
