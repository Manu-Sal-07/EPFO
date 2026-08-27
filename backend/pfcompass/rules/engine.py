from pathlib import Path
from typing import Any
import yaml

from pfcompass.rules.base import PFHealthRule, RuleContext, RuleResult
from pfcompass.rules.health.pfh_001_inoperative import InoperativeAccountRule
from pfcompass.rules.health.pfh_002_missing_exit import MissingExitDateRule
from pfcompass.rules.health.pfh_004_uan_multiplicity import UANMultiplicityRule
from pfcompass.rules.health.pfh_007_kyc_mismatch import KYCMismatchRule

# Registry mapping rule_id to rule class
RULE_CLASS_MAP: dict[str, type[PFHealthRule]] = {
    "PFH-001": InoperativeAccountRule,
    "PFH-002": MissingExitDateRule,
    "PFH-004": UANMultiplicityRule,
    "PFH-007": KYCMismatchRule,
}


class RuleRegistry:
    """Registry managing rule definitions and execution."""

    def __init__(self, definitions_dir: Path | None = None):
        if definitions_dir is None:
            definitions_dir = Path(__file__).parent.parent / "rule_definitions" / "health"
        self._definitions_dir = definitions_dir
        self._rules: dict[str, PFHealthRule] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        if not self._definitions_dir.exists():
            return

        for yaml_file in self._definitions_dir.glob("*.yaml"):
            try:
                content = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                rule_id = content.get("id")
                if rule_id in RULE_CLASS_MAP:
                    rule_cls = RULE_CLASS_MAP[rule_id]
                    self._rules[rule_id] = rule_cls(content.get("parameters"))
            except Exception as e:
                print(f"Error loading rule definition {yaml_file}: {e}")

    def get_rules(self) -> list[PFHealthRule]:
        return list(self._rules.values())

    def evaluate_health(self, context: RuleContext) -> list[RuleResult]:
        """Evaluate all active rules against the given citizen context."""
        results: list[RuleResult] = []
        for rule in self._rules.values():
            try:
                res = rule.evaluate(context)
                if res.triggered:
                    results.append(res)
            except Exception as e:
                print(f"Error evaluating rule {rule.rule_id}: {e}")
        return results
