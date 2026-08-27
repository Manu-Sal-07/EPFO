from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class CaseEventCreate(BaseModel):
    event_type: str
    actor: str
    what_happened: str
    why_it_happened: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    metadata_payload: Optional[Dict[str, Any]] = None
    new_status: Optional[str] = None


class StatusChangeSchema(BaseModel):
    from_status: Optional[str] = None
    to_status: Optional[str] = None


class TimelineItemSchema(BaseModel):
    id: str
    event_type: str
    occurred_at: datetime
    actor: str
    actor_label: str
    what_happened: str
    why_it_happened: Optional[str] = None
    status_change: Optional[StatusChangeSchema] = None
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_action_required: bool = False


class CaseTimelineSchema(BaseModel):
    case_id: str
    current_status: str
    items: List[TimelineItemSchema]
    total_duration_days: float


class NextActionSetSchema(BaseModel):
    primary_action: str
    secondary_actions: List[str]
    estimated_wait_days: int
    can_citizen_act_now: bool
    action_url: Optional[str] = None


class CaseCreateSchema(BaseModel):
    case_type: str  # CLAIM | CORRECTION
    case_subtype: str
    claim_id: Optional[UUID] = None
    finding_id: Optional[UUID] = None
    initial_event_text: Optional[str] = None


class CaseSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    citizen_id: UUID
    case_type: str
    case_subtype: str
    status: str
    claim_id: Optional[UUID] = None
    finding_id: Optional[UUID] = None
    resolution_note: Optional[str] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    event_count: int = 0
    latest_event_text: Optional[str] = None


class CaseDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    citizen_id: UUID
    case_type: str
    case_subtype: str
    status: str
    claim_id: Optional[UUID] = None
    finding_id: Optional[UUID] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    timeline: CaseTimelineSchema
    next_actions: NextActionSetSchema
