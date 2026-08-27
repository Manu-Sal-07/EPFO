from typing import Optional, Tuple
from pfcompass.casewise.state_machine import CaseState, CaseStateMachine


class DemoEventSimulator:
    """
    Simulates EPFO back-office event progression for demo purposes.
    Allows demo users to step through case life cycles interactively.
    """

    # Simulation progression sequence: (new_state, event_type, actor, what_happened, why_it_happened)
    SIMULATION_SEQUENCE = {
        # CLAIM path
        ("CLAIM", CaseState.DRAFT): (
            CaseState.SUBMITTED,
            "CLAIM_SUBMITTED",
            "CITIZEN",
            "Claim Form submitted online by citizen via PF Compass portal",
            "Citizen submitted application for PF withdrawal/transfer",
        ),
        ("CLAIM", CaseState.SUBMITTED): (
            CaseState.UNDER_REVIEW,
            "PROCESSING_STARTED",
            "EPFO",
            "EPFO Field Office acknowledged claim application (Ref #EPFO/2026/89421)",
            "Automated intake system routed claim to Regional Office for processing",
        ),
        ("CLAIM", CaseState.UNDER_REVIEW): (
            CaseState.DOCUMENT_PENDING,
            "DOCUMENT_REQUESTED",
            "EPFO",
            "EPFO officer requested upload of Form 15G and cancelled cheque scan",
            "Tax exemption verification requires signed Form 15G declaration",
        ),
        ("CLAIM", CaseState.DOCUMENT_PENDING): (
            CaseState.DOCUMENT_SUBMITTED,
            "DOCUMENT_SUBMITTED",
            "CITIZEN",
            "Citizen uploaded requested Form 15G PDF document",
            "Citizen fulfilled document request from EPFO",
        ),
        ("CLAIM", CaseState.DOCUMENT_SUBMITTED): (
            CaseState.APPROVED,
            "EPFO_APPROVED",
            "EPFO",
            "EPFO Field Office approved claim application for final settlement",
            "All service records and document verifications satisfied",
        ),
        ("CLAIM", CaseState.APPROVED): (
            CaseState.SETTLED,
            "AMOUNT_CREDITED",
            "EPFO",
            "Settlement amount credited to citizen's registered bank account via NEFT",
            "Payment advice executed by State Bank of India nodal branch",
        ),
        # CORRECTION path
        ("CORRECTION", CaseState.OPEN): (
            CaseState.IN_CORRECTION,
            "CORRECTION_INITIATED",
            "CITIZEN",
            "Citizen submitted Joint Declaration request for record update",
            "Discrepancy in date of exit/KYC identified by PF Health engine",
        ),
        ("CORRECTION", CaseState.IN_CORRECTION): (
            CaseState.PENDING_EPFO,
            "EMPLOYER_APPROVED",
            "EMPLOYER",
            "Previous employer verified and digitally signed Joint Declaration form",
            "Employer confirmed service period dates in Unified Employer Portal",
        ),
        ("CORRECTION", CaseState.PENDING_EPFO): (
            CaseState.RESOLVED,
            "CORRECTION_APPLIED",
            "EPFO",
            "EPFO Field Office updated member master record in central database",
            "Section Officer verified employer endorsement and approved correction",
        ),
        ("CORRECTION", CaseState.RESOLVED): (
            CaseState.CLOSED,
            "CASE_CLOSED",
            "SYSTEM",
            "Correction case marked CLOSED as issue is fully resolved",
            "Health finding updated to RESOLVED status",
        ),
    }

    def simulate_next_event(self, case_type: str, current_status: str) -> Optional[Tuple[str, str, str, str, str]]:
        key = (case_type.upper(), current_status)
        return self.SIMULATION_SEQUENCE.get(key)
