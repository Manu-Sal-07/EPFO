import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.ai.output_schemas import FindingExplanation
from pfcompass.api.middleware.auth_middleware import get_current_citizen
from pfcompass.database import get_db_session
from pfcompass.models import Citizen
from pfcompass.repositories.health_repo import HealthRepository
from pfcompass.schemas.health import HealthFindingResponse, HealthReportResponse
from pfcompass.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["PF Health"])


@router.get("/report", response_model=HealthReportResponse)
async def get_health_report(
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session)
) -> HealthReportResponse:
    health_service = HealthService(session)
    report_data = await health_service.generate_health_report(current_citizen)
    return HealthReportResponse.model_validate(report_data)


@router.get("/findings/{finding_id}", response_model=HealthFindingResponse)
async def get_finding_detail(
    finding_id: uuid.UUID,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session)
) -> HealthFindingResponse:
    repo = HealthRepository(session)
    finding = await repo.get_finding_by_id(finding_id)
    if not finding or finding.citizen_id != current_citizen.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health finding not found or access forbidden."
        )

    return HealthFindingResponse(
        id=finding.id,
        rule_id=finding.rule_id,
        severity=finding.severity,
        status=finding.status,
        what_is_wrong=finding.what_is_wrong,
        why_it_happened=finding.why_it_happened,
        potential_impact=finding.potential_impact,
        correction_path=finding.correction_path,
        evidence=finding.evidence,
        detected_at=str(finding.detected_at)
    )


@router.post("/findings/{finding_id}/explain", response_model=FindingExplanation)
async def explain_finding(
    finding_id: uuid.UUID,
    current_citizen: Citizen = Depends(get_current_citizen),
    session: AsyncSession = Depends(get_db_session)
):
    """Generate an AI-powered plain-language explanation for a PF Health finding."""
    from pfcompass.ai.explainer import ai_explainer

    repo = HealthRepository(session)
    finding = await repo.get_finding_by_id(finding_id)
    if not finding or finding.citizen_id != current_citizen.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health finding not found or access forbidden."
        )

    return await ai_explainer.explain_finding(
        rule_id=finding.rule_id,
        rule_title=finding.what_is_wrong or "PF Health Finding",
        what_is_wrong=finding.what_is_wrong or "",
        why_it_happened=finding.why_it_happened or "",
        correction_path=finding.correction_path or {}
    )
