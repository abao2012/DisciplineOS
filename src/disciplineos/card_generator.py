from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import DisciplineCard


CARD_TEMPLATES: dict[str, dict[str, Any]] = {
    "value": {
        "label": "Value",
        "asset_type": "stock",
        "sector": "unknown",
        "default_max_position_pct": 15,
        "thesis_options": [
            "Valuation is below the long-term discipline range.",
            "Cash flow and profitability remain stable.",
            "Dividend or shareholder return remains reliable.",
        ],
        "no_buy_conditions": [
            "Valuation is outside the pre-defined discipline range.",
            "Safety margin is not clear.",
        ],
        "add_conditions": [
            "Valuation remains inside the discipline range.",
            "Fundamentals remain stable or improve.",
            "New evidence supports the original thesis.",
        ],
        "raise_position_conditions": [
            "Two consecutive reviews confirm the thesis and risk remains controlled.",
            "Cash flow, profit, or order evidence improves materially.",
        ],
        "reduce_conditions": [
            "Position exceeds the limit.",
            "Valuation becomes overheated.",
            "Fundamentals weaken materially.",
        ],
        "lower_position_conditions": [
            "Evidence quality weakens or becomes stale.",
            "Volatility or drawdown exceeds the pre-defined tolerance.",
        ],
        "invalid_conditions": [
            "Core profitability or cash flow deteriorates for two review periods.",
            "The original safety margin no longer exists.",
        ],
        "forbidden_behaviors": [
            "Do not buy only because the price has fallen.",
            "Do not add without new fundamental evidence.",
        ],
    },
    "growth": {
        "label": "Growth",
        "asset_type": "stock",
        "sector": "unknown",
        "default_max_position_pct": 12,
        "thesis_options": [
            "Revenue growth is accelerating.",
            "Profit growth confirms operating leverage.",
            "New product, order, or user data supports the second curve.",
        ],
        "no_buy_conditions": [
            "Growth rate no longer matches valuation.",
            "The second growth curve is unproven.",
        ],
        "add_conditions": [
            "Revenue or profit growth confirms the thesis.",
            "New product, order, or user data improves visibility.",
        ],
        "raise_position_conditions": [
            "Growth is confirmed by both revenue and profit quality.",
            "The second curve becomes measurable instead of narrative-only.",
        ],
        "reduce_conditions": [
            "Growth slows below the discipline threshold.",
            "Position or theme exposure becomes concentrated.",
        ],
        "lower_position_conditions": [
            "Growth remains strong but valuation/risk becomes asymmetric.",
            "Customer, order, or margin evidence deteriorates.",
        ],
        "invalid_conditions": [
            "Core growth indicators miss expectations for two periods.",
            "Management guidance weakens materially.",
        ],
        "forbidden_behaviors": [
            "Do not chase a hot theme without evidence.",
            "Do not reinterpret a broken growth thesis as a value thesis.",
        ],
    },
    "cyclical": {
        "label": "Cyclical",
        "asset_type": "stock",
        "sector": "cyclical",
        "default_max_position_pct": 10,
        "thesis_options": [
            "Cycle data is improving from the trough.",
            "Product price or inventory data supports recovery.",
            "Capital expenditure discipline remains acceptable.",
        ],
        "no_buy_conditions": [
            "Cycle position is unclear.",
            "Inventory or product price data conflicts with the thesis.",
        ],
        "add_conditions": [
            "Cycle data improves and confirms the expected direction.",
            "Capital expenditure discipline remains acceptable.",
        ],
        "raise_position_conditions": [
            "Inventory, price, and demand data all confirm cycle recovery.",
            "Supply expansion remains constrained while demand improves.",
        ],
        "reduce_conditions": [
            "Product price or inventory data turns against the thesis.",
            "Position becomes too large for a cyclical asset.",
        ],
        "lower_position_conditions": [
            "Cycle evidence becomes mixed or late-stage.",
            "Industry supply growth weakens the expected recovery.",
        ],
        "invalid_conditions": [
            "Cycle recovery evidence fails to appear.",
            "Supply expansion damages the original thesis.",
        ],
        "forbidden_behaviors": [
            "Do not average down without updated cycle evidence.",
            "Do not treat cyclical profits as permanently stable.",
        ],
    },
    "trend": {
        "label": "Trend",
        "asset_type": "stock",
        "sector": "theme",
        "default_max_position_pct": 10,
        "thesis_options": [
            "Trend strength remains above the pre-defined threshold.",
            "Volume confirms participation rather than only narrative heat.",
            "Theme leadership remains intact.",
        ],
        "no_buy_conditions": [
            "Trend strength has already weakened.",
            "Entry is based only on social heat or price momentum.",
        ],
        "add_conditions": [
            "Trend strength and volume confirm continuation.",
            "Position remains below the limit.",
        ],
        "raise_position_conditions": [
            "Trend, volume, and leadership all remain intact after review.",
            "Risk can still be reduced through a clear exit rule.",
        ],
        "reduce_conditions": [
            "Trend breaks the pre-defined exit signal.",
            "Theme exposure becomes concentrated.",
        ],
        "lower_position_conditions": [
            "Trend remains but volume participation weakens.",
            "Theme crowding or single-name exposure becomes excessive.",
        ],
        "invalid_conditions": [
            "The main trend signal fails.",
            "The theme narrative changes without supporting data.",
        ],
        "forbidden_behaviors": [
            "Do not chase FOMO after a sharp rise.",
            "Do not convert a failed trend trade into a long-term thesis.",
        ],
    },
    "etf": {
        "label": "ETF",
        "asset_type": "ETF",
        "sector": "index",
        "default_max_position_pct": 25,
        "thesis_options": [
            "Allocation plan requires index exposure.",
            "Purchase follows the pre-defined batch plan.",
            "Portfolio rebalance requires adding this exposure.",
        ],
        "no_buy_conditions": [
            "Allocation plan has not been defined.",
            "The purchase breaks the rebalance plan.",
        ],
        "add_conditions": [
            "Purchase follows the batch plan.",
            "Portfolio allocation remains inside limits.",
        ],
        "raise_position_conditions": [
            "Portfolio rebalance plan explicitly raises the target allocation.",
            "Drawdown has been pre-budgeted and batch rules remain intact.",
        ],
        "reduce_conditions": [
            "Allocation exceeds target range.",
            "Rebalance rule is triggered.",
        ],
        "lower_position_conditions": [
            "Portfolio target allocation is lowered.",
            "Correlation with existing holdings becomes too high.",
        ],
        "invalid_conditions": [
            "Index exposure no longer matches the portfolio objective.",
        ],
        "forbidden_behaviors": [
            "Do not buy only because the index dropped today.",
            "Do not abandon the batch plan during volatility.",
        ],
    },
}


