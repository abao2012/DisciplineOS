from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .models import (
    Action,
    AuditResult,
    AuditStatus,
    Decision,
    DisciplineCard,
    Emotion,
    InvestorProfile,
    Severity,
    Violation,
)
from .violation_catalog import get_violation_definition


RuleFn = Callable[[InvestorProfile, DisciplineCard, Decision], list[Violation]]


@dataclass(frozen=True, slots=True)
class RuleSpec:
    id: str
    name: str
    fn: RuleFn


BLOCKING_SEVERITIES = {Severity.HIGH}
WARN_SEVERITIES = {Severity.MEDIUM, Severity.LOW}


def evaluate_decision(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> AuditResult:
    violations: list[Violation] = []
    warnings: list[Violation] = []
    notes: list[str] = []

    for finding in run_rules(profile, card, decision):
        if finding.severity in BLOCKING_SEVERITIES:
            violations.append(finding)
        elif finding.severity in WARN_SEVERITIES:
            warnings.append(finding)
        else:
            notes.append(finding.message)

    evidence_findings = [
        item
        for item in warnings
        if item.rule_id.startswith("evidence.") or item.category == "evidence"
    ]
    review_findings = [
        item
        for item in warnings
        if item.rule_id.startswith(("review.", "thesis.")) or item.category in {"review", "thesis"}
    ]

    if violations:
        status = AuditStatus.BLOCKED
    elif evidence_findings:
        status = AuditStatus.EVIDENCE_REQUIRED
    elif review_findings:
        status = AuditStatus.REVIEW_REQUIRED
    elif warnings:
        status = AuditStatus.WARN
    else:
        status = AuditStatus.PASS
        notes.append("Decision is consistent with the current discipline card.")

    return AuditResult(
        decision_id=decision.id,
        status=status,
        violations=violations,
        warnings=warnings,
        notes=notes,
    )


def list_rule_specs() -> list[dict[str, str]]:
    return [{"id": rule.id, "name": rule.name} for rule in DECISION_RULES]


def build_rule_results(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for rule in DECISION_RULES:
        findings = rule.fn(profile, card, decision)
        params = _rule_params_for_result(profile, card, rule.id)
        if not findings:
            results.append(
                {
                    "decision_id": decision.id,
                    "rule_code": rule.id,
                    "rule_name": rule.name,
                    "status": AuditStatus.PASS.value,
                    "severity": Severity.INFO.value,
                    "category": _category_for_rule(rule.id),
                    "message": "Rule passed.",
                    "params": params,
                }
            )
            continue
        for finding in findings:
            results.append(
                {
                    "decision_id": decision.id,
                    "rule_code": finding.rule_id,
                    "rule_name": rule.name,
                    "status": _status_for_finding(finding).value,
                    "severity": finding.severity.value,
                    "category": finding.category,
                    "message": finding.message,
                    "params": params,
                }
            )
    return results


def run_rules(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    findings: list[Violation] = []
    for rule in DECISION_RULES:
        findings.extend(rule.fn(profile, card, decision))
    return findings


def _position_limit_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    card_limit = _rule_param(card, "position.max_single", "max_position_pct", card.max_position_pct)
    position_limit = min(float(card_limit), profile.max_single_position_pct)
    if decision.position_after_pct <= position_limit:
        return []
    return [
        _violation(
            violation_type="Position Overweight",
            rule_id="position.max_single",
            message=(
                f"Position after action is {decision.position_after_pct:.1f}%, "
                f"above the allowed {position_limit:.1f}%."
            ),
        )
    ]


def _evidence_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    rule = _card_rule(card, "evidence.required_for_add")
    require_add_only = rule is not None
    checked_actions = {Action.ADD} if require_add_only else {Action.BUY, Action.ADD}
    if decision.action not in checked_actions or decision.evidence:
        return []
    return [
        _violation(
            violation_type="No Evidence Trade",
            rule_id="evidence.required_for_add" if require_add_only else "evidence.required_for_buy_or_add",
            message="Buy/add decisions must include traceable evidence, not only a narrative.",
        )
    ]


def _emotional_averaging_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    reason = decision.reason.lower()
    emotional_terms = ("fallen", "drop", "cheap", "average cost", "reduce my cost")
    emotional_state = decision.emotion in {
        Emotion.ANXIOUS,
        Emotion.FEARFUL,
        Emotion.REVENGE,
    }
    if decision.action != Action.ADD or not (
        emotional_state or any(term in reason for term in emotional_terms)
    ):
        return []
    severity = Severity.HIGH if not decision.evidence else Severity.MEDIUM
    return [
        _violation(
            violation_type="Emotional Averaging Down",
            rule_id="behavior.no_emotional_averaging_down",
            severity=severity,
            message=(
                "Add decision looks driven by anxiety or cost averaging "
                "instead of new evidence."
            ),
        )
    ]


def _earnings_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    if (
        decision.action in {Action.BUY, Action.ADD}
        and decision.is_before_earnings
        and not profile.allow_pre_earnings_add
    ):
        return [
            _violation(
                violation_type="Earnings Bet",
                rule_id="earnings.no_unplanned_add",
                message="Adding before earnings is not allowed by the investor profile.",
            )
        ]
    return []


def _fomo_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    if decision.emotion != Emotion.FOMO:
        return []
    return [
        _violation(
            violation_type="FOMO Trade",
            rule_id="behavior.no_fomo",
            message="Decision is marked as FOMO and should be reviewed before acting.",
        )
    ]


def _revenge_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    if decision.emotion != Emotion.REVENGE:
        return []
    return [
        _violation(
            violation_type="Revenge Trade",
            rule_id="behavior.no_revenge_trade",
            message="Decision is marked as revenge trading after loss or frustration.",
        )
    ]


def _thesis_drift_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    if not decision.thesis_changed:
        return []
    return [
        _violation(
            violation_type="Thesis Drift",
            rule_id="thesis.review_required",
            severity=Severity.MEDIUM,
            message="The investment thesis changed; update the discipline card before acting.",
        )
    ]


def _style_drift_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    reason = decision.reason.lower()
    terms = ("long term now", "hold forever", "value now", "changed to value")
    if not any(term in reason for term in terms):
        return []
    return [
        _violation(
            violation_type="Style Drift",
            rule_id="behavior.no_style_drift",
            message="Reason suggests changing the investment style after the fact.",
        )
    ]


def _valuation_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    reason = decision.reason.lower()
    terms = ("valuation too high", "overvalued", "outside valuation range")
    if decision.action not in {Action.BUY, Action.ADD} or not any(
        term in reason for term in terms
    ):
        return []
    return [
        _violation(
            violation_type="Valuation Violation",
            rule_id="valuation.range_required",
            message="Reason indicates valuation may be outside the discipline range.",
        )
    ]


def _review_rule(
    profile: InvestorProfile,
    card: DisciplineCard,
    decision: Decision,
) -> list[Violation]:
    if decision.action not in {Action.ADD, Action.REDUCE, Action.SELL}:
        return []
    return [
        _violation(
            violation_type="Review Required",
            rule_id="review.after_material_action",
            message="Material actions should be included in the next monthly review.",
        )
    ]


def _violation(
    violation_type: str,
    rule_id: str,
    message: str,
    severity: Severity | None = None,
) -> Violation:
    definition = get_violation_definition(violation_type)
    return Violation(
        type=definition.type,
        message=message,
        severity=severity or definition.default_severity,
        rule_id=rule_id,
        category=definition.category,
        remediation=definition.remediation,
        weight=definition.weight,
    )


def _card_rule(card: DisciplineCard, rule_code: str) -> dict | None:
    for rule in card.card_rules:
        if rule.get("rule_code") == rule_code and rule.get("enabled", True):
            return rule
    return None


def _rule_param(
    card: DisciplineCard,
    rule_code: str,
    param_name: str,
    default: float | str | bool,
) -> float | str | bool:
    rule = _card_rule(card, rule_code)
    if not rule:
        return default
    params = rule.get("params") or {}
    return params.get(param_name, default)


def _rule_params_for_result(
    profile: InvestorProfile,
    card: DisciplineCard,
    rule_code: str,
) -> dict[str, Any]:
    if rule_code == "position.max_single":
        card_limit = _rule_param(
            card,
            "position.max_single",
            "max_position_pct",
            card.max_position_pct,
        )
        return {
            "card_limit_pct": float(card_limit),
            "profile_limit_pct": profile.max_single_position_pct,
            "effective_limit_pct": min(float(card_limit), profile.max_single_position_pct),
        }
    card_rule = _card_rule(card, rule_code) or _card_rule(card, "evidence.required_for_add")
    if card_rule:
        return dict(card_rule.get("params") or {})
    return {}


def _status_for_finding(finding: Violation) -> AuditStatus:
    if finding.severity in BLOCKING_SEVERITIES:
        return AuditStatus.BLOCKED
    if finding.rule_id.startswith("evidence.") or finding.category == "evidence":
        return AuditStatus.EVIDENCE_REQUIRED
    if finding.rule_id.startswith(("review.", "thesis.")) or finding.category in {
        "review",
        "thesis",
    }:
        return AuditStatus.REVIEW_REQUIRED
    if finding.severity in WARN_SEVERITIES:
        return AuditStatus.WARN
    return AuditStatus.PASS


def _category_for_rule(rule_code: str) -> str:
    if rule_code.startswith("position."):
        return "position"
    if rule_code.startswith("evidence."):
        return "evidence"
    if rule_code.startswith("earnings."):
        return "earnings"
    if rule_code.startswith("thesis."):
        return "thesis"
    if rule_code.startswith("review."):
        return "review"
    if rule_code.startswith(("behavior.", "emotion.")):
        return "emotion"
    if rule_code.startswith("valuation."):
        return "buy"
    return "general"


DECISION_RULES: list[RuleSpec] = [
    RuleSpec("position.max_single", "Position limit", _position_limit_rule),
    RuleSpec("evidence.required_for_buy_or_add", "Evidence required", _evidence_rule),
    RuleSpec(
        "behavior.no_emotional_averaging_down",
        "Emotional averaging down",
        _emotional_averaging_rule,
    ),
    RuleSpec("earnings.no_unplanned_add", "Earnings bet", _earnings_rule),
    RuleSpec("behavior.no_fomo", "FOMO trade", _fomo_rule),
    RuleSpec("behavior.no_revenge_trade", "Revenge trade", _revenge_rule),
    RuleSpec("thesis.review_required", "Thesis drift", _thesis_drift_rule),
    RuleSpec("behavior.no_style_drift", "Style drift", _style_drift_rule),
    RuleSpec("valuation.range_required", "Valuation violation", _valuation_rule),
    RuleSpec("review.after_material_action", "Review required", _review_rule),
]
