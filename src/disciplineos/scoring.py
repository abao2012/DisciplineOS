from __future__ import annotations

from collections import defaultdict
from typing import Any


SCORE_WEIGHTS: dict[str, int] = {
    "position": 25,
    "buy": 20,
    "sell": 15,
    "earnings": 10,
    "review": 10,
    "emotion": 10,
    "evidence": 10,
}

CATEGORY_ALIASES = {
    "behavior": "emotion",
    "thesis": "buy",
    "general": "review",
}


def calculate_discipline_score(audits: list[dict[str, Any]]) -> dict[str, Any]:
    deductions: dict[str, int] = defaultdict(int)
    issues: list[dict[str, Any]] = []

    for audit in audits:
        for item in audit.get("violations", []) + audit.get("warnings", []):
            category = _score_category(str(item.get("category", "general")))
            if category not in SCORE_WEIGHTS:
                continue
            weight = int(item.get("weight", 0))
            severity_multiplier = _severity_multiplier(str(item.get("severity", "info")))
            deduction = min(SCORE_WEIGHTS[category], round(weight * severity_multiplier))
            deductions[category] += deduction
            issues.append(
                {
                    "type": item.get("type"),
                    "category": category,
                    "severity": item.get("severity"),
                    "deduction": deduction,
                    "remediation": item.get("remediation", ""),
                }
            )

    dimensions = {}
    for category, max_score in SCORE_WEIGHTS.items():
        deduction = min(max_score, deductions.get(category, 0))
        dimensions[category] = {
            "weight": max_score,
            "deduction": deduction,
            "score": max(max_score - deduction, 0),
        }

    total = sum(item["score"] for item in dimensions.values())
    return {
        "score": total,
        "max_score": sum(SCORE_WEIGHTS.values()),
        "dimensions": dimensions,
        "issues": issues,
    }


def _score_category(category: str) -> str:
    return CATEGORY_ALIASES.get(category, category)


def _severity_multiplier(severity: str) -> float:
    if severity == "high":
        return 1.0
    if severity == "medium":
        return 0.6
    if severity == "low":
        return 0.3
    return 0.0

