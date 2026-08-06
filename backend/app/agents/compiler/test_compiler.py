import asyncio
from app.models.workflow import WorkflowDNA, WorkflowDNAStep
from app.agents.workflow_dna.publisher import DNAPublisher
from app.agents.compiler import CompilerAgent, PlaywrightCodeGenerator, CodeArtifact, CodePublisher


def create_sample_dna() -> WorkflowDNA:
    step1 = WorkflowDNAStep(
        step_number=1,
        action_name="Navigate to SAP Portal",
        target_app="SAP ERP",
        selector="https://sap.ghosttrace.ai",
        fallback_selectors=["a.sap-login"]
    )
    step2 = WorkflowDNAStep(
        step_number=2,
        action_name="Enter Invoice ID",
        target_app="SAP ERP",
        selector="#invoice-id-input",
        fallback_selectors=["input[name='invoice']"],
        parameters={"value": "INV-2026-9041"}
    )
    step3 = WorkflowDNAStep(
        step_number=3,
        action_name="Submit Form",
        target_app="SAP ERP",
        selector="#submit-btn",
        fallback_selectors=["button[type='submit']"]
    )
    
    return WorkflowDNA(
        name="SAP Invoice Processing",
        description="Processes SAP invoices automatically",
        steps=[step1, step2, step3],
        inputs_schema={"input_step_2": {"type": "string", "default": "INV-2026-9041"}},
        output_schema={"status": "string"},
        applications_involved=["SAP ERP"],
        confidence_score=0.95
    )


async def run_compiler_verification():
    print("=== GhostTrace AI: Compiler Agent Verification ===")

    dna_pub = DNAPublisher()
    code_pub = CodePublisher()
    agent = CompilerAgent(dna_publisher=dna_pub, publisher=code_pub)

    published_artifacts = []

    async def sample_code_subscriber(artifact: CodeArtifact):
        published_artifacts.append(artifact)
        print(f"   [Code Subscriber Received] Artifact ID={artifact.artifact_id[:8]} Framework={artifact.framework} Lines={len(artifact.source_code.splitlines())}")

    code_pub.subscribe(sample_code_subscriber)
    assert code_pub.subscriber_count() == 1, "Code subscriber registration failed"

    # 1. Test WorkflowDNA -> Python Code Synthesis
    sample_dna = create_sample_dna()
    await dna_pub.publish(sample_dna)

    assert len(published_artifacts) == 1, "CompilerAgent should publish CodeArtifact on DNA emission"
    artifact = published_artifacts[0]

    # Verify Modular Code Functions
    source = artifact.source_code
    assert "async def step_1_navigate_to_sap_portal" in source, "Step 1 modular helper function missing"
    assert "async def step_2_enter_invoice_id" in source, "Step 2 modular helper function missing"
    assert "async def step_3_submit_form" in source, "Step 3 modular helper function missing"
    assert "async def run_workflow" in source, "Main workflow runner missing"
    print("[OK] Modular Code Synthesis: Generated modular helper functions for each WorkflowDNAStep.")

    # 2. Test Step-to-Line Mapping
    assert len(artifact.step_map) == 3, f"Step map length mismatch: expected 3, got {len(artifact.step_map)}"
    step_1_map = artifact.step_map[1]
    assert step_1_map["function_name"] == "step_1_navigate_to_sap_portal"
    assert step_1_map["line_start"] < step_1_map["line_end"]
    print("[OK] Step Line Mapping: Step-to-line mappings created for precise self-healing diagnosis.")

    # 3. Test Pure Python Syntax Compilation
    try:
        compiled_code_object = compile(source, "<string>", "exec")
        assert compiled_code_object is not None
        print("[OK] Syntax Validation: Generated Playwright Python code compiled cleanly via built-in compile().")
    except SyntaxError as e:
        assert False, f"Generated Python code contains syntax error: {e}"

    # 4. Test CodeArtifact Model Metadata & Lineage
    assert artifact.workflow_id == sample_dna.workflow_id
    assert artifact.language == "python"
    assert artifact.framework == "playwright"
    print("[OK] Artifact Metadata: Lineage IDs, language, and framework metadata preserved.")

    print("\nPASSED: Compiler Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_compiler_verification())
