import pytest
from app.agents.business_process.business_agent import BusinessProcessAgent, _DOMAIN_DEFAULTS

def test_business_process_agent_domain_defaults():
    """Verify BusinessProcessAgent domain-specific fallback metadata."""
    agent = BusinessProcessAgent()

    for domain in ["FINANCE", "HR", "SALES"]:
        meta = agent.analyze_process(
            candidate_name="Test Workflow",
            steps=["COPY on #source-f1", "PASTE on #target-f1"],
            source_app="Source",
            target_app="Target",
            repetition_count=3,
            workflow_domain=domain
        )
        assert meta.repeatability == "3 observations"
        assert meta.automation_readiness == "High"
        assert meta.workflow_name is not None

        expected_name = _DOMAIN_DEFAULTS[domain]["workflow_name"]
        assert meta.workflow_name == expected_name

def test_business_process_agent_budget_per_domain():
    """Verify Gemini call budget is isolated per domain."""
    agent = BusinessProcessAgent()

    # Call for FINANCE
    meta_fin = agent.analyze_process(
        candidate_name="Test",
        steps=["Step 1"],
        source_app="PDF",
        target_app="SAP",
        workflow_domain="FINANCE"
    )
    assert meta_fin.department == "Finance & Accounting"

    # Call for HR with same step count
    meta_hr = agent.analyze_process(
        candidate_name="Test",
        steps=["Step 1"],
        source_app="Resume",
        target_app="Workday",
        workflow_domain="HR"
    )
    assert meta_hr.department == "Human Resources"
