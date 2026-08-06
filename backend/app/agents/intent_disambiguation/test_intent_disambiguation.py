import asyncio
from typing import Optional
from app.models.enums import IntentChoice
from app.models.workflow import WorkflowCandidate, IntentDecision
from app.agents.intent_disambiguation import (
    IntentDisambiguationAgent,
    AmbiguityDetector,
    DecisionPublisher,
)


def create_sample_candidate(confidence: float = 0.90, repetition_count: int = 3) -> WorkflowCandidate:
    return WorkflowCandidate(
        confidence_score=confidence,
        repetition_count=repetition_count,
        sequence_event_ids=["evt-1", "evt-2", "evt-3"],
        description="Sample Workflow Candidate"
    )


async def run_intent_disambiguation_verification():
    print("=== GhostTrace AI: Intent Disambiguation Agent Verification ===")

    publisher = DecisionPublisher()
    detector = AmbiguityDetector(auto_approve_threshold=0.85)
    agent = IntentDisambiguationAgent(ambiguity_detector=detector, publisher=publisher)

    published_records = []

    async def sample_decision_subscriber(decision: IntentDecision, candidate: Optional[WorkflowCandidate]):
        published_records.append((decision, candidate))
        cand_id = candidate.candidate_id[:8] if candidate else "None"
        print(f"   [Decision Subscriber Received] Choice={decision.choice} Reason='{decision.reason}' Candidate={cand_id}")

    publisher.subscribe(sample_decision_subscriber)
    assert publisher.subscriber_count() == 1, "Subscriber registration failed"

    # 1. Test High Confidence Candidate (Auto-Approve Flow)
    high_conf_candidate = create_sample_candidate(confidence=0.90)
    decision_1 = await agent.evaluate_candidate(high_conf_candidate)
    
    assert decision_1.choice == IntentChoice.APPROVED
    assert len(published_records) == 1
    assert published_records[0][0].choice == IntentChoice.APPROVED
    assert published_records[0][1].candidate_id == high_conf_candidate.candidate_id
    print("[OK] High Confidence Flow: Candidate auto-approved and published with both decision & candidate.")

    # 2. Test Low Confidence Candidate (Ambiguity Request Flow)
    published_records.clear()
    low_conf_candidate = create_sample_candidate(confidence=0.72)
    decision_2 = await agent.evaluate_candidate(low_conf_candidate)
    
    assert decision_2.choice == IntentChoice.REJECTED  # Pending request state
    assert decision_2.reason == "Low confidence"
    assert len(published_records) == 0, "Ambiguous candidate should not be published automatically"
    assert len(agent.get_pending_decisions()) == 1, "Pending decision count mismatch"
    print("[OK] Low Confidence Flow: Ambiguity detected with reason 'Low confidence' and paused for HITL.")

    # 3. Test Mistake Flow Resolution
    pending_id = decision_2.decision_id
    resolved_dec, resolved_cand = await agent.receive_decision(pending_id, IntentChoice.MISTAKE)
    
    assert resolved_dec.choice == IntentChoice.MISTAKE
    assert resolved_cand is None, "Mistake candidate should be discarded (None)"
    assert len(published_records) == 1
    assert published_records[0][0].choice == IntentChoice.MISTAKE
    assert published_records[0][1] is None
    assert len(agent.get_pending_decisions()) == 0
    print("[OK] Mistake Flow: Candidate discarded and decision published.")

    # 4. Test Branch Flow Resolution
    published_records.clear()
    branch_candidate = create_sample_candidate(confidence=0.75)
    branch_dec_req = await agent.evaluate_candidate(branch_candidate)
    
    resolved_dec, resolved_cand = await agent.receive_decision(branch_dec_req.decision_id, IntentChoice.BRANCH, comment="User branch")
    assert resolved_dec.choice == IntentChoice.BRANCH
    assert resolved_cand is not None
    assert "[Branch]" in resolved_cand.description
    assert published_records[0][1].candidate_id == branch_candidate.candidate_id
    print("[OK] Branch Flow: Candidate marked as new workflow branch and published.")

    # 5. Test Manual Approved Flow Resolution
    published_records.clear()
    manual_candidate = create_sample_candidate(confidence=0.65)
    manual_dec_req = await agent.evaluate_candidate(manual_candidate)
    
    resolved_dec, resolved_cand = await agent.receive_decision(manual_dec_req.decision_id, IntentChoice.APPROVED)
    assert resolved_dec.choice == IntentChoice.APPROVED
    assert resolved_cand is not None
    assert published_records[0][1].candidate_id == manual_candidate.candidate_id
    print("[OK] Manual Approved Flow: Candidate approved by user and published.")

    # 6. Test KeyError on Unknown Decision ID
    try:
        await agent.receive_decision("invalid-uuid", IntentChoice.APPROVED)
        assert False, "Should have raised KeyError"
    except KeyError:
        print("[OK] Edge Cases: Non-existent decision ID handled with KeyError.")

    print("\nPASSED: Intent Disambiguation Agent Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_intent_disambiguation_verification())
