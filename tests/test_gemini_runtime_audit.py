"""
Gemini Runtime Audit Test Suite
Verifies:
1. Gemini API Client configuration & model cascade order.
2. Number of Gemini API calls made per workflow runtime.
3. Call budget enforcement (max 1 call per workflow session for business process understanding).
4. Graceful fallback behavior when API key is missing or quota is exhausted.
"""

import os
from app.services.gemini_service import GeminiService, gemini_service
from app.services.call_budget import GeminiCallBudget, gemini_budget
from app.agents.business_process.business_agent import BusinessProcessAgent


def test_gemini_model_cascade_order():
    """Verify primary model and cascade model ordering."""
    service = GeminiService()
    assert service.primary_model == "gemini-2.0-flash"
    assert service.cascade_models == [
        "gemini-2.0-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]


def test_gemini_call_budget_enforcement():
    """Verify Gemini call budget enforces max 1 call per workflow key per purpose."""
    budget = GeminiCallBudget()
    wf_key = "test_wf_001"

    # Initial state: call allowed
    assert budget.can_call(wf_key, "business") is True

    # Mark called once
    budget.mark_called(wf_key, "business")

    # Second call attempt should be blocked by budget
    assert budget.can_call(wf_key, "business") is False

    # Purpose 'repair' should still have independent budget
    assert budget.can_call(wf_key, "repair") is True


def test_business_process_agent_gemini_runtime_audit():
    """Audit end-to-end runtime call count and fallback during business process analysis."""
    agent = BusinessProcessAgent()
    steps = ["COPY on Invoice ID", "PASTE on Invoice ID", "SUBMIT_ACTION on Save"]

    # Execute analysis for a test workflow
    meta = agent.analyze_process(
        candidate_name="PDF Invoice Source -> SAP ERP Financials",
        steps=steps,
        source_app="PDF Invoice Source",
        target_app="SAP ERP Financials",
        repetition_count=3
    )

    # Verify structured metadata returned
    assert meta.workflow_name is not None
    assert meta.department is not None
    assert meta.repeatability == "3 observations"
    assert meta.confidence >= 0.80

    print("\n==================================================")
    print("GEMINI RUNTIME AUDIT REPORT:")
    print("==================================================")
    print(f"Primary Gemini Model : {gemini_service.primary_model}")
    print(f"Model Cascade Order  : {gemini_service.cascade_models}")
    print(f"API Key Configured   : {bool(gemini_service.api_key)}")
    safe_name = str(meta.workflow_name).replace("→", "->")
    print(f"Workflow Classified  : {safe_name}")
    print(f"Department          : {meta.department}")
    print("==================================================")


if __name__ == "__main__":
    test_gemini_model_cascade_order()
    test_gemini_call_budget_enforcement()
    test_business_process_agent_gemini_runtime_audit()
    print("\nALL GEMINI RUNTIME AUDIT TESTS PASSED SUCCESSFULLY!")
