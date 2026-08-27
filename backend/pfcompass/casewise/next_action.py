from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class NextActionSet:
    primary_action: str
    secondary_actions: List[str] = field(default_factory=list)
    estimated_wait_days: int = 0
    can_citizen_act_now: bool = False
    action_url: Optional[str] = None


# Lookup table mapping (case_type, status) to NextActionSet
NEXT_ACTIONS: Dict[Tuple[str, str], NextActionSet] = {
    ("CLAIM", "DRAFT"): NextActionSet(
        primary_action="Complete and submit your claim request",
        secondary_actions=[
            "Review bank account details linked to your UAN",
            "Ensure Form 15G is attached if service is under 5 years",
        ],
        estimated_wait_days=0,
        can_citizen_act_now=True,
        action_url="/decision",
    ),
    ("CLAIM", "SUBMITTED"): NextActionSet(
        primary_action="Awaiting EPFO acknowledgment and initial verification",
        secondary_actions=[
            "EPFO standard processing timeframe is 7-14 working days",
            "Monitor SMS alerts on your registered mobile number",
        ],
        estimated_wait_days=3,
        can_citizen_act_now=False,
    ),
    ("CLAIM", "UNDER_REVIEW"): NextActionSet(
        primary_action="EPFO Field Office is reviewing your claim application",
        secondary_actions=[
            "Verification of employer contributions and service records in progress",
            "No action required from citizen at this stage",
        ],
        estimated_wait_days=7,
        can_citizen_act_now=False,
    ),
    ("CLAIM", "DOCUMENT_PENDING"): NextActionSet(
        primary_action="Upload requested documents to resume claim processing",
        secondary_actions=[
            "Check requested document details in the case timeline below",
            "Ensure files are clear PDF scans under 2MB",
        ],
        estimated_wait_days=0,
        can_citizen_act_now=True,
        action_url="/cases/{case_id}/upload",
    ),
    ("CLAIM", "DOCUMENT_SUBMITTED"): NextActionSet(
        primary_action="Document received — awaiting EPFO re-verification",
        secondary_actions=["Field office officer will re-examine the claim file"],
        estimated_wait_days=5,
        can_citizen_act_now=False,
    ),
    ("CLAIM", "APPROVED"): NextActionSet(
        primary_action="Claim approved — fund transfer instructions sent to bank",
        secondary_actions=[
            "Amount will be credited via NEFT to your registered bank account",
            "Standard bank processing window: 3-5 working days",
        ],
        estimated_wait_days=4,
        can_citizen_act_now=False,
    ),
    ("CLAIM", "SETTLED"): NextActionSet(
        primary_action="Claim successfully settled and funds credited",
        secondary_actions=["Download settlement receipt and passbook update"],
        estimated_wait_days=0,
        can_citizen_act_now=False,
    ),
    ("CLAIM", "REJECTED"): NextActionSet(
        primary_action="Claim rejected — review reason and submit correction or appeal",
        secondary_actions=[
            "Read specific rejection remark in event history",
            "File EPFiGMS grievance if rejection appears erroneous",
        ],
        estimated_wait_days=0,
        can_citizen_act_now=True,
        action_url="https://epfigms.gov.in",
    ),
    ("CLAIM", "CLOSED"): NextActionSet(
        primary_action="Case is closed",
        secondary_actions=[],
        estimated_wait_days=0,
        can_citizen_act_now=False,
    ),
    ("CLAIM", "WITHDRAWN"): NextActionSet(
        primary_action="Claim application withdrawn by citizen",
        secondary_actions=["You can initiate a new claim application at any time"],
        estimated_wait_days=0,
        can_citizen_act_now=False,
    ),
    # CORRECTION Flow Next Actions
    ("CORRECTION", "OPEN"): NextActionSet(
        primary_action="Initiate correction request with supporting proof",
        secondary_actions=[
            "Review detected discrepancy details",
            "Prepare Joint Declaration or Aadhaar verification documents",
        ],
        estimated_wait_days=0,
        can_citizen_act_now=True,
    ),
    ("CORRECTION", "IN_CORRECTION"): NextActionSet(
        primary_action="Awaiting employer verification of Joint Declaration / details",
        secondary_actions=[
            "Contact your employer HR/PF cell for portal approval",
            "Employer must approve request in EPFO Unified Portal (Employer Interface)",
        ],
        estimated_wait_days=5,
        can_citizen_act_now=False,
    ),
    ("CORRECTION", "PENDING_EPFO"): NextActionSet(
        primary_action="Employer approved — pending final EPFO Field Office verification",
        secondary_actions=["EPFO Assistant Commissioner office processing correction"],
        estimated_wait_days=10,
        can_citizen_act_now=False,
    ),
    ("CORRECTION", "RESOLVED"): NextActionSet(
        primary_action="Correction applied successfully in EPFO Member Database",
        secondary_actions=["Verify updated profile details in your PF Health dashboard"],
        estimated_wait_days=0,
        can_citizen_act_now=False,
    ),
    ("CORRECTION", "REJECTED"): NextActionSet(
        primary_action="Correction request rejected by Employer or EPFO",
        secondary_actions=["Check rejection reason and resubmit with correct documents"],
        estimated_wait_days=0,
        can_citizen_act_now=True,
    ),
    ("CORRECTION", "CLOSED"): NextActionSet(
        primary_action="Correction case closed",
        secondary_actions=[],
        estimated_wait_days=0,
        can_citizen_act_now=False,
    ),
}


def get_next_actions(case_type: str, status: str, case_id: Optional[str] = None) -> NextActionSet:
    key = (case_type.upper(), status.upper())
    action_set = NEXT_ACTIONS.get(key)
    if not action_set:
        action_set = NextActionSet(
            primary_action=f"Case status: {status}",
            secondary_actions=["Check case timeline for latest updates"],
            estimated_wait_days=0,
            can_citizen_act_now=False,
        )

    # Format action URL if parametrized
    if action_set.action_url and "{case_id}" in action_set.action_url and case_id:
        url = action_set.action_url.format(case_id=case_id)
        return NextActionSet(
            primary_action=action_set.primary_action,
            secondary_actions=action_set.secondary_actions,
            estimated_wait_days=action_set.estimated_wait_days,
            can_citizen_act_now=action_set.can_citizen_act_now,
            action_url=url,
        )

    return action_set
