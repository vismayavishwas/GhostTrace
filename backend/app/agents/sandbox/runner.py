import os
import re
import sys
import time
import asyncio
import tempfile
import logging
from typing import Tuple, Optional, List
from app.agents.compiler.models import CodeArtifact
from app.models.execution import SandboxResult

logger = logging.getLogger("ghosttrace.sandbox.runner")


class SubprocessRunner:
    """
    Executes Python source code from a CodeArtifact in an isolated subprocess.
    Enforces process timeouts, captures stdout/stderr/tracebacks, and records script artifacts.
    """
    def __init__(self, default_timeout_sec: float = 30.0):
        self.default_timeout_sec = default_timeout_sec

    async def execute_artifact(
        self,
        artifact: CodeArtifact,
        timeout_sec: Optional[float] = None
    ) -> SandboxResult:
        """
        Executes the provided CodeArtifact in an isolated subprocess.
        Returns a validated SandboxResult object.
        """
        timeout = timeout_sec or self.default_timeout_sec
        start_time = time.perf_counter()
        
        # 1. Write CodeArtifact source_code to temporary script file
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix="_ghosttrace_sandbox.py",
            delete=False,
            encoding="utf-8"
        )
        temp_path = temp_file.name
        
        try:
            temp_file.write(artifact.source_code)
            temp_file.flush()
            temp_file.close()

            logger.info(f"SubprocessRunner created temp script at '{temp_path}' for Artifact ID={artifact.artifact_id[:8]}")

            # 2. Spawn isolated Python subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=dict(os.environ, PYTHONPATH=os.getcwd())
            )

            # 3. Communicate with timeout management
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                stdout_str = stdout_bytes.decode("utf-8", errors="replace")
                stderr_str = stderr_bytes.decode("utf-8", errors="replace")
                exit_code = process.returncode if process.returncode is not None else 0
                success = (exit_code == 0)

            except asyncio.TimeoutError:
                logger.warning(f"SubprocessRunner execution timed out after {timeout}s for Artifact ID={artifact.artifact_id[:8]}")
                try:
                    if sys.platform == "win32":
                        os.system(f"taskkill /F /T /PID {process.pid} >nul 2>&1")
                    else:
                        process.kill()
                    await process.communicate()
                except Exception:
                    pass

                
                exit_code = -1
                stdout_str = ""
                stderr_str = f"ExecutionTimedOutError: Subprocess timed out after {timeout} seconds."
                success = False

        except Exception as e:
            logger.error(f"SubprocessRunner failed to spawn subprocess: {e}", exc_info=True)
            exit_code = -1
            stdout_str = ""
            stderr_str = f"SubprocessSpawnError: {str(e)}"
            success = False

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 4. Parse traceback and failing line details
        error_traceback, failing_line = self._parse_traceback(stderr_str, temp_path)

        # 5. Build SandboxResult with artifact metadata and temp script path reference
        result = SandboxResult(
            execution_id=artifact.artifact_id,
            success=success,
            duration_ms=duration_ms,
            stdout=stdout_str.strip(),
            stderr=stderr_str.strip(),
            error_traceback=error_traceback,
            failing_line=failing_line,
            artifacts=[temp_path]  # Preserve temporary script path for Self-Healing inspection
        )

        logger.info(
            f"SubprocessRunner completed Artifact ID={artifact.artifact_id[:8]} "
            f"Success={success} ExitCode={exit_code} Duration={duration_ms}ms"
        )
        
        # Note: Temp file path is preserved in SandboxResult.artifacts for downstream inspection
        return result

    def _parse_traceback(self, stderr: str, temp_path: str) -> Tuple[Optional[str], Optional[int]]:
        """Parses error traceback and failing line number from stderr output."""
        if not stderr or "Traceback (most recent call last):" not in stderr:
            return None, None

        error_traceback = stderr
        failing_line = None

        # Regex to find failing line number in the temp script file
        escaped_path = re.escape(temp_path)
        pattern = rf'File "{escaped_path}", line (\d+)'
        matches = re.findall(pattern, stderr)
        if matches:
            try:
                failing_line = int(matches[-1])
            except ValueError:
                pass

        return error_traceback, failing_line
