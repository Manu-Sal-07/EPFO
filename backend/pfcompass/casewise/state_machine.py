from enum import Enum
from typing import Any, Dict, Optional, Set
from pfcompass.models import Case, CaseEvent


class CaseState(str, Enum):
    # Common / Claim States
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    DOCUMENT_PENDING = "DOCUMENT_PENDING"
    DOCUMENT_SUBMITTED = "DOCUMENT_SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SETTLED = "SETTLED"
    CLOSED = "CLOSED"
    WITHDRAWN = "WITHDRAWN"

    # Correction States
    OPEN = "OPEN"
    IN_CORRECTION = "IN_CORRECTION"
    PENDING_EPFO = "PENDING_EPFO"
    RESOLVED = "RESOLVED"


# Valid transitions: { from_state: set of valid to_states }
VALID_TRANSITIONS: Dict[CaseState, Set[CaseState]] = {
    CaseState.DRAFT: {CaseState.SUBMITTED, CaseState.WITHDRAWN},
    CaseState.SUBMITTED: {CaseState.UNDER_REVIEW, CaseState.WITHDRAWN},
    CaseState.UNDER_REVIEW: {CaseState.DOCUMENT_PENDING, CaseState.APPROVED, CaseState.REJECTED},
    CaseState.DOCUMENT_PENDING: {CaseState.DOCUMENT_SUBMITTED, CaseState.WITHDRAWN},
    CaseState.DOCUMENT_SUBMITTED: {CaseState.UNDER_REVIEW, CaseState.APPROVED, CaseState.REJECTED},
    CaseState.APPROVED: {CaseState.SETTLED, CaseState.CLOSED},
    CaseState.SETTLED: {CaseState.CLOSED},
    CaseState.REJECTED: {CaseState.CLOSED},
    CaseState.CLOSED: set(),  # terminal
    CaseState.WITHDRAWN: set(),  # terminal
    # Correction states
    CaseState.OPEN: {CaseState.IN_CORRECTION, CaseState.CLOSED},
    CaseState.IN_CORRECTION: {CaseState.PENDING_EPFO, CaseState.RESOLVED},
    CaseState.PENDING_EPFO: {CaseState.RESOLVED, CaseState.REJECTED},
    CaseState.RESOLVED: {CaseState.CLOSED},
}


class InvalidTransitionError(ValueError):
    """Raised when an invalid case state transition is attempted."""
    pass


class CaseStateMachine:
    """
    Deterministic state machine for case state transitions.
    Ensures state machine transitions are valid and builds the corresponding CaseEvent.
    """

    @staticmethod
    def is_transition_valid(current_state: str, new_state: str) -> bool:
        try:
            curr_enum = CaseState(current_state)
            new_enum = CaseState(new_state)
        except ValueError:
            return False
        return new_enum in VALID_TRANSITIONS.get(curr_enum, set())

    def transition(
        self,
        case: Case,
        new_state: str,
        event_type: str,
        actor: str,
        what_happened: str,
        why_it_happened: Optional[str] = None,
        evidence: Optional[Dict[str, Any]] = None,
        metadata_payload: Optional[Dict[str, Any]] = None,
    ) -> CaseEvent:
        curr_state = case.status
        if not self.is_transition_valid(curr_state, new_state):
            raise InvalidTransitionError(
                f"Cannot transition case {case.id} ({case.case_type}) from state '{curr_state}' to '{new_state}'"
            )

        event = CaseEvent(
            case_id=case.id,
            event_type=event_type,
            actor=actor,
            what_happened=what_happened,
            why_it_happened=why_it_happened,
            evidence=evidence,
            metadata_payload=metadata_payload,
            previous_status=curr_state,
            new_status=new_state,
        )
        return event
