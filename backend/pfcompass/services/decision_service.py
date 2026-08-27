import uuid
from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from pfcompass.decision.calculator import PFCalculationEngine
from pfcompass.decision.presubmit import PreSubmitChecker
from pfcompass.repositories.health_repo import HealthRepository
from pfcompass.rules.base import RuleContext
from pfcompass.rules.decision.pfd_001_full_withdrawal import PFD001FullWithdrawalRule
from pfcompass.rules.decision.pfd_002_partial_advance import PFD002PartialAdvanceRule
from pfcompass.rules.decision.pfd_003_pension_withdrawal import PFD003PensionWithdrawalRule
from pfcompass.rules.decision.pfd_004_pf_transfer import PFD004PFTransferRule
from pfcompass.schemas.decision import (
    CalculationResponse,
    EligibilityResultResponse,
    PreSubmitCheckItemSchema,
    PreSubmitResponse,
    RuleEvidenceSchema,
)


def _emp_to_dict(emp) -> dict:
    return {
        "employer_name": getattr(emp, "employer_name", ""),
        "date_of_joining": getattr(emp, "date_of_joining", None),
        "date_of_exit": getattr(emp, "date_of_exit", None),
    }


def _uan_to_dict(uan) -> dict:
    return {
        "uan": getattr(uan, "uan_number", ""),
        "is_primary": getattr(uan, "is_primary", True),
        "kyc_status": getattr(uan, "kyc_status", "UNVERIFIED"),
    }


def _account_to_dict(acc) -> dict:
    return {
        "id": str(getattr(acc, "id", "")),
        "status": getattr(acc, "status", ""),
        "inoperative_since": getattr(acc, "inoperative_since", None),
    }


class DecisionService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.health_repo = HealthRepository(session)
        self.calculator = PFCalculationEngine()
        self.presubmit_checker = PreSubmitChecker()

    async def _build_context(
        self,
        citizen_id: uuid.UUID,
        advance_ground: Optional[str] = None,
    ) -> tuple[RuleContext, dict]:
        records = await self.health_repo.get_citizen_records(citizen_id)

        employments = [_emp_to_dict(e) for e in records.get("employments", [])]
        uans = [_uan_to_dict(u) for u in records.get("uans", [])]
        accounts = [_account_to_dict(a) for a in records.get("accounts", [])]
        balances: dict = records.get("balances", {})

        ctx = RuleContext(
            citizen_id=str(citizen_id),
            employment_records=employments,
            pf_accounts=accounts,
            pf_balances=balances,
            uan_records=uans,
        )
        if advance_ground:
            ctx.advance_ground = advance_ground

        return ctx, balances

    async def evaluate_eligibility(
        self,
        citizen_id: uuid.UUID,
        claim_type: str,
        advance_ground: Optional[str] = None,
    ) -> EligibilityResultResponse:
        ctx, _ = await self._build_context(citizen_id, advance_ground)

        claim_type_upper = claim_type.upper()
        rule_map = {
            "FULL_WITHDRAWAL": PFD001FullWithdrawalRule,
            "PARTIAL_ADVANCE": PFD002PartialAdvanceRule,
            "PENSION_CLAIM": PFD003PensionWithdrawalRule,
            "PF_TRANSFER": PFD004PFTransferRule,
        }
        RuleClass = rule_map.get(claim_type_upper, PFD001FullWithdrawalRule)
        result = RuleClass().evaluate(ctx)
        path = result.correction_path or {}

        evidence_list = [
            RuleEvidenceSchema(
                field=e.field,
                expected=e.expected or "",
                actual=e.actual or "",
                description=e.description,
            )
            for e in result.evidence
        ]

        return EligibilityResultResponse(
            rule_id=result.rule_id,
            claim_type=path.get("claim_type", claim_type_upper),
            form_number=path.get("form_number", "FORM-19"),
            status=path.get("status", "INELIGIBLE"),
            is_eligible=path.get("is_eligible", path.get("is_withdrawal_eligible", False)),
            what_is_wrong=result.what_is_wrong or "",
            why_it_happened=result.why_it_happened or "",
            recommended_action=path.get("recommended_action", "Proceed with application"),
            reasons=path.get("reasons", []),
            evidence=evidence_list,
        )

    async def calculate_payout(
        self,
        citizen_id: uuid.UUID,
        claim_type: str = "FULL_WITHDRAWAL",
        advance_ground: Optional[str] = None,
        requested_amount: Optional[float] = None,
        has_pan: Optional[bool] = None,
    ) -> CalculationResponse:
        ctx, balances = await self._build_context(citizen_id, advance_ground)

        calc = self.calculator.calculate_payout(
            employments=ctx.employment_records,
            uans=ctx.uan_records,
            balances_map=balances,
            claim_type=claim_type,
            advance_ground=advance_ground,
            requested_amount=requested_amount,
            has_pan=has_pan,
        )

        return CalculationResponse(
            employee_share=calc.employee_share,
            employer_share=calc.employer_share,
            interest_accrued=calc.interest_accrued,
            total_balance=calc.total_balance,
            eligible_payout_amount=calc.eligible_payout_amount,
            total_service_years=calc.total_service_years,
            is_tax_free=calc.is_tax_free,
            taxability_reason=calc.taxability_reason,
            tds_rate_percent=calc.tds_rate_percent,
            estimated_tds_amount=calc.estimated_tds_amount,
            form_15g_applicable=calc.form_15g_applicable,
            form_15g_recommendation=calc.form_15g_recommendation,
        )

    async def run_presubmit_audit(
        self,
        citizen_id: uuid.UUID,
        claim_type: str = "FULL_WITHDRAWAL",
    ) -> PreSubmitResponse:
        ctx, _ = await self._build_context(citizen_id)

        audit = self.presubmit_checker.audit_claim_readiness(
            uans=ctx.uan_records,
            employments=ctx.employment_records,
            claim_type=claim_type,
        )

        return PreSubmitResponse(
            is_ready_to_submit=audit.is_ready_to_submit,
            readiness_score=audit.readiness_score,
            total_checks=audit.total_checks,
            passed_checks=audit.passed_checks,
            blocking_issues_count=audit.blocking_issues_count,
            check_items=[
                PreSubmitCheckItemSchema(
                    check_id=item.check_id,
                    title=item.title,
                    description=item.description,
                    status=item.status,
                    is_blocking=item.is_blocking,
                    remediation_hint=item.remediation_hint,
                )
                for item in audit.check_items
            ],
        )
