from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class DecisionEvaluateRequest(BaseModel):
    claim_type: str  # FULL_WITHDRAWAL | PARTIAL_ADVANCE | PENSION_CLAIM | PF_TRANSFER
    advance_ground: Optional[str] = None  # ILLNESS | MARRIAGE | EDUCATION | HOUSE | PANDEMIC


class RuleEvidenceSchema(BaseModel):
    field: str
    expected: str
    actual: str
    description: str


class EligibilityResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_id: str
    claim_type: str
    form_number: str
    status: str  # ELIGIBLE | CONDITIONALLY_ELIGIBLE | INELIGIBLE
    is_eligible: bool
    what_is_wrong: str
    why_it_happened: str
    recommended_action: str
    reasons: List[str]
    evidence: List[RuleEvidenceSchema]


class CalculationRequest(BaseModel):
    claim_type: str = "FULL_WITHDRAWAL"
    advance_ground: Optional[str] = None
    requested_amount: Optional[float] = None
    has_pan: Optional[bool] = True


class CalculationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_share: float
    employer_share: float
    interest_accrued: float
    total_balance: float
    eligible_payout_amount: float
    total_service_years: float
    is_tax_free: bool
    taxability_reason: str
    tds_rate_percent: float
    estimated_tds_amount: float
    form_15g_applicable: bool
    form_15g_recommendation: str


class PreSubmitRequest(BaseModel):
    claim_type: str = "FULL_WITHDRAWAL"


class PreSubmitCheckItemSchema(BaseModel):
    check_id: str
    title: str
    description: str
    status: str
    is_blocking: bool
    remediation_hint: str


class PreSubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_ready_to_submit: bool
    readiness_score: int
    total_checks: int
    passed_checks: int
    blocking_issues_count: int
    check_items: List[PreSubmitCheckItemSchema]
