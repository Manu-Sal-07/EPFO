from datetime import date
from typing import List
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class PFD001FullWithdrawalRule(PFHealthRule):
    """
    PFD-001: Full PF Withdrawal Eligibility (Form 19)
    EPF Scheme Para 69 — citizen must have left service and waited 2 months.
    """

    @property
    def rule_id(self) -> str:
        return "PFD-001"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "DECISION"

    def evaluate(self, context: RuleContext) -> RuleResult:
        employments = context.employment_records
        evidence: List[RuleEvidence] = []
        is_eligible = True
        reasons: List[str] = []

        # 1. Check for active (no exit date) employment
        active = [e for e in employments if not e.get("date_of_exit")]
        if active:
            is_eligible = False
            reasons.append(
                f"Currently employed at {active[0].get('employer_name', 'unknown')}. "
                "Full withdrawal (Form 19) is permitted only after leaving service."
            )
            evidence.append(RuleEvidence(
                field="employment_status",
                expected="NOT_ACTIVE",
                actual="ACTIVE",
                source="employment_records",
                description="Active employment found",
            ))

        # 2. Enforce 60-day waiting period post-exit
        today = date.today()
        for emp in employments:
            exit_str = emp.get("date_of_exit")
            if exit_str:
                exit_d = exit_str if isinstance(exit_str, date) else date.fromisoformat(str(exit_str))
                days = (today - exit_d).days
                if days < 60:
                    is_eligible = False
                    reasons.append(
                        f"Only {days} days elapsed since exit from {emp.get('employer_name', 'employer')}. "
                        "A 2-month (60-day) unemployment period is required."
                    )
                    evidence.append(RuleEvidence(
                        field="days_since_exit",
                        expected=">= 60",
                        actual=str(days),
                        source="employment_records",
                        description="Mandatory 2-month waiting period not fulfilled",
                    ))

        status = "ELIGIBLE" if is_eligible else "INELIGIBLE"
        form_number = "FORM-19"

        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=not is_eligible,
            severity="INFO",
            what_is_wrong="Eligible for Full PF Withdrawal (Form 19)." if is_eligible else "Not eligible for Full PF Withdrawal.",
            why_it_happened="All EPF Scheme Para 69 conditions satisfied." if is_eligible else "; ".join(reasons),
            potential_impact="Full PF withdrawal pays out accumulated employee + employer shares with applicable interest.",
            correction_path={
                "claim_type": "FULL_WITHDRAWAL",
                "form_number": form_number,
                "status": status,
                "is_eligible": is_eligible,
                "reasons": reasons,
                "recommended_action": "Submit Form 19 via EPFO Unified Member Portal" if is_eligible else "Resolve eligibility blockers or apply for PF Transfer (Form 13).",
            },
            evidence=evidence,
        )
