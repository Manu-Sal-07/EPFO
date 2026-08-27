import uuid
from typing import Any, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.models import EmploymentHistory, HealthFinding, PFAccount, PFBalanceSnapshot, RuleVersion, UANRecord


class HealthRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_citizen_records(self, citizen_id: uuid.UUID) -> dict[str, Sequence[Any]]:
        """Fetch all records associated with a citizen for rule evaluation."""
        e_stmt = select(EmploymentHistory).where(EmploymentHistory.citizen_id == citizen_id)
        employments = (await self.session.execute(e_stmt)).scalars().all()

        u_stmt = select(UANRecord).where(UANRecord.citizen_id == citizen_id)
        uans = (await self.session.execute(u_stmt)).scalars().all()

        p_stmt = select(PFAccount).where(PFAccount.citizen_id == citizen_id)
        accounts = (await self.session.execute(p_stmt)).scalars().all()

        balances_map: dict[str, dict[str, Any]] = {}
        for acc in accounts:
            b_stmt = (
                select(PFBalanceSnapshot)
                .where(PFBalanceSnapshot.pf_account_id == acc.id)
                .order_by(PFBalanceSnapshot.snapshot_date.desc())
            )
            bal = (await self.session.execute(b_stmt)).scalars().first()
            if bal:
                balances_map[str(acc.id)] = {
                    "employee_share": float(bal.employee_share),
                    "employer_share": float(bal.employer_share),
                    "interest_accrued": float(bal.interest_accrued),
                    "total_balance": float(bal.total_balance),
                    "snapshot_date": str(bal.snapshot_date)
                }

        return {
            "employments": employments,
            "uans": uans,
            "accounts": accounts,
            "balances": balances_map
        }

    async def get_rule_version(self, rule_id: str) -> RuleVersion | None:
        stmt = select(RuleVersion).where(RuleVersion.rule_id == rule_id, RuleVersion.is_active.is_(True))
        return (await self.session.execute(stmt)).scalars().first()

    async def get_open_findings(self, citizen_id: uuid.UUID) -> Sequence[HealthFinding]:
        stmt = select(HealthFinding).where(HealthFinding.citizen_id == citizen_id, HealthFinding.status != "RESOLVED")
        return (await self.session.execute(stmt)).scalars().all()

    async def get_finding_by_id(self, finding_id: uuid.UUID) -> HealthFinding | None:
        stmt = select(HealthFinding).where(HealthFinding.id == finding_id)
        return (await self.session.execute(stmt)).scalars().first()

    async def save_findings(self, findings: list[HealthFinding]) -> None:
        self.session.add_all(findings)
        await self.session.commit()
