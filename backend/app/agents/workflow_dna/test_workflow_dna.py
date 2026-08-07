import asyncio
from datetime import datetime, timezone
from typing import Optional
from app.models.enums import EventType, IntentChoice
from app.models.telemetry import TelemetryEvent
from app.models.workflow import WorkflowCandidate, IntentDecision, WorkflowDNA
from app.agents.intent_disambiguation.publisher import DecisionPublisher
from app.agents.workflow_dna import WorkflowDNAAgent, DNATransformer, DNAPublisher


def create_sample_event(event_type: EventType, selector: str, tag: str, app: str, val: Optional[str] = None) -> TelemetryEvent:
    return TelemetryEvent(
        event_type=event_type,
        target_selector=selector,
        element_tag=tag,
        app_title=app,
        input_value=val,
        timestamp=datetime.now(timezone.utc)
    )


async def run_workflow_dna_verification():
    print("=== GhostTrace AI: Workflow DNA Agent Verification ===")

    decision_pub = DecisionPublisher()
    dna_pub = DNAPublisher()
    agent = WorkflowDNAAgent(decision_publisher=decision_pub, publisher=dna_pub)

    published_dna_list = []

    async def sample_dna_subscriber(dna: WorkflowDNA):
        published_dna_list.append(dna)
        print(f"   [DNA Subscriber Received] DNA ID={dna.workflow_id[:8]} Title='{dna.name}' Steps={len(dna.steps)} Apps={dna.applications_involved}")

    dna_pub.subscribe(sample_dna_subscriber)
    assert dna_pub.subscriber_count() == 1, "Subscriber registration failed"

    # 1. Test Telemetry -> WorkflowDNA Semantic Transformation
    e1 = create_sample_event(EventType.CLICK, "#nav-invoices", "NAV", "SAP ERP")
    e2 = create_sample_event(EventType.TYPE, "#invoice-id-input", "INPUT", "SAP ERP", val="INV-99482")
    e3 = create_sample_event(EventType.CLICK, "#submit-button", "BUTTON", "Zendesk Support")

    candidate = WorkflowCandidate(
        sequence_event_ids=[e1.event_id, e2.event_id, e3.event_id],
        sequence=[e1, e2, e3],
        confidence_score=0.92,
        repetition_count=3,
        description="SAP and Zendesk Invoice Processing"
    )

    decision = IntentDecision(
        candidate_id=candidate.candidate_id,
        choice=IntentChoice.APPROVED,
        reason="Auto-approved"
    )

    # Publish approved decision & candidate
    await decision_pub.publish(decision, candidate)

    assert len(published_dna_list) == 1, "WorkflowDNA should be extracted for approved candidate"
    dna = published_dna_list[0]

    # Verify Semantic Steps
    assert len(dna.steps) == 3, f"Step count mismatch: expected 3, got {len(dna.steps)}"
    assert dna.steps[0].action_name != "", "Step 1 action name should not be empty"
    assert dna.steps[1].action_name != "", "Step 2 action name should not be empty"
    assert dna.steps[2].action_name != "", "Step 3 action name should not be empty"
    print(f"[OK] Telemetry -> WorkflowDNA Transformation: Mapped {len(dna.steps)} events to dynamic semantic steps ({[s.action_name for s in dna.steps]}).")


    # 2. Test Multi-Application Detection
    assert sorted(dna.applications_involved) == ["SAP ERP", "Zendesk Support"], f"Apps mismatch: {dna.applications_involved}"
    print("[OK] Multi-Application Detection: Unique target applications identified correctly.")

    # 3. Test Confidence Preservation & Metadata
    assert dna.confidence_score == 0.92, f"Confidence score mismatch: expected 0.92, got {dna.confidence_score}"
    assert dna.metadata["candidate_id"] == candidate.candidate_id
    print("[OK] Confidence & Lineage Preservation: Candidate confidence score and lineage IDs preserved.")

    # 4. Test Clean JSON Serialization
    json_output = dna.model_dump_json(indent=2)
    assert '"workflow_id"' in json_output
    assert '"steps"' in json_output
    assert '"applications_involved"' in json_output
    print("[OK] JSON Serialization: WorkflowDNA model serializes to clean JSON matching schema.")

    # 5. Test Ignored Decision Choice (MISTAKE)
    published_dna_list.clear()
    mistake_decision = IntentDecision(candidate_id=candidate.candidate_id, choice=IntentChoice.MISTAKE)
    await decision_pub.publish(mistake_decision, candidate)
    assert len(published_dna_list) == 0, "Mistake decision should be ignored by WorkflowDNAAgent"
    print("[OK] Decision Filter: Discarded/Mistake decisions correctly ignored.")

    print("\nPASSED: Workflow DNA Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_workflow_dna_verification())
