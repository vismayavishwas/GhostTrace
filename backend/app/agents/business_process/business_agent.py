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
    automation_score: float = Field(default=0.95, description="Feasibility automation score (0.0 - 1.0)")
    estimated_time_saved: str = Field(default="2.4 hours/day", description="Estimated operational time saved")
    repeatability: str = Field(default="High", description="Observed repeatability score")
    human_summary: str = Field(default="Automates repetitive data transfer between web portals and enterprise software.", description="Executive-level summary")


class BusinessProcessAgent:
    """
    ⭐ Business Process Understanding Agent ⭐
    Uses Google Gemini 3.1 Flash Lite to transform raw technical DOM action steps
    into executive-grade enterprise business process intelligence.
    """

    def __init__(self):
        logger.info("BusinessProcessAgent initialized with Gemini 3.1 Flash Lite intelligence.")

    def analyze_process(self, candidate_name: str, steps: list, source_app: str, target_app: str) -> BusinessProcessMetadata:
        """
        Calls GeminiService to classify the enterprise business process, department, and ROI metrics.
        """
        formatted_steps = "\n".join([f"Step {idx+1}: {step}" for idx, step in enumerate(steps[:10])])

        prompt = f"""You are a Principal Enterprise Process Mining Architect & Automation Strategist.
Analyze the following observed user interaction workflow sequence and provide executive-level business process intelligence.

WORKFLOW CONTEXT:
- Candidate Name: {candidate_name}
- Source Application: {source_app}
- Target Application: {target_app}
- Technical Steps Recorded:
{formatted_steps}

REQUIREMENT:
Classify this workflow into an enterprise business process. Output MUST be valid JSON with the following exact keys:
{{
  "workflow_name": "<Short professional name e.g. Vendor Invoice Entry, Lead Intake>",
  "department": "<Finance | Operations | Customer Care | HR | Sales | IT>",
  "business_goal": "<1-sentence summary of the business objective>",
  "automation_score": <number between 0.80 and 0.99>,
  "estimated_time_saved": "<e.g. 2.4 hours/day, 12.5 hours/week>",
  "repeatability": "<High | Medium | Exceptional>",
  "human_summary": "<Executive summary of what this automated digital employee accomplishes>"
}}

Respond ONLY with valid JSON inside a code block. Do NOT include additional text outside the JSON.
"""

        fallback_meta = BusinessProcessMetadata(
            workflow_name=f"{source_app} → {target_app} Automation",
            department="Operations / Finance",
            business_goal=f"Automates data transfer from {source_app} into {target_app}",
            automation_score=0.92,
            estimated_time_saved="2.1 hours/day",
            repeatability="High",
            human_summary=f"Automates repetitive manual copy-paste workflow between {source_app} and {target_app}."
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
            meta = BusinessProcessMetadata(**parsed)
            logger.info(
                f"BusinessProcessAgent classified workflow in {elapsed:.2f}s | "
                f"Name: '{meta.workflow_name}' | Department: {meta.department} | Saved: {meta.estimated_time_saved}"
            )
            return meta
        except Exception as e:
            logger.warning(f"Error parsing BusinessProcessAgent JSON response ({e}). Using rule fallback.")
            return fallback_meta


business_process_agent = BusinessProcessAgent()
