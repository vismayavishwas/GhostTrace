import logging
from typing import Optional, List
from app.models.workflow import WorkflowDNA
from app.agents.workflow_dna.publisher import DNAPublisher
from app.agents.compiler.models import CodeArtifact
from app.agents.compiler.playwright_generator import PlaywrightCodeGenerator
from app.agents.compiler.publisher import CodePublisher

logger = logging.getLogger("ghosttrace.compiler")


class CompilerAgent:
    """
    Compiler Agent responsible for translating WorkflowDNA into executable,
    modular Playwright Python source code with precise step-to-line mapping metadata.
    """
    def __init__(
        self,
        generator: Optional[PlaywrightCodeGenerator] = None,
        dna_publisher: Optional[DNAPublisher] = None,
        publisher: Optional[CodePublisher] = None,
    ):
        self.generator = generator or PlaywrightCodeGenerator()
        self.publisher = publisher or CodePublisher()
        self._artifacts_history: List[CodeArtifact] = []

        if dna_publisher:
            dna_publisher.subscribe(self.on_workflow_dna)
            logger.info("CompilerAgent subscribed to DNAPublisher")

    async def on_workflow_dna(self, dna: WorkflowDNA) -> CodeArtifact:
        """Callback executed upon receiving a synthesized WorkflowDNA object."""
        return await self.compile_dna(dna)

    async def compile_dna(self, dna: WorkflowDNA) -> CodeArtifact:
        """
        Translates WorkflowDNA into a CodeArtifact containing modular Python Playwright
        source code and step line mappings for self-healing.
        """
        source_code, step_map = self.generator.generate_code(dna)

        artifact = CodeArtifact(
            workflow_id=dna.workflow_id,
            source_code=source_code,
            language="python",
            framework="playwright",
            step_map=step_map,
            metadata={
                "workflow_name": dna.name,
                "total_steps": len(dna.steps),
                "applications_involved": dna.applications_involved,
                "confidence_score": dna.confidence_score,
            }
        )

        self._artifacts_history.append(artifact)
        logger.info(
            f"CompilerAgent compiled CodeArtifact ID={artifact.artifact_id[:8]} "
            f"for Workflow ID={dna.workflow_id[:8]} ({len(step_map)} step mappings)"
        )

        await self.publisher.publish(artifact)
        return artifact

    def get_artifacts_history(self) -> List[CodeArtifact]:
        """Returns history of compiled CodeArtifact objects."""
        return list(self._artifacts_history)

