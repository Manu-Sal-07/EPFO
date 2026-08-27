import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.models import Citizen, AuthCredential


class CitizenRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, citizen_id: uuid.UUID) -> Optional[Citizen]:
        result = await self.session.execute(
            select(Citizen).where(Citizen.id == citizen_id, Citizen.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Citizen]:
        result = await self.session.execute(
            select(Citizen).where(Citizen.email == email.lower().strip(), Citizen.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create_citizen(
        self,
        display_name: str,
        email: str,
        password_hash: str,
        is_demo: bool = True
    ) -> Citizen:
        citizen = Citizen(
            display_name=display_name,
            email=email.lower().strip(),
            is_demo=is_demo
        )
        self.session.add(citizen)
        await self.session.flush()

        auth_cred = AuthCredential(
            citizen_id=citizen.id,
            password_hash=password_hash
        )
        self.session.add(auth_cred)
        await self.session.commit()
        await self.session.refresh(citizen)
        return citizen
