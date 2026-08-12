import pytest

@pytest.mark.asyncio
async def test_post_and_get_telemetry_events(async_client, sample_telemetry_payload):
    """Test telemetry ingestion (POST) and retrieval (GET)."""
    # 1. Ingest event
    res = await async_client.post("/api/v1/telemetry/events", json=sample_telemetry_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "event_id" in data

    # 2. Retrieve events
    get_res = await async_client.get("/api/v1/telemetry/events")
    assert get_res.status_code == 200
    events = get_res.json()
    assert len(events) >= 1
    first_evt = events[0]
    assert first_evt.get("event_type") == "PASTE" or first_evt.get("event_type") == "paste"

@pytest.mark.asyncio
async def test_reset_telemetry_state(async_client, sample_telemetry_payload):
    """Test telemetry buffer reset endpoint."""
    # Ingest event
    await async_client.post("/api/v1/telemetry/events", json=sample_telemetry_payload)

    # Post reset
    reset_res = await async_client.post("/api/v1/telemetry/reset")
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "SUCCESS"

    # Verify buffer is empty
    events_res = await async_client.get("/api/v1/telemetry/events")
    assert len(events_res.json()) == 0

@pytest.mark.asyncio
async def test_refine_workflow_candidate(async_client):
    """Test candidate refinement HITL endpoint."""
    refine_payload = {
        "choice": "EXCLUDE",
        "target_selector": "#target-amount"
    }
    res = await async_client.post("/api/v1/telemetry/candidates/cand-123/refine", json=refine_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["action"] == "EXCLUDE"
