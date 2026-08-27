import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.ai.output_schemas import CaseNarrative
from pfcompass.api.middleware.auth_middleware import get_current_citizen
from pfcompass.database import get_db_session
from pfcompass.models import Citizen
from pfcompass.schemas.casewise import (
    CaseCreateSchema,
    CaseDetailResponse,
    CaseEventCreate,
    CaseSummaryResponse,
)
from pfcompass.services.casewise_service import CaseWiseService

router = APIRouter(prefix="/cases", tags=["CaseWise"])


@router.get("", response_model=List[CaseSummaryResponse])
async def list_cases(
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """List all cases (claims and corrections) for the authenticated citizen."""
    service = CaseWiseService(session)
    return await service.list_citizen_cases(current_citizen.id)


@router.get("/{case_id}", response_model=CaseDetailResponse)
async def get_case_detail(
    case_id: uuid.UUID,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Get full case details including reconstructed timeline and next actions."""
    service = CaseWiseService(session)
    detail = await service.get_case_detail(current_citizen.id, case_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found or access denied",
        )
    return detail


@router.post("", response_model=CaseDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    data: CaseCreateSchema,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new case (claim or correction workflow)."""
    service = CaseWiseService(session)
    return await service.create_case(current_citizen.id, data)


@router.post("/{case_id}/events", response_model=CaseDetailResponse)
async def add_case_event(
    case_id: uuid.UUID,
    data: CaseEventCreate,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Add an event to the case event log and optionally transition case state."""
    service = CaseWiseService(session)
    try:
        return await service.add_event(current_citizen.id, case_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{case_id}/simulate", response_model=CaseDetailResponse)
async def simulate_case_step(
    case_id: uuid.UUID,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Simulate the next EPFO back-office event for live demonstration."""
    service = CaseWiseService(session)
    try:
        return await service.simulate_next_step(current_citizen.id, case_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{case_id}/explain", response_model=CaseNarrative)
async def explain_case(
    case_id: uuid.UUID,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session),
):
    """Generate an AI-powered case narrative explanation for a CaseWise timeline."""
    from pfcompass.ai.explainer import ai_explainer

    service = CaseWiseService(session)
    detail = await service.get_case_detail(current_citizen.id, case_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found or access denied",
        )

    items = detail.timeline.items if detail.timeline else []
    last_event_desc = items[-1].what_happened if items else "Case initiated"
    next_action_title = detail.next_actions.primary_action if detail.next_actions else None
    next_action_desc = f"Estimated wait: {detail.next_actions.estimated_wait_days} days" if detail.next_actions else None

    return await ai_explainer.explain_case_narrative(
        case_type=detail.case_type,
        current_status=detail.status,
        last_event_description=last_event_desc,
        next_action_title=next_action_title,
        next_action_description=next_action_desc,
    )
