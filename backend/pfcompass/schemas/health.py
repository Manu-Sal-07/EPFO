import uuid
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class HealthFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rule_id: str
    severity: str
    status: str
    what_is_wrong: str
    why_it_happened: Optional[str]
    potential_impact: str
    correction_path: dict[str, Any]
    evidence: list[dict[str, Any]]
    detected_at: str


class HealthReportResponse(BaseModel):
    citizen_id: str
    display_name: str
    health_score: int
    health_status: str
    total_balance: float
    total_accounts: int
    findings: list[HealthFindingResponse]
