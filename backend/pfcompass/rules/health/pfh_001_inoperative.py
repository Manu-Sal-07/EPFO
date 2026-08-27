from datetime import date
from typing import Any
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class InoperativeAccountRule(PFHealthRule):
    """PFH-001: Detect inoperative PF accounts (>36 months inactive post exit)."""

    def __init__(self, parameters: dict[str, Any] | None = None):
        params = parameters or {}
        self._threshold_months: int = params.get("inoperative_threshold_months", 36)

    @property
    def rule_id(self) -> str:
        return "PFH-001"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "HEALTH"

    def evaluate(self, context: RuleContext) -> RuleResult:
        findings: list[dict[str, Any]] = []

        for account in context.pf_accounts:
            account_id = str(account.get("id", ""))
            status = str(account.get("status", "")).upper()
            employment_id = str(account.get("employment_id", ""))

            # Match employment
            employment = next(
                (emp for emp in context.employment_records if str(emp.get("id", "")) == employment_id),
                None
            )
            if not employment:
                continue

            date_of_exit = employment.get("date_of_exit")
            # If account status is explicitly marked INOPERATIVE or exit date > threshold months
            is_explicit = (status == "INOPERATIVE")

            months_inactive = 0
            if date_of_exit:
                if isinstance(date_of_exit, str):
                    date_of_exit = date.fromisoformat(date_of_exit)
                months_inactive = (context.evaluation_date.year - date_of_exit.year) * 12 + (context.evaluation_date.month - date_of_exit.month)

            if is_explicit or (date_of_exit and months_inactive >= self._threshold_months and status not in ("SETTLED", "TRANSFERRED")):
                findings.append({
                    "account": account,
                    "employment": employment,
                    "months_inactive": months_inactive,
                    "is_explicit": is_explicit
                })

        if not findings:
            return self._no_finding()

        worst = max(findings, key=lambda f: f["months_inactive"])
        acc = worst["account"]
        emp = worst["employment"]

        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=True,
            severity="HIGH",
            what_is_wrong=f"Your PF account with member ID {acc.get('member_id')} ({emp.get('employer_name')}) is inoperative.",
            why_it_happened=f"No contributions or transfer request occurred for over {worst['months_inactive']} months after resignation.",
            potential_impact="Inoperative PF accounts stop earning compound interest and require offline verification for withdrawal.",
            correction_path={
                "summary": "Transfer or withdraw the balance in this inoperative account.",
                "form_numbers": ["FORM-13", "FORM-19"],
                "estimated_days": 15,
                "steps": [
                    "Log in to EPFO Member Unified Portal.",
                    "Submit Form 13 to transfer the balance to your active UAN account.",
                    "Or submit Form 19 for online withdrawal."
                ]
            },
            evidence=[
                RuleEvidence(
                    field="pf_account.status",
                    expected="ACTIVE or TRANSFERRED",
                    actual=str(acc.get("status")),
                    source=f"pf_accounts.id={acc.get('id')}",
                    description=f"Account status is {acc.get('status')} after {worst['months_inactive']} months of inactivity."
                )
            ],
            affected_account_ids=[str(acc.get("id"))],
            affected_employment_ids=[str(emp.get("id"))]
        )
