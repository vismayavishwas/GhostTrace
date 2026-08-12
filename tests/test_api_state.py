import pytest

@pytest.mark.asyncio
async def test_get_current_state_default(async_client):
    """Test getting current graph state when idle."""
    res = await async_client.get("/api/v1/state")
    assert res.status_code == 200
    data = res.json()
    assert "confidence_score" in data
    assert "repetition_count" in data
    assert "workflow_domain" in data
    assert data["workflow_domain"] in ["FINANCE", "HR", "SALES"]

@pytest.mark.asyncio
async def test_state_domain_inference_hr(async_client):
    """Test state endpoint correctly infers HR domain from telemetry events."""
    hr_event = {
        "event_type": "PASTE",
        "active_tab": "WORKDAY ATS PORTAL",
        "url": "http://localhost:3000/demo",
        "target_selector": "#target-name",
        "element_tag": "INPUT",
        "field_label": "Candidate Name",
        "input_value": "Elena Rostova",
        "app_title": "WORKDAY ATS PORTAL",
        "cycle_id": "cycle-1",
        "domain": "HR",
        "workflow_domain": "HR",
        "metadata": {
            "domain": "HR",
            "workflow_domain": "HR",
            "app_title": "WORKDAY ATS PORTAL"
        }
    }
    await async_client.post("/api/v1/telemetry/events", json=hr_event)

    state_res = await async_client.get("/api/v1/state")
    assert state_res.status_code == 200
    data = state_res.json()
    assert data["workflow_domain"] == "HR"
    assert "HR" in data["candidate_name"] or "Candidate" in data["candidate_name"]

@pytest.mark.asyncio
async def test_state_refine_endpoint(async_client):
    """Test /api/v1/state/refine endpoint."""
    payload = {
        "choice": "EXCLUDE",
        "target_selector": "#source-amount"
    }
    res = await async_client.post("/api/v1/state/refine", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["action"] == "EXCLUDE"
