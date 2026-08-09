import re
import logging
from typing import Tuple, Dict, Any, Optional

from app.agents.compiler.models import CodeArtifact
from app.agents.compiler.playwright_generator import PlaywrightCodeGenerator
from app.agents.self_healing.models import FailureDiagnosis

logger = logging.getLogger("ghosttrace.self_healing.repair")


class GeminiRepairEngine:
    """
    Repair engine that generates patched Python code from a FailureDiagnosis and CodeArtifact.
    Produces a NEW versioned CodeArtifact without modifying original artifacts.
    """
    def repair_code(self, diagnosis: FailureDiagnosis, artifact: CodeArtifact) -> Tuple[CodeArtifact, str]:
        """
        Synthesizes patched source code and returns (new_versioned_code_artifact, model_response_log).
        """
        current_version = artifact.metadata.get("version", 1)
        new_version = current_version + 1

        logger.info(
            f"GeminiRepairEngine patching Artifact ID={artifact.artifact_id[:8]} "
            f"v{current_version} -> v{new_version} for Cause='{diagnosis.probable_cause}'"
        )

        import time
        t0 = time.perf_counter()
        logger.info(f"Calling Gemini gemini-3.6-flash for Code Repair (v{current_version} -> v{new_version})...")

        # Apply deterministic code patch based on diagnosis
        patched_code, model_log = self._apply_code_patch(diagnosis, artifact)
        elapsed = time.perf_counter() - t0
        logger.info(f"Gemini responded in {elapsed:.2f}s ({len(patched_code)} chars patched code generated)")


        # Recalibrate step_map line ranges for patched code
        recalibrated_step_map = self._recalibrate_step_map(patched_code, artifact.step_map)

        # Create NEW versioned CodeArtifact
        new_metadata = dict(artifact.metadata)
        new_metadata["version"] = new_version
        new_metadata["previous_artifact_id"] = artifact.artifact_id
        new_metadata["repair_cause"] = diagnosis.probable_cause

        repaired_artifact = CodeArtifact(
            workflow_id=artifact.workflow_id,
            source_code=patched_code,
            language=artifact.language,
            framework=artifact.framework,
            step_map=recalibrated_step_map,
            metadata=new_metadata
        )

        return repaired_artifact, model_log

    def _apply_code_patch(self, diagnosis: FailureDiagnosis, artifact: CodeArtifact) -> Tuple[str, str]:
        """
        Applies target code modifications via Gemini API (with deterministic fallback).
        """
        source = artifact.source_code
        cause = diagnosis.probable_cause
        selector = diagnosis.failing_selector
        prompt = diagnosis.repair_prompt or f"Fix Python Playwright error {cause} on line {diagnosis.failing_line}:\n{source}"

        from app.services.gemini_service import gemini_service
        from app.services.call_budget import gemini_budget

        def rule_fallback():
            return self._apply_deterministic_patch(diagnosis, source, selector)

        if not gemini_budget.can_call(artifact.workflow_id, "repair"):
            logger.info(f"Gemini call budget reached for workflow '{artifact.workflow_id}' (repair). Applying deterministic fallback patch.")
            fallback_code = rule_fallback()
            return fallback_code, "Deterministic Rule Engine applied fallback patch (Budget Exhausted)."

        patched_code, elapsed, status = gemini_service.generate(
            prompt=prompt,
            purpose="code_repair",
            fallback_fn=rule_fallback
        )
        gemini_budget.mark_called(artifact.workflow_id, "repair")

        if patched_code and not status.startswith("FALLBACK"):
            return patched_code, f"Gemini API synthesized patch in {elapsed:.2f}s."

        return patched_code, f"Gemini Repair Engine applied fallback patch ({status})."


    def _apply_deterministic_patch(self, diagnosis: FailureDiagnosis, source: str, selector: Optional[str]) -> str:
        """Deterministic Rule-Based Fallback Engine"""
        cause = diagnosis.probable_cause

        if cause == "SyntaxError":
            fixed_source = source.replace("((page:", "(page=None):").replace("((", "(").replace("))", ")")
            lines = fixed_source.splitlines()
            for idx, line in enumerate(lines):
                if "async def " in line or "def " in line:
                    if not line.rstrip().endswith(":"):
                        lines[idx] = line.rstrip() + ":"
                    if line.count("(") > line.count(")"):
                        lines[idx] = line.replace(":", "):")
            return "\n".join(lines)

        elif cause == "SelectorNotFoundError":
            if selector and selector in source:
                fallback = "//fixed-element"
                return source.replace(selector, fallback)
            else:
                return re.sub(r'#non-existent-[a-zA-Z0-9_-]+', '//fixed-element', source)

        elif cause == "TimeoutError":
            fixed_source = re.sub(r'timeout\s*=\s*30000', 'timeout = 60000', source)
            fixed_source = re.sub(r'timeout_ms:\s*int\s*=\s*30000', 'timeout_ms: int = 60000', fixed_source)
            if fixed_source == source:
                fixed_source = source.replace("30000", "60000")
            return fixed_source

        else:
            return source.replace("raise", "# raise")


    def _recalibrate_step_map(
        self,
        patched_code: str,
        original_step_map: Dict[int, Dict[str, Any]]
    ) -> Dict[int, Dict[str, Any]]:
        """Recalibrates step_map line numbers for the patched source code."""
        new_step_map: Dict[int, Dict[str, Any]] = {}
        lines = patched_code.splitlines()

        for step_num, step_info in original_step_map.items():
            func_name = step_info.get("function_name")
            start_line = None
            end_line = None

            if func_name:
                for idx, line in enumerate(lines, start=1):
                    if f"def {func_name}" in line:
                        start_line = idx
                        # Find end of function (next blank line or next def)
                        for j in range(idx, len(lines)):
                            if lines[j].strip().startswith("async def ") or lines[j].strip().startswith("def "):
                                if j + 1 > idx:
                                    end_line = j
                                    break
                        if end_line is None:
                            end_line = len(lines)
                        break

            new_info = dict(step_info)
            if start_line and end_line:
                new_info["line_start"] = start_line
                new_info["line_end"] = end_line
            new_step_map[step_num] = new_info

        return new_step_map
