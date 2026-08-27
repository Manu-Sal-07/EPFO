import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.ai.output_schemas import DecisionExplanation
from pfcompass.api.middleware.auth_middleware import get_current_citizen
from pfcompass.database import get_db_session
from pfcompass.models import Citizen
from pfcompass.schemas.decision import (
    CalculationRequest,
    CalculationResponse,
    DecisionEvaluateRequest,
    EligibilityResultResponse,
    PreSubmitRequest,
    PreSubmitResponse,
)
from pfcompass.services.decision_service import DecisionService

router = APIRouter(prefix="/decision", tags=["PF Decision Engine"])


@router.post("/evaluate", response_model=EligibilityResultResponse)
async def evaluate_eligibility(
    data: DecisionEvaluateRequest,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Evaluate deterministic eligibility for a chosen claim/transfer option."""
    service = DecisionService(session)
    return await service.evaluate_eligibility(
        citizen_id=current_citizen.id,
        claim_type=data.claim_type,
        advance_ground=data.advance_ground,
    )


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_payout(
    data: CalculationRequest,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Calculate estimated payout amount, service years, tax exemption, and TDS deductions."""
    service = DecisionService(session)
    return await service.calculate_payout(
        citizen_id=current_citizen.id,
        claim_type=data.claim_type,
        advance_ground=data.advance_ground,
        requested_amount=data.requested_amount,
        has_pan=data.has_pan,
    )


@router.post("/presubmit", response_model=PreSubmitResponse)
async def run_presubmit_audit(
    data: PreSubmitRequest,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Run pre-submit readiness audit for KYC, bank details, and exit date verification."""
    service = DecisionService(session)
    return await service.run_presubmit_audit(
        citizen_id=current_citizen.id,
        claim_type=data.claim_type,
    )


@router.post("/explain", response_model=DecisionExplanation)
async def explain_decision(
    data: DecisionEvaluateRequest,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Generate an AI-powered plain-language explanation for an eligibility decision."""
    from pfcompass.ai.explainer import ai_explainer

    service = DecisionService(session)
    res = await service.evaluate_eligibility(
        citizen_id=current_citizen.id,
        claim_type=data.claim_type,
        advance_ground=data.advance_ground,
    )
    calc = await service.calculate_payout(
        citizen_id=current_citizen.id,
        claim_type=data.claim_type,
        advance_ground=data.advance_ground,
    )

    return await ai_explainer.explain_decision(
        claim_type=res.claim_type,
        form_number=res.form_number,
        eligibility_status=res.status,
        why_it_happened=res.why_it_happened,
        recommended_action=res.recommended_action,
        tax_note=calc.taxability_reason,
    )
