import re
import logging
from typing import Optional, Dict, Any, Tuple
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult
from app.agents.self_healing.models import FailureDiagnosis

logger = logging.getLogger("ghosttrace.self_healing.diagnoser")


class FailureDiagnoser:
    """
    Analyzes failed SandboxResult instances against CodeArtifact step_map metadata.
    Isolates traceback parsing, line matching, and prompt construction into a structured FailureDiagnosis model.
    """
    def diagnose_failure(self, result: SandboxResult, artifact: CodeArtifact) -> FailureDiagnosis:
        """
        Diagnoses a sandbox failure and returns a structured FailureDiagnosis instance.
        """
        stderr = result.stderr or ""
        traceback_str = result.error_traceback or stderr
        
        # 1. Determine Failing Line Number
        failing_line = result.failing_line
        if failing_line is None:
            failing_line = self._extract_line_number(stderr)

        # 2. Match Line against CodeArtifact.step_map
        failing_step_num, failing_step_name, failing_selector = self._match_step(failing_line, artifact)
        if not failing_selector:
            # Fallback: extract selector directly from stderr regex
            sel_match = re.search(r"selector ['\"]([^'\"]+)['\"]", stderr, re.IGNORECASE)
            if sel_match:
                failing_selector = sel_match.group(1)


        # 3. Pre-Healing Verification: Distinguish Accidental User Mistake vs Genuine Target UI Failure
        from app.agents.pattern_discovery.correction_memory import global_correction_memory

        is_accidental_user_mistake = False
        if failing_selector:
            clean_sel = failing_selector.replace("#", "").replace(".", "")
            if global_correction_memory.is_known_accidental_correction("source_entity", clean_sel):
                is_accidental_user_mistake = True
                logger.info(f"Pre-Healing Verification: Isolated failure on '{failing_selector}' as an Accidental User Correction. Skipping UI script self-healing.")

        # 4. Categorize Probable Cause via GeminiService with deterministic traceback fallback
        from app.services.gemini_service import gemini_service

        diag_prompt = (
            f"Analyze this Python Playwright traceback and classify the primary error cause as one of: "
            f"SyntaxError, SelectorNotFoundError, TimeoutError, AssertionError, AccidentalUserMistake.\n\n"
            f"Traceback:\n{stderr[:1000]}"
        )
        def rule_fallback():
            return "AccidentalUserMistake" if is_accidental_user_mistake else self._categorize_cause(stderr)

        gemini_cause, elapsed, status = gemini_service.generate(
            prompt=diag_prompt,
            purpose="failure_diagnosis",
            fallback_fn=rule_fallback
        )
        probable_cause = "AccidentalUserMistake" if is_accidental_user_mistake else (gemini_cause if (gemini_cause and not status.startswith("FALLBACK")) else self._categorize_cause(stderr))

        # 5. Extract Surrounding Code Snippet
        surrounding_code = self._get_surrounding_code(artifact.source_code, failing_line)


        # 5. Construct Structured Repair Prompt for Gemini
        repair_prompt = self._build_repair_prompt(
            workflow_id=artifact.workflow_id,
            probable_cause=probable_cause,
            failing_line=failing_line,
            failing_step_name=failing_step_name,
            failing_selector=failing_selector,
            stderr=stderr,
            surrounding_code=surrounding_code,
            full_source=artifact.source_code
        )

        diagnosis = FailureDiagnosis(
            artifact_id=artifact.artifact_id,
            workflow_id=artifact.workflow_id,
            failing_line=failing_line,
            failing_step_number=failing_step_num,
            failing_step_name=failing_step_name,
            failing_selector=failing_selector,
            probable_cause=probable_cause,
            traceback=traceback_str,
            surrounding_code=surrounding_code,
            repair_prompt=repair_prompt
        )

        logger.info(
            f"FailureDiagnoser diagnosed Artifact ID={artifact.artifact_id[:8]} "
            f"Cause='{probable_cause}' FailingStep='{failing_step_name}' Line={failing_line}"
        )
        return diagnosis

    def _extract_line_number(self, stderr: str) -> Optional[int]:
        """Extracts line number from Python traceback stderr strings."""
        matches = re.findall(r"line (\d+)", stderr)
        if matches:
            try:
                return int(matches[-1])
            except ValueError:
                pass
        return None

    def _match_step(self, line: Optional[int], artifact: CodeArtifact) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """Matches a 1-indexed line number against CodeArtifact step_map."""
        if not line or not artifact.step_map:
            return None, None, None

        for step_num, step_info in artifact.step_map.items():
            start = step_info.get("line_start", 0)
            end = step_info.get("line_end", 0)
            if start <= line <= end:
                return int(step_num), step_info.get("action_name"), step_info.get("selector")

        return None, None, None

    def _categorize_cause(self, stderr: str) -> str:
        """Categorizes probable error cause based on stderr output."""
        if "SyntaxError" in stderr or "IndentationError" in stderr:
            return "SyntaxError"
        elif "PlaywrightTimeoutError" in stderr or "selector" in stderr.lower():
            return "SelectorNotFoundError"
        elif "ExecutionTimedOutError" in stderr or "TimeoutError" in stderr:
            return "TimeoutError"
        elif "NameError" in stderr or "AttributeError" in stderr:
            return "ReferenceError"
        else:
            return "RuntimeError"


    def _get_surrounding_code(self, source_code: str, line: Optional[int], context_lines: int = 4) -> str:
        """Extracts surrounding code snippet for the failing line."""
        if not line or not source_code:
            return ""
        
        lines = source_code.splitlines()
        idx = line - 1
        start = max(0, idx - context_lines)
        end = min(len(lines), idx + context_lines + 1)

        snippet_lines = []
        for i in range(start, end):
            prefix = " > " if i == idx else "   "
            snippet_lines.append(f"{i + 1:4d}:{prefix}{lines[i]}")

        return "\n".join(snippet_lines)

    def _build_repair_prompt(
        self,
        workflow_id: str,
        probable_cause: str,
        failing_line: Optional[int],
        failing_step_name: Optional[str],
        failing_selector: Optional[str],
        stderr: str,
        surrounding_code: str,
        full_source: str
    ) -> str:
        """Constructs a clear, structured prompt for code repair engines."""
        return (
            f"You are the Self-Healing Engine for GhostTrace AI.\n"
            f"A Playwright Python automation script failed during sandbox execution.\n\n"
            f"=== ERROR DIAGNOSIS ===\n"
            f"- Probable Cause: {probable_cause}\n"
            f"- Failing Line: {failing_line or 'Unknown'}\n"
            f"- Failing Step: {failing_step_name or 'Unknown'}\n"
            f"- Failing Selector: {failing_selector or 'None'}\n\n"
            f"=== STDERR TRACEBACK ===\n"
            f"{stderr[:1000]}\n\n"
            f"=== SURROUNDING CODE SNIPPET ===\n"
            f"{surrounding_code}\n\n"
            f"=== ORIGINAL SOURCE CODE ===\n"
            f"{full_source}\n\n"
            f"INSTRUCTIONS FOR 5-LEVEL AI SELF-HEALING:\n"
            f"Analyze the error across all 5 levels of self-healing and re-synthesize the repaired script:\n"
            f"- Level 1 (Selector Healing): Patch updated CSS/XPath selectors (e.g. `#submit-btn` -> `#submit_button`).\n"
            f"- Level 2 (Locator Healing): Relocate element if moved into a new div, iframe, or modal container.\n"
            f"- Level 3 (Structural Healing): Re-sequence step order if form step order changed (e.g. `Invoice -> Vendor -> Amount` instead of `Invoice -> Amount -> Vendor`).\n"
            f"- Level 4 (Semantic Healing): Re-map fields if semantic labels changed (e.g. `Invoice Number` -> `Document ID`).\n"
            f"- Level 5 (Intent Healing): Re-synthesize step flow if UI interaction intent expanded (e.g. `Click Save` -> `Click Review` -> `Click Confirm`).\n\n"
            f"Return ONLY valid, executable Python Playwright source code."
        )

