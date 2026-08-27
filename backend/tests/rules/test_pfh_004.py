from pfcompass.rules.base import RuleContext
from pfcompass.rules.health.pfh_004_uan_multiplicity import UANMultiplicityRule


def test_pfh004_triggers_when_multiple_uans_present():
    rule = UANMultiplicityRule({"max_allowed_uans": 1})
    context = RuleContext(
        citizen_id="c1",
        employment_records=[],
        pf_accounts=[],
        pf_balances={},
        uan_records=[
            {"id": "u1", "uan": "100111222333", "is_primary": True},
            {"id": "u2", "uan": "100444555666", "is_primary": False}
        ]
    )

    result = rule.evaluate(context)
    assert result.triggered is True
    assert result.severity == "CRITICAL"
    assert result.rule_id == "PFH-004"


def test_pfh004_does_not_trigger_for_single_uan():
    rule = UANMultiplicityRule({"max_allowed_uans": 1})
    context = RuleContext(
        citizen_id="c1",
        employment_records=[],
        pf_accounts=[],
        pf_balances={},
        uan_records=[
            {"id": "u1", "uan": "100111222333", "is_primary": True}
        ]
    )

    result = rule.evaluate(context)
    assert result.triggered is False
