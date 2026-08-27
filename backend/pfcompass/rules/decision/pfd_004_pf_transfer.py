from typing import List
from pfcompass.rules.base import PFHealthRule, RuleContext, RuleEvidence, RuleResult


class PFD004PFTransferRule(PFHealthRule):
    """
    PFD-004: PF Account Transfer Eligibility (Form 13)
    EPF Scheme Para 57 — requires active destination account, previous source accounts, and verified KYC.
    """

    @property
    def rule_id(self) -> str:
        return "PFD-004"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def domain(self) -> str:
        return "DECISION"

    def evaluate(self, context: RuleContext) -> RuleResult:
        accounts = context.pf_accounts
        uans = context.uan_records

        is_eligible = True
        reasons: List[str] = []
        evidence: List[RuleEvidence] = []

        # Need at least 2 accounts (source + destination)
        if len(accounts) < 2:
            is_eligible = False
            reasons.append("No previous PF account detected to transfer from. At least one previous account is required.")
            evidence.append(RuleEvidence(
                field="pf_account_count",
                expected=">= 2",
                actual=str(len(accounts)),
                source="pf_accounts",
                description="At least one previous and one active account required for Form 13 transfer",
            ))

        # Need at least one active destination account
        active = [a for a in accounts if a.get("status", "").upper() == "ACTIVE"]
        if not active:
            is_eligible = False
            reasons.append("No active destination PF account found. Form 13 requires a current active employer account.")
            evidence.append(RuleEvidence(
                field="active_account_count",
                expected=">= 1",
                actual="0",
                source="pf_accounts",
                description="No active destination account available",
            ))

        # KYC must be verified on UAN
        unverified = [u for u in uans if u.get("kyc_status", "").upper() != "VERIFIED"]
        if unverified:
            is_eligible = False
            reasons.append("Aadhaar/Bank KYC is unverified on one or more UAN records.")
            evidence.append(RuleEvidence(
                field="kyc_status",
                expected="VERIFIED",
                actual="UNVERIFIED",
                source="uan_records",
                description="KYC verification required before online Form 13 transfer",
            ))

        status = "ELIGIBLE" if is_eligible else "INELIGIBLE"
        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=not is_eligible,
            severity="INFO",
            what_is_wrong="Eligible for Online PF Transfer (Form 13)." if is_eligible else "Not eligible for Form 13 PF Transfer at this time.",
            why_it_happened="Active destination account and previous source accounts identified with verified KYC." if is_eligible else "; ".join(reasons),
            potential_impact="Transferring previous PF accounts consolidates service history for pension eligibility and maintains continuous interest growth.",
            correction_path={
                "claim_type": "PF_TRANSFER",
                "form_number": "FORM-13",
                "status": status,
                "is_eligible": is_eligible,
                "reasons": reasons,
                "recommended_action": "Submit online Form 13 Transfer via EPFO Member Portal." if is_eligible else "Resolve destination account or KYC issues before initiating transfer.",
            },
            evidence=evidence,
        )
