from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional


@dataclass
class CalculationBreakdown:
    employee_share: float
    employer_share: float
    interest_accrued: float
    total_balance: float
    eligible_payout_amount: float
    total_service_years: float
    is_tax_free: bool
    taxability_reason: str
    tds_rate_percent: float
    estimated_tds_amount: float
    form_15g_applicable: bool
    form_15g_recommendation: str


class PFCalculationEngine:
    """
    Deterministic calculation engine for PF payouts, tax exemptions, and TDS computations.
    Grounded in Income Tax Act Sec 192A / 10(12) and EPF Scheme rules.
    """

    def calculate_payout(
        self,
        employments: List[Any],
        uans: List[Any],
        balances_map: Dict[str, Dict[str, Any]],
        claim_type: str = "FULL_WITHDRAWAL",
        advance_ground: Optional[str] = None,
        requested_amount: Optional[float] = None,
        has_pan: Optional[bool] = None,
    ) -> CalculationBreakdown:
        
        # 1. Sum balances across accounts
        total_employee_share = 0.0
        total_employer_share = 0.0
        total_interest = 0.0
        total_balance = 0.0

        for acc_id, bal in balances_map.items():
            total_employee_share += bal.get("employee_share", 0.0)
            total_employer_share += bal.get("employer_share", 0.0)
            total_interest += bal.get("interest_accrued", 0.0)
            total_balance += bal.get("total_balance", 0.0)

        # Fallback if balances_map empty
        if total_balance == 0.0 and balances_map:
            total_balance = total_employee_share + total_employer_share + total_interest

        # 2. Total service years — handle both dicts and ORM objects
        total_days = 0
        today = date.today()
        for emp in employments:
            if isinstance(emp, dict):
                doj = emp.get("date_of_joining")
                doe = emp.get("date_of_exit") or today
            else:
                doj = getattr(emp, "date_of_joining", None)
                doe = getattr(emp, "date_of_exit", None) or today
            if doj:
                if isinstance(doj, str):
                    doj = date.fromisoformat(doj)
                if isinstance(doe, str):
                    doe = date.fromisoformat(doe)
                total_days += (doe - doj).days

        total_service_years = round(total_days / 365.25, 1)

        # 3. Determine eligible payout based on claim type
        max_eligible = total_balance
        if claim_type.upper() == "PARTIAL_ADVANCE":
            ground = (advance_ground or "ILLNESS").upper()
            if ground == "ILLNESS":
                # Up to 6 months basic wages or employee share
                max_eligible = min(total_balance, total_employee_share * 0.9)
            elif ground in ("MARRIAGE", "EDUCATION"):
                # Up to 50% of employee share
                max_eligible = total_employee_share * 0.5
            elif ground == "HOUSE":
                # Up to 36 months basic wages or total balance
                max_eligible = min(total_balance, (total_employee_share + total_employer_share) * 0.9)
            elif ground == "PANDEMIC":
                # Up to 75% of total balance
                max_eligible = total_balance * 0.75

        if requested_amount is not None and requested_amount > 0:
            eligible_payout = min(requested_amount, max_eligible)
        else:
            eligible_payout = max_eligible

        # 4. Tax Exemption & TDS Computation
        if has_pan is not None:
            is_pan_verified = has_pan
        else:
            is_pan_verified = any(
                (u.get("kyc_status") if isinstance(u, dict) else getattr(u, "kyc_status", "")).upper() == "VERIFIED"
                for u in uans
            )

        if total_service_years >= 5.0:
            is_tax_free = True
            taxability_reason = "100% Tax-Exempt under Income Tax Act Sec 10(12) (Continuous service >= 5 years)."
            tds_rate = 0.0
            tds_amount = 0.0
            form_15g = False
            form_15g_rec = "Form 15G not required. Entire payout is tax-free."
        else:
            # Service < 5 years
            if eligible_payout < 50000:
                is_tax_free = False
                taxability_reason = "Service < 5 years, but payout amount is below ₹50,000 threshold. No TDS deducted by EPFO, but income must be reported in ITR."
                tds_rate = 0.0
                tds_amount = 0.0
                form_15g = False
                form_15g_rec = "Form 15G not required as payout is under ₹50,000."
            else:
                is_tax_free = False
                if is_pan_verified:
                    tds_rate = 10.0
                    tds_amount = eligible_payout * 0.10
                    taxability_reason = f"Service < 5 years and payout >= ₹50,000. TDS @ 10% (₹{tds_amount:,.2f}) applies under Sec 192A."
                    form_15g = True
                    form_15g_rec = "Upload Form 15G/15H to claim 0% TDS if your total annual taxable income is below the exemption limit."
                else:
                    tds_rate = 20.0
                    tds_amount = eligible_payout * 0.20
                    taxability_reason = f"Service < 5 years, payout >= ₹50,000, and PAN is unverified. Maximum marginal TDS @ 20% (₹{tds_amount:,.2f}) applies."
                    form_15g = True
                    form_15g_rec = "Verify PAN immediately on Member Portal to reduce TDS from 20% to 10%, or upload Form 15G."

        return CalculationBreakdown(
            employee_share=round(total_employee_share, 2),
            employer_share=round(total_employer_share, 2),
            interest_accrued=round(total_interest, 2),
            total_balance=round(total_balance, 2),
            eligible_payout_amount=round(eligible_payout, 2),
            total_service_years=total_service_years,
            is_tax_free=is_tax_free,
            taxability_reason=taxability_reason,
            tds_rate_percent=tds_rate,
            estimated_tds_amount=round(tds_amount, 2),
            form_15g_applicable=form_15g,
            form_15g_recommendation=form_15g_rec,
        )
