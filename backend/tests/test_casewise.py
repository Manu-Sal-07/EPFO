import uuid
from datetime import datetime, timezone, timedelta
import pytest
from pfcompass.casewise.state_machine import CaseState, CaseStateMachine, InvalidTransitionError
from pfcompass.casewise.timeline_builder import TimelineBuilder
from pfcompass.casewise.next_action import get_next_actions
from pfcompass.casewise.simulator import DemoEventSimulator
from pfcompass.models import Case, CaseEvent


def test_state_machine_valid_transitions():
    sm = CaseStateMachine()
    
    # Claim flow valid transition: DRAFT -> SUBMITTED
    dummy_case = Case(id=uuid.uuid4(), case_type="CLAIM", status="DRAFT")
    event = sm.transition(
        case=dummy_case,
        new_state="SUBMITTED",
        event_type="CLAIM_SUBMITTED",
        actor="CITIZEN",
        what_happened="Claim submitted",
    )
    assert event.new_status == "SUBMITTED"
    assert event.previous_status == "DRAFT"


def test_state_machine_invalid_transition():
    sm = CaseStateMachine()
    
    # Invalid transition: DRAFT directly to APPROVED
    dummy_case = Case(id=uuid.uuid4(), case_type="CLAIM", status="DRAFT")
    with pytest.raises(InvalidTransitionError):
        sm.transition(
            case=dummy_case,
            new_state="APPROVED",
            event_type="EPFO_APPROVED",
            actor="EPFO",
            what_happened="Invalid fast forward",
        )


def test_timeline_builder():
    tb = TimelineBuilder()
    case_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    
    events = [
        CaseEvent(
            id=uuid.uuid4(),
            case_id=case_id,
            event_type="CASE_OPENED",
            actor="SYSTEM",
            what_happened="Case opened",
            previous_status=None,
            new_status="DRAFT",
            occurred_at=now - timedelta(days=2),
        ),
        CaseEvent(
            id=uuid.uuid4(),
            case_id=case_id,
            event_type="CLAIM_SUBMITTED",
            actor="CITIZEN",
            what_happened="Citizen submitted claim",
            previous_status="DRAFT",
            new_status="SUBMITTED",
            occurred_at=now,
        ),
    ]
    
    timeline = tb.build_timeline(str(case_id), events)
    assert timeline.current_status == "SUBMITTED"
    assert len(timeline.items) == 2
    assert timeline.items[0].actor_label == "PF Compass Engine"
    assert timeline.items[1].actor_label == "Citizen"
    assert timeline.total_duration_days == 2.0


def test_next_action_lookup():
    action = get_next_actions("CLAIM", "SUBMITTED")
    assert "EPFO" in action.primary_action or "Awaiting" in action.primary_action
    assert action.estimated_wait_days > 0
    assert not action.can_citizen_act_now

    action_pending_doc = get_next_actions("CLAIM", "DOCUMENT_PENDING", case_id="test-123")
    assert action_pending_doc.can_citizen_act_now
    assert "/cases/test-123/upload" in action_pending_doc.action_url


def test_demo_simulator():
    sim = DemoEventSimulator()
    next_step = sim.simulate_next_event("CLAIM", "SUBMITTED")
    assert next_step is not None
    new_state, event_type, actor, what_happened, why_it_happened = next_step
    assert new_state == CaseState.UNDER_REVIEW
    assert event_type == "PROCESSING_STARTED"
    assert actor == "EPFO"
