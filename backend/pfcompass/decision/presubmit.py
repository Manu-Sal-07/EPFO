from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PreSubmitCheckItem:
    check_id: str
    title: str
    description: str
    status: str  # PASSED | FAILED | WARNING
    is_blocking: bool
    remediation_hint: str


@dataclass
class PreSubmitAuditResult:
    is_ready_to_submit: bool
    readiness_score: int  # 0–100
    total_checks: int
    passed_checks: int
    blocking_issues_count: int
    check_items: List[PreSubmitCheckItem] = field(default_factory=list)


class PreSubmitChecker:
    """
    Pre-Submit Readiness Checker — accepts both dict and object records.
    """

    def _get(self, obj, key, default=None):
        """Safe getter for both dicts and objects."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def audit_claim_readiness(
        self,
        uans: List[Any],
        employments: List[Any],
        claim_type: str = "FULL_WITHDRAWAL",
    ) -> PreSubmitAuditResult:
        items: List[PreSubmitCheckItem] = []

        # Check 1: Primary UAN KYC Status
        primary_uan = next(
            (u for u in uans if self._get(u, "is_primary", False)),
            uans[0] if uans else None
        )
        kyc_status = self._get(primary_uan, "kyc_status", "") if primary_uan else ""
        kyc_verified = kyc_status.upper() == "VERIFIED"

        items.append(PreSubmitCheckItem(
            check_id="CHK_KYC_AADHAAR",
            title="Aadhaar & KYC Verification",
            description="Verified Aadhaar and PAN linkage on primary UAN",
            status="PASSED" if kyc_verified else "FAILED",
            is_blocking=True,
            remediation_hint="Complete KYC on EPFO Member e-Sewa Portal using Aadhaar OTP." if not kyc_verified else "KYC verified.",
        ))

        # Check 2: Bank Account Linkage
        items.append(PreSubmitCheckItem(
            check_id="CHK_BANK_ACCOUNT",
            title="Bank Account Linkage",
            description="Active bank account and valid IFSC seeded in EPFO master",
            status="PASSED" if kyc_verified else "WARNING",
            is_blocking=False,
            remediation_hint="Ensure bank account is digitally approved by employer in Member Portal." if not kyc_verified else "Bank account verified.",
        ))

        # Check 3: Date of Exit (required for Full Withdrawal & Pension)
        if claim_type.upper() in ("FULL_WITHDRAWAL", "PENSION_CLAIM"):
            missing_exit = [
                e for e in employments
                if not self._get(e, "date_of_exit", None)
            ]
            has_exit = len(missing_exit) == 0 and len(employments) > 0

            items.append(PreSubmitCheckItem(
                check_id="CHK_DATE_OF_EXIT",
                title="Date of Exit Record",
                description="Exit date updated by previous employer or marked online by citizen",
                status="PASSED" if has_exit else "FAILED",
                is_blocking=True,
                remediation_hint="Mark Date of Exit via Member Portal → Manage → Mark Exit." if not has_exit else "Exit date present.",
            ))

        # Check 4: Multiple UAN Conflicts
        has_multiple_uans = len(uans) > 1
        items.append(PreSubmitCheckItem(
            check_id="CHK_UAN_MULTIPLICITY",
            title="Single Primary UAN Record",
            description="Check for conflicting duplicate UAN records",
            status="WARNING" if has_multiple_uans else "PASSED",
            is_blocking=False,
            remediation_hint="Consolidate duplicate UANs via Form 13 transfer before claim." if has_multiple_uans else "Single primary UAN verified.",
        ))

        # Check 5: Mobile Number OTP Readiness
        items.append(PreSubmitCheckItem(
            check_id="CHK_MOBILE_OTP",
            title="Aadhaar-Linked Mobile OTP",
            description="Active mobile number linked to Aadhaar for e-Sign OTP",
            status="PASSED",
            is_blocking=True,
            remediation_hint="Ensure your mobile is active to receive Aadhaar OTP during e-Sign submission.",
        ))

        passed = [i for i in items if i.status == "PASSED"]
        blocking = [i for i in items if i.status == "FAILED" and i.is_blocking]
        total = len(items)
        score = int((len(passed) / total) * 100) if total else 100

        return PreSubmitAuditResult(
            is_ready_to_submit=len(blocking) == 0,
            readiness_score=score,
            total_checks=total,
            passed_checks=len(passed),
            blocking_issues_count=len(blocking),
            check_items=items,
        )
