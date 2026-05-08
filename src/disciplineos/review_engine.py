from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


ATTRIBUTION_BUCKETS = {
    "market": {"market"},
    "security": {"buy", "sell", "thesis", "earnings"},
    "portfolio": {"position"},
    "behavior": {"emotion", "behavior", "evidence", "review", "general"},
}


def build_review_attribution(
    decisions: list[dict[str, Any]],
    audits: list[dict[str, Any]],
) -> dict[str, Any]:
    audit_by_id = {audit["decision_id"]: audit for audit in audits}
    bucket_counts: dict[str, Counter] = {
        bucket: Counter() for bucket in ATTRIBUTION_BUCKETS
    }
    symbol_counts: Counter = Counter()
    action_counts: Counter = Counter()

    for decision in decisions:
        symbol_counts[decision.get("symbol", "unknown")] += 1
        action_counts[decision.get("action", "unknown")] += 1
        audit = audit_by_id.get(decision.get("id"), {})
        for item in audit.get("violations", []) + audit.get("warnings", []):
            bucket = _bucket_for_category(str(item.get("category", "general")))
            bucket_counts[bucket][item.get("type", "Unknown")] += 1

    return {
        "market": _bucket_summary("market", bucket_counts["market"]),
        "security": _bucket_summary("security", bucket_counts["security"]),
        "portfolio": _bucket_summary("portfolio", bucket_counts["portfolio"]),
        "behavior": _bucket_summary("behavior", bucket_counts["behavior"]),
        "symbols": dict(symbol_counts),
        "actions": dict(action_counts),
    }


def build_rule_revision_suggestions(
    violations: list[dict[str, Any]],
) -> list[dict[str, str]]:
    open_violations = [
        item for item in violations if item.get("status", "open") != "resolved"
    ]
    by_type: Counter = Counter(item.get("type", "Unknown") for item in open_violations)
    by_symbol: dict[str, Counter] = defaultdict(Counter)
    for item in open_violations:
        by_symbol[item.get("symbol", "unknown")][item.get("type", "Unknown")] += 1

    suggestions: list[dict[str, str]] = []
    for violation_type, count in by_type.most_common():
        if count >= 2:
            suggestions.append(
                {
                    "scope": "profile",
                    "trigger": violation_type,
                    "suggestion": _profile_suggestion(violation_type),
                }
            )

    for symbol, counter in by_symbol.items():
        for violation_type, count in counter.most_common():
            if count >= 2:
                suggestions.append(
                    {
                        "scope": f"card:{symbol}",
                        "trigger": violation_type,
                        "suggestion": _card_suggestion(symbol, violation_type),
                    }
                )

    return suggestions[:8]


def _bucket_for_category(category: str) -> str:
    for bucket, categories in ATTRIBUTION_BUCKETS.items():
        if category in categories:
            return bucket
    return "behavior"


def _bucket_summary(bucket: str, counter: Counter) -> dict[str, Any]:
    total = sum(counter.values())
    top = [{"type": key, "count": value} for key, value in counter.most_common(5)]
    return {
        "bucket": bucket,
        "issue_count": total,
        "top_issues": top,
        "summary": _summary_text(bucket, total, top),
    }


def _summary_text(bucket: str, total: int, top: list[dict[str, Any]]) -> str:
    if total == 0:
        return f"No {bucket} attribution issue recorded."
    top_text = ", ".join(f"{item['type']} x{item['count']}" for item in top)
    return f"{bucket.title()} attribution has {total} issue(s): {top_text}."


def _profile_suggestion(violation_type: str) -> str:
    if violation_type == "Position Overweight":
        return "Tighten investor profile position limits or require forced reduction before adding."
    if violation_type in {"FOMO Trade", "Revenge Trade", "Emotional Averaging Down"}:
        return "Add this behavior to profile weaknesses and require a cooling-off rule."
    if violation_type == "No Evidence Trade":
        return "Require at least one concrete evidence item for every buy/add decision."
    return "Review investor profile constraints for repeated discipline failures."


def _card_suggestion(symbol: str, violation_type: str) -> str:
    if violation_type == "Thesis Drift":
        return f"Update {symbol} discipline card thesis and invalidation conditions."
    if violation_type == "Position Overweight":
        return f"Lower or clarify {symbol} max position rule."
    if violation_type == "No Evidence Trade":
        return f"Clarify accepted evidence types for {symbol} add/buy decisions."
    return f"Review {symbol} discipline card rules for repeated {violation_type}."

