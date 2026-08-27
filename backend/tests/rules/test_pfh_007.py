from pfcompass.rules.base import RuleContext
from pfcompass.rules.health.pfh_007_kyc_mismatch import KYCMismatchRule


def test_pfh007_triggers_when_kyc_status_is_unverified():
    rule = KYCMismatchRule()
    context = RuleContext(
        citizen_id="c1",
        employment_records=[],
        pf_accounts=[],
        pf_balances={},
        uan_records=[
            {"id": "u1", "uan": "100111222333", "kyc_status": "UNVERIFIED"}
        ]
    )

    result = rule.evaluate(context)
    assert result.triggered is True
    assert result.severity == "HIGH"
    assert result.rule_id == "PFH-007"


def test_pfh007_does_not_trigger_when_kyc_status_is_verified():
    rule = KYCMismatchRule()
    context = RuleContext(
        citizen_id="c1",
        employment_records=[],
        pf_accounts=[],
        pf_balances={},
        uan_records=[
            {"id": "u1", "uan": "100111222333", "kyc_status": "VERIFIED"}
        ]
    )

    result = rule.evaluate(context)
    assert result.triggered is False
