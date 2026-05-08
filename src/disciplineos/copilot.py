from __future__ import annotations

from collections import Counter
from typing import Any


COMPLIANCE_NOTICE = (
    "Copilot output reviews discipline consistency only. It is not investment "
    "advice, does not predict returns, and does not provide trade-action recommendations."
)


def build_copilot_summary(dashboard: dict[str, Any]) -> dict[str, Any]:
    review = dashboard.get("review", {})
    cards = dashboard.get("cards", {})
    violations = dashboard.get("violations", [])
    open_violations = [item for item in violations if item.get("status") != "resolved"]

    return {
        "notice": COMPLIANCE_NOTICE,
        "monthly_review_draft": _monthly_review_draft(review, open_violations),
        "thesis_drift_alerts": _thesis_drift_alerts(cards, open_violations),
        "card_draft_suggestions": _card_draft_suggestions(cards, open_violations),
        "next_actions": _next_actions(review, open_violations),
    }


def _monthly_review_draft(
    review: dict[str, Any],
    open_violations: list[dict[str, Any]],
) -> str:
    score = review.get("discipline_score", 100)
    pass_rate = review.get("pass_rate", 100)
    attribution = review.get("attribution", {})
    behavior_summary = attribution.get("behavior", {}).get(
        "summary", "No behavior attribution issue recorded."
    )
    portfolio_summary = attribution.get("portfolio", {}).get(
        "summary", "No portfolio attribution issue recorded."
    )
    top_types = review.get("violation_types", {})
    top_text = ", ".join(f"{key} x{value}" for key, value in top_types.items()) or "none"

    return (
        f"Monthly discipline score is {score}/100 with pass rate {pass_rate}%. "
        f"Open issues: {len(open_violations)}. Main violation types: {top_text}. "
        f"Portfolio attribution: {portfolio_summary} Behavior attribution: {behavior_summary} "
        "Review whether repeated issues require profile or discipline-card updates."
    )


def _thesis_drift_alerts(
    cards: dict[str, dict[str, Any]],
    open_violations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    alerts = []
    for item in open_violations:
        if item.get("type") != "Thesis Drift":
            continue
        symbol = item.get("symbol", "")
        card = cards.get(symbol, {})
        alerts.append(
            {
                "symbol": symbol,
                "message": (
                    f"{symbol} has thesis drift. Current thesis: "
                    f"{'; '.join(card.get('thesis', [])) or 'not defined'}."
                ),
                "suggestion": "Update thesis and invalidation conditions before the next decision.",
            }
        )
    return alerts


def _card_draft_suggestions(
    cards: dict[str, dict[str, Any]],
    open_violations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    by_symbol: dict[str, Counter] = {}
    for item in open_violations:
        symbol = item.get("symbol", "")
        by_symbol.setdefault(symbol, Counter())[item.get("type", "Unknown")] += 1

    suggestions = []
    for symbol, counter in by_symbol.items():
        if not symbol or symbol not in cards:
            continue
        common_type, count = counter.most_common(1)[0]
        if count < 1:
            continue
        suggestions.append(
            {
                "symbol": symbol,
                "focus": common_type,
                "draft": _draft_for_violation(common_type),
            }
        )
    return suggestions[:6]


def _next_actions(
    review: dict[str, Any],
    open_violations: list[dict[str, Any]],
) -> list[str]:
    actions = []
    if open_violations:
        actions.append("Resolve or annotate open violations in the ledger.")
    if review.get("rule_revision_suggestions"):
        actions.append("Review generated rule revision suggestions.")
    if review.get("discipline_score", 100) < 80:
        actions.append("Pause new discretionary add decisions until review is complete.")
    if not actions:
        actions.append("Keep using the Decision Gate before material actions.")
    return actions


def _draft_for_violation(violation_type: str) -> str:
    if violation_type == "No Evidence Trade":
        return "Accepted evidence must include at least one concrete data point or event, not only price movement."
    if violation_type == "Position Overweight":
        return "If projected position exceeds the card limit, reduce planned amount or rebalance first."
    if violation_type == "Emotional Averaging Down":
        return "Averaging down is allowed only when new evidence confirms the original thesis."
    if violation_type == "Thesis Drift":
        return "When the original thesis changes, freeze new decisions until the card is rewritten."
    return "Clarify the related rule and add an explicit pre-decision checklist item."
