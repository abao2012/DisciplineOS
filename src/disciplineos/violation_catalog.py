from __future__ import annotations

from dataclasses import dataclass

from .models import Severity


@dataclass(frozen=True, slots=True)
class ViolationDefinition:
    type: str
    category: str
    default_severity: Severity
    weight: int
    remediation: str


VIOLATION_CATALOG: dict[str, ViolationDefinition] = {
    "Position Overweight": ViolationDefinition(
        type="Position Overweight",
        category="position",
        default_severity=Severity.HIGH,
        weight=25,
        remediation="Reduce planned size or lower existing exposure before adding.",
    ),
    "Emotional Averaging Down": ViolationDefinition(
        type="Emotional Averaging Down",
        category="emotion",
        default_severity=Severity.HIGH,
        weight=10,
        remediation="Pause the action and require new evidence unrelated to price decline.",
    ),
    "Earnings Bet": ViolationDefinition(
        type="Earnings Bet",
        category="earnings",
        default_severity=Severity.HIGH,
        weight=10,
        remediation="Create a pre-earnings plan or wait until earnings uncertainty clears.",
    ),
    "Valuation Violation": ViolationDefinition(
        type="Valuation Violation",
        category="buy",
        default_severity=Severity.MEDIUM,
        weight=20,
        remediation="Define or revisit the valuation range before buying or adding.",
    ),
    "No Evidence Trade": ViolationDefinition(
        type="No Evidence Trade",
        category="evidence",
        default_severity=Severity.MEDIUM,
        weight=10,
        remediation="Attach concrete new evidence before proceeding.",
    ),
    "Thesis Drift": ViolationDefinition(
        type="Thesis Drift",
        category="thesis",
        default_severity=Severity.HIGH,
        weight=20,
        remediation="Update the discipline card before making a new decision.",
    ),
    "Style Drift": ViolationDefinition(
        type="Style Drift",
        category="behavior",
        default_severity=Severity.HIGH,
        weight=10,
        remediation="Do not re-label a failed thesis as a different investment style.",
    ),
    "FOMO Trade": ViolationDefinition(
        type="FOMO Trade",
        category="emotion",
        default_severity=Severity.MEDIUM,
        weight=10,
        remediation="Wait for a planned entry condition instead of reacting to heat.",
    ),
    "Revenge Trade": ViolationDefinition(
        type="Revenge Trade",
        category="emotion",
        default_severity=Severity.HIGH,
        weight=10,
        remediation="Stop trading for the review period and document the loss trigger.",
    ),
    "Review Missing": ViolationDefinition(
        type="Review Missing",
        category="review",
        default_severity=Severity.LOW,
        weight=10,
        remediation="Add this action to the next monthly review checklist.",
    ),
    "Review Required": ViolationDefinition(
        type="Review Required",
        category="review",
        default_severity=Severity.LOW,
        weight=10,
        remediation="Include this material action in the monthly review.",
    ),
}


def get_violation_definition(violation_type: str) -> ViolationDefinition:
    if violation_type not in VIOLATION_CATALOG:
        return ViolationDefinition(
            type=violation_type,
            category="general",
            default_severity=Severity.INFO,
            weight=0,
            remediation="Review the decision and update the discipline card if needed.",
        )
    return VIOLATION_CATALOG[violation_type]

