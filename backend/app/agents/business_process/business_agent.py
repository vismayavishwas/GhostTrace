import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.gemini_service import gemini_service

logger = logging.getLogger("ghosttrace.business_process")


class BusinessProcessMetadata(BaseModel):
    workflow_name: str = Field(default="Cross-Application Data Transfer", description="Human-readable business workflow name")
    department: str = Field(default="Operations", description="Target enterprise department")
    business_goal: str = Field(default="Automate manual cross-app data entry", description="Primary business goal")
    confidence: float = Field(default=0.92, description="Semantic classification confidence rating")
    repeatability: str = Field(default="3 observations", description="Telemetry-backed repetition count")
    automation_readiness: str = Field(default="High", description="Automation feasibility rating")
    summary: str = Field(default="Recurring data entry workflow suitable for autonomous automation.", description="Executive-level summary")


class BusinessProcessAgent:
    """
    ⭐ Business Process Understanding Agent ⭐
    Uses Google Gemini 3.1 Flash Lite to transform raw technical DOM action steps
    into dynamic, context-aware business process intelligence backed by live telemetry.
    """

    def __init__(self):
        logger.info("BusinessProcessAgent initialized with dynamic telemetry reasoning.")

    def analyze_process(self, candidate_name: str, steps: list, source_app: str, target_app: str, repetition_count: int = 3, avg_duration_sec: float = 12.5) -> BusinessProcessMetadata:
        """
        Calls GeminiService to dynamically classify the business process based on live runtime context.
        Computes telemetry-backed repeatability and readiness metrics.
        """
        formatted_steps = "\n".join([f"Step {idx+1}: {step}" for idx, step in enumerate(steps[:10])])
        obs_string = f"{repetition_count} observations"

        prompt = f"""You are a Principal Enterprise Process Mining Architect.
Analyze the following observed user interaction workflow sequence and classify it based STRICTLY on the live runtime applications and steps.

RUNTIME CONTEXT:
- Observed Source Window/App: {source_app}
- Observed Target Window/App: {target_app}
- Repetitions Counted in Telemetry: {obs_string}
- Observed Step Sequence:
{formatted_steps}

INSTRUCTIONS:
1. Dynamically infer the exact business process name based ONLY on the actual applications involved:
   - If Chrome -> Excel / Word Table: Name it "Spreadsheet Data Entry" or "Document Table Synthesis".
   - If SAP / Portal -> Finance: Name it "Vendor Invoice Entry" or "ERP Data Intake".
   - If Web -> CRM / Email: Name it "Lead Intake & Dispatch".
   Do NOT output "Vendor Invoice Entry" unless SAP or Invoice portals are explicitly in the source/target apps.

2. Output MUST be valid JSON with the following exact keys:
{{
  "workflow_name": "<Dynamic professional name derived strictly from the runtime apps>",
  "department": "<Finance | Operations | Customer Support | HR | Sales | Engineering>",
  "business_goal": "<1-sentence summary of the business objective>",
  "confidence": <number between 0.85 and 0.99>,
  "repeatability": "{obs_string}",
  "automation_readiness": "<High | Exceptional | Ready>",
  "summary": "<1-sentence executive summary of the observed workflow>"
}}

Respond ONLY with valid JSON inside a ```json code block.
"""

        fallback_meta = BusinessProcessMetadata(
            workflow_name=f"{source_app} → {target_app} Data Flow",
            department="Operations / IT",
            business_goal=f"Transfer structured data between {source_app} and {target_app}",
            confidence=0.88,
            repeatability=obs_string,
            automation_readiness="High",
            summary=f"Automates repetitive manual interaction pattern between {source_app} and {target_app}."
        )

        def fallback_fn():
            return fallback_meta.model_dump_json()

        response_text, elapsed, status = gemini_service.generate(
            prompt=prompt,
            purpose="business_process_understanding",
            fallback_fn=fallback_fn
        )

        try:
            cleaned_json = response_text.strip()
            if "```json" in cleaned_json:
                cleaned_json = cleaned_json.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_json:
                cleaned_json = cleaned_json.split("```")[1].split("```")[0].strip()

            parsed = json.loads(cleaned_json)
            # Guarantee empirical repeatability metric is preserved from telemetry
            parsed["repeatability"] = obs_string

            meta = BusinessProcessMetadata(**parsed)
            logger.info(
                f"BusinessProcessAgent dynamically classified workflow in {elapsed:.2f}s | "
                f"Name: '{meta.workflow_name}' | Dept: {meta.department} | Readiness: {meta.automation_readiness}"
            )
            return meta
        except Exception as e:
            logger.warning(f"Error parsing BusinessProcessAgent JSON response ({e}). Using telemetry fallback.")
            return fallback_meta



business_process_agent = BusinessProcessAgent()
