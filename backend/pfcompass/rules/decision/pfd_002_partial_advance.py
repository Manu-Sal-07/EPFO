from datetime import date
from typing import List
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class PFD002PartialAdvanceRule(PFHealthRule):
    """
    PFD-002: Partial Withdrawal / Advance Eligibility (Form 31)
    EPF Scheme Para 68 grounds: ILLNESS, MARRIAGE, EDUCATION, HOUSE, PANDEMIC.
    """

    ADVANCE_GROUNDS = {
        "ILLNESS":    {"min_years": 0, "para": "68J", "description": "Medical treatment for self or family"},
        "MARRIAGE":   {"min_years": 7, "para": "68K", "description": "Marriage of self, children, or siblings"},
        "EDUCATION":  {"min_years": 7, "para": "68K", "description": "Post-matriculation education of children"},
        "HOUSE":      {"min_years": 5, "para": "68B", "description": "Purchase or construction of residential property"},
        "PANDEMIC":   {"min_years": 0, "para": "68L", "description": "Non-refundable pandemic/outbreak advance"},
    }

    @property
    def rule_id(self) -> str:
        return "PFD-002"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "DECISION"

    def evaluate(self, context: RuleContext) -> RuleResult:
        employments = context.employment_records
        requested_ground = getattr(context, "advance_ground", "ILLNESS").upper()
        ground_info = self.ADVANCE_GROUNDS.get(requested_ground, self.ADVANCE_GROUNDS["ILLNESS"])

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
        min_years = ground_info["min_years"]
        is_eligible = total_service_years >= min_years

        reasons = []
        if not is_eligible:
            reasons.append(
                f"'{requested_ground}' advance requires >= {min_years} years of service. "
                f"Calculated service: {total_service_years} years."
            )

        evidence = [RuleEvidence(
            field="total_service_years",
            expected=f">= {min_years} years",
            actual=f"{total_service_years} years",
            source="employment_records",
            description=f"Para {ground_info['para']} — {ground_info['description']}",
        )]

        status = "ELIGIBLE" if is_eligible else "INELIGIBLE"
        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=not is_eligible,
            severity="INFO",
            what_is_wrong=f"Eligible for Partial Advance (Form 31 Para {ground_info['para']})." if is_eligible else f"Ineligible for '{requested_ground}' advance.",
            why_it_happened=ground_info["description"] if is_eligible else "; ".join(reasons),
            potential_impact="PF advance is non-refundable and credited directly to your bank account without exiting service.",
            correction_path={
                "claim_type": "PARTIAL_ADVANCE",
                "form_number": "FORM-31",
                "status": status,
                "advance_ground": requested_ground,
                "para_code": ground_info["para"],
                "is_eligible": is_eligible,
                "total_service_years": total_service_years,
                "reasons": reasons,
                "recommended_action": "Submit Form 31 via Member Portal" if is_eligible else "Try ILLNESS ground (Para 68J) which requires 0 years minimum service.",
            },
            evidence=evidence,
        )
