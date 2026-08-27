from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional


@dataclass
class RuleEvidence:
    field: str
    expected: Optional[str]
    actual: Optional[str]
    source: str
    description: str


@dataclass
class RuleResult:
    rule_id: str
    rule_version: str
    triggered: bool
    severity: Optional[str] = None  # CRITICAL | HIGH | MEDIUM | LOW | INFO
    what_is_wrong: Optional[str] = None
    why_it_happened: Optional[str] = None
    potential_impact: Optional[str] = None
    correction_path: Optional[dict[str, Any]] = None
    evidence: list[RuleEvidence] = field(default_factory=list)
    affected_account_ids: list[str] = field(default_factory=list)
    affected_employment_ids: list[str] = field(default_factory=list)


@dataclass
class RuleContext:
    citizen_id: str
    employment_records: list[dict[str, Any]]
    pf_accounts: list[dict[str, Any]]
    pf_balances: dict[str, dict[str, Any]]  # pf_account_id -> balance dict
    uan_records: list[dict[str, Any]]
    evaluation_date: date = field(default_factory=date.today)


class PFHealthRule(ABC):
    """Abstract base class for deterministic PF Health rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        ...

    @property
    @abstractmethod
    def domain(self) -> str:
        ...

    @abstractmethod
    def evaluate(self, context: RuleContext) -> RuleResult:
        ...

    def _no_finding(self) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            rule_version=self.version,
            triggered=False,
            severity=None,
            what_is_wrong=None,
            why_it_happened=None,
            potential_impact=None,
            correction_path=None,
            evidence=[],
            affected_account_ids=[],
            affected_employment_ids=[],
        )
