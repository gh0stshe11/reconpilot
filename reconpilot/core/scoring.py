"""Priority scoring engine for assets and findings"""
from dataclasses import dataclass
from typing import Callable

from reconpilot.core.models import Asset, Finding, Severity


@dataclass
class ScoringRule:
    """Represents a scoring rule"""
    name: str
    condition: Callable[[Asset | Finding], bool]
    score_modifier: float
    reason: str


class ScoringEngine:
    """Engine for scoring assets and findings"""

    def __init__(self):
        self.asset_rules: list[ScoringRule] = []
        self.finding_rules: list[ScoringRule] = []
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialize default scoring rules"""
        # Asset scoring rules
        self.asset_rules = [
            ScoringRule(
                name="admin_panel",
                condition=lambda a: isinstance(a, Asset) and any(
                    x in a.value.lower() for x in ["admin", "login", "portal", "dashboard"]
                ),
                score_modifier=50.0,
                reason="Admin panel detected",
            ),
            ScoringRule(
                name="dev_environment",
                condition=lambda a: isinstance(a, Asset) and any(
                    x in a.value.lower() for x in ["dev", "staging", "test", "debug"]
                ),
                score_modifier=30.0,
                reason="Development environment",
            ),
            ScoringRule(
                name="database_port",
                condition=lambda a: isinstance(a, Asset) and a.type == "port" and any(
                    p in str(a.metadata.get("port", ""))
                    for p in ["3306", "5432", "27017", "6379", "1433"]
                ),
                score_modifier=40.0,
                reason="Database port exposed",
            ),
            ScoringRule(
                name="sensitive_file",
                condition=lambda a: isinstance(a, Asset) and any(
                    x in a.value.lower()
                    for x in [".git", ".env", "config", "backup", ".sql", ".db"]
                ),
                score_modifier=35.0,
                reason="Sensitive file detected",
            ),
            ScoringRule(
                name="api_endpoint",
                condition=lambda a: isinstance(a, Asset) and any(
                    x in a.value.lower() for x in ["/api/", "/v1/", "/v2/", "graphql"]
                ),
                score_modifier=25.0,
                reason="API endpoint",
            ),
        ]

        # Finding scoring rules based on severity
        severity_scores = {
            Severity.CRITICAL: 100.0,
            Severity.HIGH: 75.0,
            Severity.MEDIUM: 50.0,
            Severity.LOW: 25.0,
            Severity.INFO: 10.0,
        }

        self.finding_rules = [
            ScoringRule(
                name=f"severity_{sev.value}",
                condition=lambda f, s=sev: isinstance(f, Finding) and f.severity == s,
                score_modifier=score,
                reason=f"{sev.value.capitalize()} severity",
            )
            for sev, score in severity_scores.items()
        ]

    def score_asset(self, asset: Asset) -> float:
        """Calculate score for an asset"""
        base_score = 10.0
        total_score = base_score

        for rule in self.asset_rules:
            if rule.condition(asset):
                total_score += rule.score_modifier

        return min(total_score, 100.0)

    def score_finding(self, finding: Finding) -> float:
        """Calculate score for a finding"""
        total_score = 0.0

        for rule in self.finding_rules:
            if rule.condition(finding):
                total_score += rule.score_modifier

        return min(total_score, 100.0)

    def add_asset_rule(self, rule: ScoringRule) -> None:
        """Add a custom asset scoring rule"""
        self.asset_rules.append(rule)

    def add_finding_rule(self, rule: ScoringRule) -> None:
        """Add a custom finding scoring rule"""
        self.finding_rules.append(rule)