def list_card_templates() -> dict[str, dict[str, Any]]:
    return deepcopy(CARD_TEMPLATES)


def generate_card_from_answers(payload: dict[str, Any]) -> DisciplineCard:
    template_key = str(payload.get("template", "value"))
    template = deepcopy(CARD_TEMPLATES.get(template_key, CARD_TEMPLATES["value"]))

    symbol = str(payload.get("symbol", "")).strip().upper()
    if not symbol:
        raise ValueError("symbol is required")

    name = str(payload.get("name", symbol)).strip() or symbol
    sector = str(payload.get("sector") or template["sector"])
    max_position_pct = float(
        payload.get("max_position_pct") or template["default_max_position_pct"]
    )
    review_cycle = str(payload.get("review_cycle") or "monthly")

    why_buy = _lines(payload.get("why_buy"))
    no_buy = _lines(payload.get("no_buy"))
    add_when = _lines(payload.get("add_when"))
    reduce_when = _lines(payload.get("reduce_when"))
    raise_position = _lines(payload.get("raise_position"))
    lower_position = _lines(payload.get("lower_position"))
    invalid_when = _lines(payload.get("invalid_when"))
    forbidden = _lines(payload.get("forbidden_behaviors"))

    card_rules = build_card_rules(
        max_position_pct=max_position_pct,
        no_buy_conditions=no_buy or template["no_buy_conditions"],
        add_conditions=add_when or template["add_conditions"],
        reduce_conditions=reduce_when or template["reduce_conditions"],
        raise_position_conditions=raise_position
        or template["raise_position_conditions"],
        lower_position_conditions=lower_position
        or template["lower_position_conditions"],
        invalid_conditions=invalid_when or template["invalid_conditions"],
    )

    return DisciplineCard(
        symbol=symbol,
        name=name,
        asset_type=str(payload.get("asset_type") or template["asset_type"]),
        sector=sector,
        thesis=why_buy or ["Define the core investment thesis before acting."],
        max_position_pct=max_position_pct,
        no_buy_conditions=no_buy or template["no_buy_conditions"],
        add_conditions=add_when or template["add_conditions"],
        reduce_conditions=reduce_when or template["reduce_conditions"],
        raise_position_conditions=raise_position
        or template["raise_position_conditions"],
        lower_position_conditions=lower_position
        or template["lower_position_conditions"],
        invalid_conditions=invalid_when or template["invalid_conditions"],
        forbidden_behaviors=forbidden or template["forbidden_behaviors"],
        card_rules=card_rules,
        review_cycle=review_cycle,
    )


def build_card_rules(
    *,
    max_position_pct: float,
    no_buy_conditions: list[str],
    add_conditions: list[str],
    reduce_conditions: list[str],
    invalid_conditions: list[str],
    raise_position_conditions: list[str] | None = None,
    lower_position_conditions: list[str] | None = None,
) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = [
        {
            "rule_code": "position.max_single",
            "enabled": True,
            "severity": "HARD_BLOCK",
            "params": {"max_position_pct": max_position_pct},
        }
    ]
    if _mentions(no_buy_conditions + add_conditions, "evidence", "证据"):
        rules.append(
            {
                "rule_code": "evidence.required_for_add",
                "enabled": True,
                "severity": "EVIDENCE_REQUIRED",
                "params": {},
            }
        )
    if _mentions(no_buy_conditions, "earnings", "财报"):
        rules.append(
            {
                "rule_code": "earnings.no_unplanned_add",
                "enabled": True,
                "severity": "HARD_BLOCK",
                "params": {},
            }
        )
    if _mentions(reduce_conditions + invalid_conditions, "thesis", "logic", "逻辑"):
        rules.append(
            {
                "rule_code": "thesis.review_required",
                "enabled": True,
                "severity": "REVIEW_REQUIRED",
                "params": {},
            }
        )
    return rules


def _mentions(items: list[str], *terms: str) -> bool:
    text = "\n".join(items).lower()
    return any(term.lower() in text for term in terms)


def _lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [line.strip() for line in str(value).splitlines() if line.strip()]
