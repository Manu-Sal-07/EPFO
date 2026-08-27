from typing import Any
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class KYCMismatchRule(PFHealthRule):
    """PFH-007: Detect unverified or missing KYC details on citizen UAN."""

    def __init__(self, parameters: dict[str, Any] | None = None):
        params = parameters or {}

    @property
    def rule_id(self) -> str:
        return "PFH-007"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "HEALTH"

    def evaluate(self, context: RuleContext) -> RuleResult:
        unverified_uans: list[dict[str, Any]] = []

        for uan_rec in context.uan_records:
            kyc_status = str(uan_rec.get("kyc_status", "")).upper()
            if kyc_status != "VERIFIED":
                unverified_uans.append(uan_rec)

        if not unverified_uans:
            return self._no_finding()

        target = unverified_uans[0]

        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=True,
            severity="HIGH",
            what_is_wrong=f"KYC status for UAN {target.get('uan')} is currently {target.get('kyc_status')}.",
            why_it_happened="Aadhaar, PAN, or Bank Details have either not been uploaded or are pending employer verification.",
            potential_impact="All online claim submissions (Form 19, 31, 10C) require fully verified KYC.",
            correction_path={
                "summary": "Upload and verify KYC documents on EPFO Member Portal.",
                "form_numbers": ["KYC-UPDATE"],
                "estimated_days": 10,
                "steps": [
                    "Log in to EPFO Member Unified Portal.",
                    "Go to 'Manage' -> 'KYC' and upload your Aadhaar and Bank Details.",
                    "Request employer to approve the pending KYC using their DSC."
                ]
            },
            evidence=[
                RuleEvidence(
                    field="uan_records.kyc_status",
                    expected="VERIFIED",
                    actual=str(target.get("kyc_status")),
                    source=f"uan_records.id={target.get('id')}",
                    description=f"UAN {target.get('uan')} has KYC status {target.get('kyc_status')}."
                )
            ],
            affected_account_ids=[],
            affected_employment_ids=[]
        )
