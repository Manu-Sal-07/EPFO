from datetime import date
from typing import List
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class PFD003PensionWithdrawalRule(PFHealthRule):
    """
    PFD-003: Pension Withdrawal vs Scheme Certificate Eligibility (Form 10C / Form 10D)
    EPS 1995 — service >= 10 years blocks lump sum, unlocks monthly pension (Form 10D).
    """

    @property
    def rule_id(self) -> str:
        return "PFD-003"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "DECISION"

    def evaluate(self, context: RuleContext) -> RuleResult:
        employments = context.employment_records

        today = date.today()
        total_days = 0
        for emp in employments:
            doj = emp.get("date_of_joining")
            doe = emp.get("date_of_exit") or today
            if doj:
                if isinstance(doj, str):
                    doj = date.fromisoformat(doj)
                if isinstance(doe, str):
                    doe = date.fromisoformat(doe)
                total_days += (doe - doj).days

        total_service_years = round(total_days / 365.25, 1)
        active = [e for e in employments if not e.get("date_of_exit")]

        reasons: List[str] = []
        is_withdrawal_eligible = True

        if active:
            is_withdrawal_eligible = False
            reasons.append("Currently in active service. Pension withdrawal can only be claimed after leaving service.")

        if total_service_years >= 10.0:
            is_withdrawal_eligible = False
            reasons.append(
                f"Total service ({total_service_years} yrs) >= 10 years. Under EPS 1995, "
                "lump sum withdrawal is disallowed. You are eligible for a Scheme Certificate / monthly pension (Form 10D)."
            )
            form_number = "FORM-10D_SCHEME_CERT"
            recommendation = "Apply for Scheme Certificate (Form 10C) to preserve pension entitlement until age 58."
            status = "CONDITIONALLY_ELIGIBLE"
        else:
            form_number = "FORM-10C"
            recommendation = "Apply for Pension Withdrawal Benefit lump sum (Form 10C)."
            status = "ELIGIBLE" if is_withdrawal_eligible else "INELIGIBLE"

        if active and total_service_years < 10.0:
            status = "INELIGIBLE"

        evidence = [RuleEvidence(
            field="total_service_years",
            expected="< 10 years for withdrawal benefit",
            actual=f"{total_service_years} years",
            source="employment_records",
            description="EPS 1995 10-year threshold evaluation",
        )]

        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=not is_withdrawal_eligible,
            severity="INFO",
            what_is_wrong="Eligible for Pension Withdrawal Benefit (Form 10C)." if is_withdrawal_eligible else "Eligible for Scheme Certificate instead of lump sum withdrawal.",
            why_it_happened="Service < 10 years and exit marked." if is_withdrawal_eligible else "; ".join(reasons),
            potential_impact="Pension lump sum calculated using EPS 1995 Table D matrix based on service years and pensionable salary.",
            correction_path={
                "claim_type": "PENSION_CLAIM",
                "form_number": form_number,
                "status": status,
                "is_withdrawal_eligible": is_withdrawal_eligible,
                "total_service_years": total_service_years,
                "reasons": reasons,
                "recommended_action": recommendation,
            },
            evidence=evidence,
        )
