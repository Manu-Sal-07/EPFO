from typing import Any
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class MissingExitDateRule(PFHealthRule):
    """PFH-002: Detect missing date of exit for past employment records."""

    def __init__(self, parameters: dict[str, Any] | None = None):
        params = parameters or {}

    @property
    def rule_id(self) -> str:
        return "PFH-002"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "HEALTH"

    def evaluate(self, context: RuleContext) -> RuleResult:
        missing_exits: list[dict[str, Any]] = []

        # Find employments that have date_of_exit = None BUT are not the citizen's current employment
        # (e.g. citizen has subsequent employment records or multiple employments without exit dates)
        total_employments = len(context.employment_records)

        for idx, emp in enumerate(context.employment_records):
            date_of_exit = emp.get("date_of_exit")
            # If not the latest employment and exit date is missing
            if date_of_exit is None and idx < total_employments - 1:
                missing_exits.append(emp)

        if not missing_exits:
            return self._no_finding()

        target = missing_exits[0]

        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=True,
            severity="HIGH",
            what_is_wrong=f"Date of exit is missing for your former employer '{target.get('employer_name')}'.",
            why_it_happened="Your previous employer did not mark your date of exit in the ECR portal upon resignation.",
            potential_impact="You will be unable to process online PF withdrawal claims (Form 19) or transfers until the exit date is recorded.",
            correction_path={
                "summary": "Mark your exit date online on the EPFO Member Portal.",
                "form_numbers": ["MARK-EXIT", "JOINT-DECLARATION"],
                "estimated_days": 7,
                "steps": [
                    "Log in to EPFO Member Unified Portal.",
                    "Go to 'Manage' -> 'Mark Exit'.",
                    "Select your former employer and enter the exit date as per your relieving letter."
                ]
            },
            evidence=[
                RuleEvidence(
                    field="employment_history.date_of_exit",
                    expected="YYYY-MM-DD",
                    actual="None",
                    source=f"employment_history.id={target.get('id')}",
                    description=f"Exit date is NULL for former employment at {target.get('employer_name')}."
                )
            ],
            affected_account_ids=[],
            affected_employment_ids=[str(target.get("id"))]
        )
