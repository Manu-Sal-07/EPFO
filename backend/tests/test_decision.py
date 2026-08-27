from datetime import date, timedelta
import pytest
from pfcompass.decision.calculator import PFCalculationEngine
from pfcompass.decision.presubmit import PreSubmitChecker
from pfcompass.rules.base import RuleContext
from pfcompass.rules.decision.pfd_001_full_withdrawal import PFD001FullWithdrawalRule
from pfcompass.rules.decision.pfd_002_partial_advance import PFD002PartialAdvanceRule
from pfcompass.rules.decision.pfd_003_pension_withdrawal import PFD003PensionWithdrawalRule
from pfcompass.rules.decision.pfd_004_pf_transfer import PFD004PFTransferRule


def make_emp(employer_name, doj, doe):
    return {"employer_name": employer_name, "date_of_joining": doj, "date_of_exit": doe}


def make_uan(uan, is_primary=True, kyc_status="VERIFIED"):
    return {"uan": uan, "is_primary": is_primary, "kyc_status": kyc_status}


def make_account(status="ACTIVE", inoperative_since=None):
    return {"status": status, "inoperative_since": inoperative_since}


def make_context(employments=None, accounts=None, uans=None, balances=None, advance_ground=None):
    ctx = RuleContext(
        citizen_id="test-citizen-001",
        employment_records=employments or [],
        pf_accounts=accounts or [],
        pf_balances=balances or {},
        uan_records=uans or [],
    )
    if advance_ground:
        ctx.advance_ground = advance_ground
    return ctx


# ── PFD-001: Full Withdrawal ──────────────────────────────────────────────────

def test_pfd001_full_withdrawal_active_employment():
    rule = PFD001FullWithdrawalRule()
    emp = make_emp("Acme Corp", date(2020, 1, 1), None)  # No exit → active
    ctx = make_context(employments=[emp])
    result = rule.evaluate(ctx)
    assert not result.correction_path["is_eligible"]
    assert result.correction_path["status"] == "INELIGIBLE"


def test_pfd001_full_withdrawal_eligible():
    rule = PFD001FullWithdrawalRule()
    exit_d = date.today() - timedelta(days=90)
    emp = make_emp("Acme Corp", date(2018, 1, 1), exit_d)
    ctx = make_context(employments=[emp])
    result = rule.evaluate(ctx)
    assert result.correction_path["is_eligible"]
    assert result.correction_path["status"] == "ELIGIBLE"


def test_pfd001_waiting_period_not_met():
    rule = PFD001FullWithdrawalRule()
    recent_exit = date.today() - timedelta(days=30)
    emp = make_emp("Acme Corp", date(2018, 1, 1), recent_exit)
    ctx = make_context(employments=[emp])
    result = rule.evaluate(ctx)
    assert not result.correction_path["is_eligible"]


# ── PFD-002: Partial Advance ──────────────────────────────────────────────────

def test_pfd002_illness_ground_zero_years():
    rule = PFD002PartialAdvanceRule()
    emp = make_emp("Acme", date.today() - timedelta(days=180), None)  # 6 months service
    ctx = make_context(employments=[emp], advance_ground="ILLNESS")
    result = rule.evaluate(ctx)
    assert result.correction_path["is_eligible"]


def test_pfd002_marriage_ground_requires_seven_years():
    rule = PFD002PartialAdvanceRule()
    emp = make_emp("Acme", date.today() - timedelta(days=730), None)  # 2 years service
    ctx = make_context(employments=[emp], advance_ground="MARRIAGE")
    result = rule.evaluate(ctx)
    assert not result.correction_path["is_eligible"]
    assert result.correction_path["status"] == "INELIGIBLE"


def test_pfd002_house_ground_eligible_five_years():
    rule = PFD002PartialAdvanceRule()
    emp = make_emp("Acme", date.today() - timedelta(days=6 * 365), None)  # 6 years
    ctx = make_context(employments=[emp], advance_ground="HOUSE")
    result = rule.evaluate(ctx)
    assert result.correction_path["is_eligible"]


# ── PFD-003: Pension Withdrawal ───────────────────────────────────────────────

