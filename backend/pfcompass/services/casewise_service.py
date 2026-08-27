import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.casewise.next_action import get_next_actions
from pfcompass.casewise.simulator import DemoEventSimulator
from pfcompass.casewise.state_machine import CaseState, CaseStateMachine
from pfcompass.casewise.timeline_builder import TimelineBuilder
from pfcompass.models import Case, CaseEvent
from pfcompass.repositories.case_repo import CaseRepository
from pfcompass.schemas.casewise import (
    CaseCreateSchema,
    CaseDetailResponse,
    CaseEventCreate,
    CaseSummaryResponse,
    CaseTimelineSchema,
    NextActionSetSchema,
    StatusChangeSchema,
    TimelineItemSchema,
)


class CaseWiseService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CaseRepository(session)
        self.state_machine = CaseStateMachine()
        self.timeline_builder = TimelineBuilder()
        self.simulator = DemoEventSimulator()

    async def list_citizen_cases(self, citizen_id: uuid.UUID) -> List[CaseSummaryResponse]:
        cases = await self.repo.list_cases_for_citizen(citizen_id)
        result = []
        for case in cases:
            events = sorted(case.events, key=lambda x: x.occurred_at) if case.events else []
            latest_text = events[-1].what_happened if events else None
            result.append(
                CaseSummaryResponse(
                    id=case.id,
                    citizen_id=case.citizen_id,
                    case_type=case.case_type,
                    case_subtype=case.case_subtype,
                    status=case.status,
                    claim_id=case.claim_id,
                    finding_id=case.finding_id,
                    resolution_note=case.resolution_note,
                    opened_at=case.opened_at,
                    resolved_at=case.resolved_at,
                    event_count=len(events),
                    latest_event_text=latest_text,
                )
            )
        return result

    async def get_case_detail(self, citizen_id: uuid.UUID, case_id: uuid.UUID) -> Optional[CaseDetailResponse]:
        case = await self.repo.get_case_by_id(case_id, citizen_id)
        if not case:
            return None

        events = sorted(case.events, key=lambda x: x.occurred_at) if case.events else []
        timeline = self.timeline_builder.build_timeline(str(case.id), events)

        next_action_set = get_next_actions(case.case_type, case.status, case_id=str(case.id))

        timeline_schema = CaseTimelineSchema(
            case_id=timeline.case_id,
            current_status=timeline.current_status,
            total_duration_days=timeline.total_duration_days,
            items=[
                TimelineItemSchema(
                    id=item.id,
                    event_type=item.event_type,
                    occurred_at=item.occurred_at,
                    actor=item.actor,
                    actor_label=item.actor_label,
                    what_happened=item.what_happened,
                    why_it_happened=item.why_it_happened,
                    status_change=StatusChangeSchema(
                        from_status=item.status_change.from_status,
                        to_status=item.status_change.to_status,
                    ) if item.status_change else None,
                    evidence=item.evidence,
                    metadata=item.metadata,
                    is_action_required=item.is_action_required,
                )
                for item in timeline.items
            ],
        )

        next_actions_schema = NextActionSetSchema(
            primary_action=next_action_set.primary_action,
            secondary_actions=next_action_set.secondary_actions,
            estimated_wait_days=next_action_set.estimated_wait_days,
            can_citizen_act_now=next_action_set.can_citizen_act_now,
            action_url=next_action_set.action_url,
        )

        return CaseDetailResponse(
            id=case.id,
            citizen_id=case.citizen_id,
            case_type=case.case_type,
            case_subtype=case.case_subtype,
            status=case.status,
            claim_id=case.claim_id,
            finding_id=case.finding_id,
            opened_at=case.opened_at,
            resolved_at=case.resolved_at,
            resolution_note=case.resolution_note,
            timeline=timeline_schema,
            next_actions=next_actions_schema,
        )

    async def create_case(self, citizen_id: uuid.UUID, data: CaseCreateSchema) -> CaseDetailResponse:
        init_status = CaseState.OPEN.value if data.case_type.upper() == "CORRECTION" else CaseState.DRAFT.value

        case = Case(
            citizen_id=citizen_id,
            case_type=data.case_type.upper(),
            case_subtype=data.case_subtype,
            status=init_status,
            claim_id=data.claim_id,
            finding_id=data.finding_id,
        )
        created_case = await self.repo.create_case(case)

        # Initial opening event
        init_event_text = data.initial_event_text or f"Case opened for {data.case_subtype}"
        init_event = CaseEvent(
            case_id=created_case.id,
            event_type="CASE_OPENED",
            actor="SYSTEM",
            what_happened=init_event_text,
            why_it_happened="Citizen initiated new case workflow",
            new_status=init_status,
        )
        await self.repo.add_case_event(init_event)

        detail = await self.get_case_detail(citizen_id, created_case.id)
        assert detail is not None
        return detail

    async def add_event(self, citizen_id: uuid.UUID, case_id: uuid.UUID, data: CaseEventCreate) -> CaseDetailResponse:
        case = await self.repo.get_case_by_id(case_id, citizen_id)
        if not case:
            raise ValueError("Case not found or access denied")

        new_status = data.new_status or case.status
        if new_status != case.status:
            event = self.state_machine.transition(
                case=case,
                new_state=new_status,
                event_type=data.event_type,
                actor=data.actor,
                what_happened=data.what_happened,
                why_it_happened=data.why_it_happened,
                evidence=data.evidence,
                metadata_payload=data.metadata_payload,
            )
        else:
            event = CaseEvent(
                case_id=case.id,
                event_type=data.event_type,
                actor=data.actor,
                what_happened=data.what_happened,
                why_it_happened=data.why_it_happened,
                evidence=data.evidence,
                metadata_payload=data.metadata_payload,
                previous_status=case.status,
                new_status=case.status,
            )

        await self.repo.add_case_event(event, new_case_status=new_status)
        detail = await self.get_case_detail(citizen_id, case_id)
        assert detail is not None
        return detail

    async def simulate_next_step(self, citizen_id: uuid.UUID, case_id: uuid.UUID) -> CaseDetailResponse:
        case = await self.repo.get_case_by_id(case_id, citizen_id)
        if not case:
            raise ValueError("Case not found or access denied")

        sim_result = self.simulator.simulate_next_event(case.case_type, case.status)
        if not sim_result:
            raise ValueError(f"No further demo simulation steps available for case in state {case.status}")

        next_state, event_type, actor, what_happened, why_it_happened = sim_result

        event_create = CaseEventCreate(
            event_type=event_type,
            actor=actor,
            what_happened=what_happened,
            why_it_happened=why_it_happened,
            new_status=next_state.value,
        )

        return await self.add_event(citizen_id, case_id, event_create)
