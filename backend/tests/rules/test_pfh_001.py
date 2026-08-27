from datetime import date
from pfcompass.rules.base import RuleContext
from pfcompass.rules.health.pfh_001_inoperative import InoperativeAccountRule


def test_pfh001_triggers_for_inoperative_account():
    rule = InoperativeAccountRule({"inoperative_threshold_months": 36})
    context = RuleContext(
        citizen_id="c1",
        employment_records=[
            {
                "id": "emp1",
                "employer_name": "Test Corp",
                "date_of_joining": date(2015, 1, 1),
                "date_of_exit": date(2019, 1, 1)  # > 36 months ago
            }
        ],
        pf_accounts=[
            {
                "id": "acc1",
                "employment_id": "emp1",
                "member_id": "MEM123",
                "status": "INOPERATIVE"
            }
        ],
        pf_balances={},
        uan_records=[],
        evaluation_date=date(2024, 8, 1)
    )

    result = rule.evaluate(context)
    assert result.triggered is True
    assert result.severity == "HIGH"
    assert result.rule_id == "PFH-001"
    assert len(result.evidence) >= 1


def test_pfh001_does_not_trigger_for_current_active_employee():
    rule = InoperativeAccountRule({"inoperative_threshold_months": 36})
    context = RuleContext(
        citizen_id="c1",
        employment_records=[
            {
                "id": "emp1",
                "employer_name": "Current Corp",
                "date_of_joining": date(2022, 1, 1),
                "date_of_exit": None
            }
        ],
        pf_accounts=[
            {
                "id": "acc1",
                "employment_id": "emp1",
                "member_id": "MEM999",
                "status": "ACTIVE"
            }
        ],
        pf_balances={},
        uan_records=[],
        evaluation_date=date(2024, 8, 1)
    )

    result = rule.evaluate(context)
    assert result.triggered is False
