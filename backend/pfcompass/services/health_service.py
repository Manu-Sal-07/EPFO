import uuid
from datetime import date
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.models import Citizen, HealthFinding
from pfcompass.repositories.health_repo import HealthRepository
from pfcompass.rules.base import RuleContext, RuleResult
from pfcompass.rules.engine import RuleRegistry


class HealthService:
    """Service handling PF Health evaluations and reports."""

    def __init__(self, session: AsyncSession):
        self.repo = HealthRepository(session)
        self.registry = RuleRegistry()

    async def generate_health_report(self, citizen: Citizen) -> dict[str, Any]:
        """
        Evaluate all active PF Health rules for a citizen.
        Calculates health score (100 base, deductions based on finding severity).
        Returns existing open findings or fresh evaluated findings.
        """
        records = await self.repo.get_citizen_records(citizen.id)

        # Transform ORM models into context dicts for rule engine
        emp_dicts = [
            {
                "id": str(e.id),
                "employer_name": e.employer_name,
                "date_of_joining": e.date_of_joining,
                "date_of_exit": e.date_of_exit,
                "exit_reason": e.exit_reason
            }
            for e in records["employments"]
        ]
        uan_dicts = [
            {
                "id": str(u.id),
                "uan": u.uan,
                "is_primary": u.is_primary,
                "kyc_status": u.kyc_status
            }
            for u in records["uans"]
        ]
        acc_dicts = [
            {
                "id": str(a.id),
                "employment_id": str(a.employment_id),
                "member_id": a.member_id,
                "status": a.status,
                "inoperative_since": a.inoperative_since
            }
            for a in records["accounts"]
        ]

        context = RuleContext(
            citizen_id=str(citizen.id),
            employment_records=emp_dicts,
            pf_accounts=acc_dicts,
            pf_balances=records["balances"],
            uan_records=uan_dicts,
            evaluation_date=date.today()
        )

        rule_results: list[RuleResult] = self.registry.evaluate_health(context)

        # Check existing findings in DB to prevent duplicates
        existing_findings = await self.repo.get_open_findings(citizen.id)
        existing_rule_ids = {f.rule_id for f in existing_findings}

        new_findings_to_save: list[HealthFinding] = []
        for res in rule_results:
            if res.rule_id not in existing_rule_ids:
                rule_ver = await self.repo.get_rule_version(res.rule_id)
                if not rule_ver:
                    continue
                new_finding = HealthFinding(
                    id=uuid.uuid4(),
                    citizen_id=citizen.id,
                    pf_account_id=uuid.UUID(res.affected_account_ids[0]) if res.affected_account_ids else None,
                    employment_id=uuid.UUID(res.affected_employment_ids[0]) if res.affected_employment_ids else None,
                    rule_version_id=rule_ver.id,
                    rule_id=res.rule_id,
                    severity=res.severity or "MEDIUM",
                    status="OPEN",
                    what_is_wrong=res.what_is_wrong or "",
                    why_it_happened=res.why_it_happened or "",
                    potential_impact=res.potential_impact or "",
                    correction_path=res.correction_path or {},
                    evidence=[
                        {
                            "field": e.field,
                            "expected": e.expected,
                            "actual": e.actual,
                            "source": e.source,
                            "description": e.description
                        }
                        for e in res.evidence
                    ]
                )
                new_findings_to_save.append(new_finding)

        if new_findings_to_save:
            await self.repo.save_findings(new_findings_to_save)

        # Refetch all active findings
        all_open = await self.repo.get_open_findings(citizen.id)

        # Compute PF Health Score
        # Start at 100
        # CRITICAL: -35, HIGH: -20, MEDIUM: -10, LOW: -5
        score = 100
        for f in all_open:
            if f.severity == "CRITICAL":
                score -= 35
            elif f.severity == "HIGH":
                score -= 20
            elif f.severity == "MEDIUM":
                score -= 10
            elif f.severity == "LOW":
                score -= 5

        score = max(0, min(100, score))

        status_text = "HEALTHY"
        if score < 50:
            status_text = "ACTION_REQUIRED"
        elif score < 80:
            status_text = "ATTENTION_NEEDED"

        # Calculate Total Balance across accounts
        total_balance = sum(b.get("total_balance", 0) for b in records["balances"].values())

        return {
            "citizen_id": str(citizen.id),
            "display_name": citizen.display_name,
            "health_score": score,
            "health_status": status_text,
            "total_balance": total_balance,
            "total_accounts": len(records["accounts"]),
            "findings": [
                {
                    "id": str(f.id),
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "status": f.status,
                    "what_is_wrong": f.what_is_wrong,
                    "why_it_happened": f.why_it_happened,
                    "potential_impact": f.potential_impact,
                    "correction_path": f.correction_path,
                    "evidence": f.evidence,
                    "detected_at": str(f.detected_at)
                }
                for f in all_open
            ]
        }
