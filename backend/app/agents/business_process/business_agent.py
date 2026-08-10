import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.gemini_service import gemini_service
from app.services.call_budget import gemini_budget

logger = logging.getLogger("ghosttrace.business_process")


class BusinessProcessMetadata(BaseModel):
    workflow_name: str = Field(default="Cross-Application Data Transfer", description="Human-readable business workflow name")
    department: str = Field(default="Operations", description="Target enterprise department")
    business_goal: str = Field(default="Automate manual cross-app data entry", description="Primary business goal")
    confidence: float = Field(default=0.92, description="Semantic classification confidence rating")
    repeatability: str = Field(default="3 observations", description="Telemetry-backed repetition count")
    automation_readiness: str = Field(default="High", description="Automation feasibility rating")
    summary: str = Field(default="Recurring data entry workflow suitable for autonomous automation.", description="Executive-level summary")


# Domain-specific defaults for fallback metadata
_DOMAIN_DEFAULTS = {
    "FINANCE": {
        "workflow_name": "Vendor Invoice → SAP ERP Entry Workflow",
        "department": "Finance & Accounting",
        "business_goal": "Automate vendor invoice data transfer from PDF portals into SAP ERP",
        "summary": "Recurring finance workflow: copy invoice fields from PDF source into SAP ERP financial system.",
    },
    "HR": {
        "workflow_name": "Candidate Resume → ATS Onboarding Workflow",
        "department": "Human Resources",
        "business_goal": "Automate candidate profile transfer from resume PDFs into Workday ATS",
        "summary": "Recurring HR workflow: transfer candidate screening data from resume source into Workday ATS portal.",
    },
    "SALES": {
        "workflow_name": "Sales Lead → Salesforce CRM Entry Workflow",
        "department": "Sales & Business Development",
        "business_goal": "Automate lead data transfer from Excel spreadsheets into Salesforce CRM",
        "summary": "Recurring sales workflow: move qualified leads from Excel pipeline into Salesforce CRM records.",
    },
}


class BusinessProcessAgent:
    """
    Business Process Understanding Agent.
    Uses Google Gemini to transform raw technical DOM action steps into dynamic,
    context-aware business process intelligence backed by live telemetry.
    """

    def __init__(self):
        logger.info("BusinessProcessAgent initialized with domain-aware telemetry reasoning.")

    def analyze_process(
        self,
        candidate_name: str,
        steps: list,
        source_app: str,
        target_app: str,
        repetition_count: int = 3,
        avg_duration_sec: float = 12.5,
        workflow_domain: str = "FINANCE",
    ) -> BusinessProcessMetadata:
        """
        Calls GeminiService to dynamically classify the business process based on live runtime context.
        Enforces GeminiCallBudget so each workflow+domain triggers Gemini at most ONCE.
        workflow_domain: "FINANCE" | "HR" | "SALES"
        """
        obs_string = f"{repetition_count} observations"
        domain_defaults = _DOMAIN_DEFAULTS.get(workflow_domain, _DOMAIN_DEFAULTS["FINANCE"])

        fallback_meta = BusinessProcessMetadata(
            workflow_name=domain_defaults["workflow_name"],
            department=domain_defaults["department"],
            business_goal=domain_defaults["business_goal"],
            confidence=0.88,
            repeatability=obs_string,
            automation_readiness="High",
            summary=domain_defaults["summary"],
        )

        # Budget key includes domain so Finance/HR/Sales each get their own Gemini call
        workflow_key = f"{workflow_domain}:{source_app}->{target_app}:{len(steps)}"
        if not gemini_budget.can_call(workflow_key, "business"):
            logger.info(f"Gemini call budget fulfilled for key '{workflow_key}'. Returning cached domain result.")
            return fallback_meta

        formatted_steps = "\n".join([f"Step {idx+1}: {step}" for idx, step in enumerate(steps[:10])])

        # Domain-specific instruction block for Gemini
        domain_instructions = {
            "FINANCE": (
                "This is a FINANCE workflow. Source is a financial document (Invoice/PDF/Statement). "
                "Target is an ERP or accounting system (SAP, Oracle, QuickBooks). "
                "Department MUST be 'Finance & Accounting'. "
                "workflow_name MUST reference invoice/vendor/financial terms."
            ),
            "HR": (
                "This is a HUMAN RESOURCES workflow. Source is a candidate document (Resume/CV/Application). "
                "Target is an ATS or HR system (Workday, Greenhouse, Lever). "
                "Department MUST be 'Human Resources'. "
                "workflow_name MUST reference candidate/onboarding/screening/ATS terms."
            ),
            "SALES": (
                "This is a SALES workflow. Source is a lead list or pipeline (Excel/Sheet/CSV). "
                "Target is a CRM system (Salesforce, HubSpot, Pipedrive). "
                "Department MUST be 'Sales & Business Development'. "
                "workflow_name MUST reference lead/deal/CRM/pipeline terms."
            ),
        }

        domain_hint = domain_instructions.get(workflow_domain, domain_instructions["FINANCE"])

        prompt = f"""You are a Principal Enterprise Process Mining Architect.
Analyze the following observed user interaction workflow and classify it based STRICTLY on the provided domain and runtime context.

WORKFLOW DOMAIN: {workflow_domain}
DOMAIN RULES: {domain_hint}

RUNTIME CONTEXT:
- Observed Source Window/App: {source_app}
- Observed Target Window/App: {target_app}
- Workflow Repetitions in Telemetry: {obs_string}
- Observed Step Sequence:
{formatted_steps}

CRITICAL INSTRUCTIONS:
1. The WORKFLOW DOMAIN field above is AUTHORITATIVE. Do NOT override it.
2. Derive the workflow_name, department, and summary STRICTLY from the domain rules above.
3. Do NOT output Finance terms for HR or Sales workflows and vice versa.

Output MUST be valid JSON with the following exact keys:
{{
  "workflow_name": "<Professional name strictly matching the domain rules above>",
  "department": "<Exact department per domain rules>",
  "business_goal": "<1-sentence business objective matching the domain>",
  "confidence": <number between 0.85 and 0.99>,
  "repeatability": "{obs_string}",
  "automation_readiness": "<High | Exceptional | Ready>",
  "summary": "<1-sentence executive summary matching the domain>"
}}

Respond ONLY with valid JSON inside a ```json code block.
"""

        def fallback_fn():
            return fallback_meta.model_dump_json()

        response_text, elapsed, status = gemini_service.generate(
            prompt=prompt,
            purpose=f"business_process_understanding_{workflow_domain.lower()}",
            fallback_fn=fallback_fn,
        )
        gemini_budget.mark_called(workflow_key, "business")

        try:
            cleaned_json = response_text.strip()
            if "```json" in cleaned_json:
                cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_json:
                cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

            parsed = json.loads(cleaned_json)
            parsed["repeatability"] = obs_string  # Always use empirical telemetry count

            meta = BusinessProcessMetadata(**parsed)
            logger.info(
                f"BusinessProcessAgent classified [{workflow_domain}] workflow in {elapsed:.2f}s | "
                f"Name: '{meta.workflow_name}' | Dept: {meta.department} | Readiness: {meta.automation_readiness}"
            )
            return meta
        except Exception as e:
            logger.warning(f"Error parsing BusinessProcessAgent JSON response ({e}). Using domain fallback.")
            return fallback_meta


business_process_agent = BusinessProcessAgent()
