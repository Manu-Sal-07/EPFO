import uuid
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pfcompass.models import Case, CaseEvent


class CaseRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_cases_for_citizen(self, citizen_id: uuid.UUID) -> Sequence[Case]:
        stmt = (
            select(Case)
            .where(Case.citizen_id == citizen_id)
            .options(selectinload(Case.events))
            .order_by(Case.created_at.desc())
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def get_case_by_id(self, case_id: uuid.UUID, citizen_id: Optional[uuid.UUID] = None) -> Optional[Case]:
        stmt = (
            select(Case)
            .where(Case.id == case_id)
            .options(selectinload(Case.events))
        )
        if citizen_id:
            stmt = stmt.where(Case.citizen_id == citizen_id)
        return (await self.session.execute(stmt)).scalars().first()

    async def create_case(self, case: Case) -> Case:
        self.session.add(case)
        await self.session.commit()
        await self.session.refresh(case)
        return case

    async def add_case_event(self, event: CaseEvent, new_case_status: Optional[str] = None) -> CaseEvent:
        self.session.add(event)

        if new_case_status:
            case = await self.get_case_by_id(event.case_id)
            if case:
                case.status = new_case_status
                if new_case_status in ("CLOSED", "SETTLED", "RESOLVED", "WITHDRAWN", "REJECTED"):
                    from datetime import datetime, timezone
                    case.resolved_at = datetime.now(timezone.utc)
                self.session.add(case)

        await self.session.commit()
        await self.session.refresh(event)
        return event