def test_pfd003_service_over_10_years_blocks_withdrawal():
    rule = PFD003PensionWithdrawalRule()
    emp = make_emp("Acme", date.today() - timedelta(days=12 * 365), date.today() - timedelta(days=60))
    ctx = make_context(employments=[emp])
    result = rule.evaluate(ctx)
    assert not result.correction_path["is_withdrawal_eligible"]
    assert "FORM-10D" in result.correction_path["form_number"]


def test_pfd003_service_under_10_years_eligible():
    rule = PFD003PensionWithdrawalRule()
    emp = make_emp("Acme", date.today() - timedelta(days=4 * 365), date.today() - timedelta(days=60))
    ctx = make_context(employments=[emp])
    result = rule.evaluate(ctx)
    assert result.correction_path["is_withdrawal_eligible"]
    assert result.correction_path["form_number"] == "FORM-10C"


# ── PFD-004: PF Transfer ──────────────────────────────────────────────────────

def test_pfd004_eligible_with_active_and_previous_accounts():
    rule = PFD004PFTransferRule()
    accounts = [make_account("ACTIVE"), make_account("INOPERATIVE")]
    uans = [make_uan("100123", kyc_status="VERIFIED")]
    ctx = make_context(accounts=accounts, uans=uans)
    result = rule.evaluate(ctx)
    assert result.correction_path["is_eligible"]


def test_pfd004_ineligible_single_account():
    rule = PFD004PFTransferRule()
    accounts = [make_account("ACTIVE")]
    uans = [make_uan("100123", kyc_status="VERIFIED")]
    ctx = make_context(accounts=accounts, uans=uans)
    result = rule.evaluate(ctx)
    assert not result.correction_path["is_eligible"]


# ── Calculator ────────────────────────────────────────────────────────────────

def test_calculator_tax_exempt_over_5_years():
    calc = PFCalculationEngine()
    emp = make_emp("Acme", date.today() - timedelta(days=6 * 365), None)
    uan = make_uan("100123", kyc_status="VERIFIED")
    balances = {"acc1": {"employee_share": 300000, "employer_share": 100000, "interest_accrued": 20000, "total_balance": 420000}}
    res = calc.calculate_payout([emp], [uan], balances, claim_type="FULL_WITHDRAWAL")
    assert res.is_tax_free
    assert res.estimated_tds_amount == 0.0
    assert res.total_balance == 420000.0


def test_calculator_tds_10_percent_with_pan():
    calc = PFCalculationEngine()
    emp = make_emp("Acme", date.today() - timedelta(days=2 * 365), None)
    uan = make_uan("100123", kyc_status="VERIFIED")
    balances = {"acc1": {"employee_share": 100000, "employer_share": 30000, "interest_accrued": 5000, "total_balance": 135000}}
    res = calc.calculate_payout([emp], [uan], balances, claim_type="FULL_WITHDRAWAL")
    assert not res.is_tax_free
    assert res.tds_rate_percent == 10.0
    assert res.estimated_tds_amount == 13500.0
    assert res.form_15g_applicable


def test_calculator_tds_20_percent_without_pan():
    calc = PFCalculationEngine()
    emp = make_emp("Acme", date.today() - timedelta(days=2 * 365), None)
    uan = make_uan("100123", kyc_status="UNVERIFIED")
    balances = {"acc1": {"employee_share": 100000, "employer_share": 30000, "interest_accrued": 5000, "total_balance": 135000}}
    res = calc.calculate_payout([emp], [uan], balances, claim_type="FULL_WITHDRAWAL")
    assert not res.is_tax_free
    assert res.tds_rate_percent == 20.0


# ── Pre-Submit Checker ────────────────────────────────────────────────────────

def test_presubmit_all_passed():
    checker = PreSubmitChecker()
    uan = make_uan("100123", kyc_status="VERIFIED")
    emp = make_emp("Acme", date(2018, 1, 1), date(2022, 1, 1))
    audit = checker.audit_claim_readiness([uan], [emp], claim_type="FULL_WITHDRAWAL")
    assert audit.is_ready_to_submit
    assert audit.readiness_score == 100


def test_presubmit_fails_without_kyc():
    checker = PreSubmitChecker()
    uan = make_uan("100123", kyc_status="UNVERIFIED")
    emp = make_emp("Acme", date(2018, 1, 1), date(2022, 1, 1))
    audit = checker.audit_claim_readiness([uan], [emp], claim_type="FULL_WITHDRAWAL")
    assert not audit.is_ready_to_submit
    assert audit.blocking_issues_count >= 1
