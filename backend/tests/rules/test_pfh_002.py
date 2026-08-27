from datetime import date
from pfcompass.rules.base import RuleContext
from pfcompass.rules.health.pfh_002_missing_exit import MissingExitDateRule


def test_pfh002_triggers_for_missing_exit_date_on_past_employment():
    rule = MissingExitDateRule()
    context = RuleContext(
        citizen_id="c1",
        employment_records=[
            {
                "id": "emp1",
                "employer_name": "Old Corp",
                "date_of_joining": date(2018, 1, 1),
                "date_of_exit": None  # Missing exit date on former employment
            },
            {
                "id": "emp2",
                "employer_name": "New Corp",
                "date_of_joining": date(2021, 1, 1),
                "date_of_exit": None  # Current employment
            }
        ],
        pf_accounts=[],
        pf_balances={},
        uan_records=[]
    )

    result = rule.evaluate(context)
    assert result.triggered is True
    assert result.severity == "HIGH"
    assert result.rule_id == "PFH-002"
    assert len(result.affected_employment_ids) == 1
    assert result.affected_employment_ids[0] == "emp1"


def test_pfh002_does_not_trigger_when_all_past_employments_have_exit_dates():
    rule = MissingExitDateRule()
    context = RuleContext(
        citizen_id="c1",
        employment_records=[
            {
                "id": "emp1",
                "employer_name": "Old Corp",
                "date_of_joining": date(2018, 1, 1),
                "date_of_exit": date(2020, 12, 31)
            },
            {
                "id": "emp2",
                "employer_name": "New Corp",
                "date_of_joining": date(2021, 1, 1),
                "date_of_exit": None
            }
        ],
        pf_accounts=[],
        pf_balances={},
        uan_records=[]
    )

    result = rule.evaluate(context)
    assert result.triggered is False
