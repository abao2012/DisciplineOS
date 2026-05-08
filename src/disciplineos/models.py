from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class Action(str, Enum):
    BUY = "buy"
    ADD = "add"
    REDUCE = "reduce"
    SELL = "sell"


class Emotion(str, Enum):
    CALM = "calm"
    ANXIOUS = "anxious"
    FEARFUL = "fearful"
    GREEDY = "greedy"
    REVENGE = "revenge"
    FOMO = "fomo"


class AuditStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    EVIDENCE_REQUIRED = "EVIDENCE_REQUIRED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class InvestorProfile:
    name: str
    style: str = "balanced"
    style_allocations: dict[str, float] = field(default_factory=dict)
    max_single_position_pct: float = 15
    max_sector_position_pct: float = 30
    max_drawdown_pct: float = 20
    allow_pre_earnings_add: bool = False
    behavioral_weaknesses: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DisciplineCard:
    symbol: str
    name: str
    asset_type: str
    sector: str
    thesis: list[str]
    max_position_pct: float
    no_buy_conditions: list[str] = field(default_factory=list)
    add_conditions: list[str] = field(default_factory=list)
    reduce_conditions: list[str] = field(default_factory=list)
    raise_position_conditions: list[str] = field(default_factory=list)
    lower_position_conditions: list[str] = field(default_factory=list)
    invalid_conditions: list[str] = field(default_factory=list)
    forbidden_behaviors: list[str] = field(default_factory=list)
    card_rules: list[dict[str, Any]] = field(default_factory=list)
    review_cycle: str = "monthly"


@dataclass(slots=True)
class Asset:
    symbol: str
    name: str
    asset_type: str = "stock"
    market: str = "A"
    sector: str = "unknown"
    theme: str = "unknown"
    currency: str = "CNY"


@dataclass(slots=True)
class Position:
    symbol: str
    name: str
    asset_type: str = "stock"
    market: str = "A"
    sector: str = "unknown"
    theme: str = "unknown"
    currency: str = "CNY"
    quantity: float = 0
    cost_price: float = 0
    current_price: float = 0

    @property
    def market_value(self) -> float:
        return round(max(self.quantity, 0) * max(self.current_price, 0), 2)

    @property
    def cost_value(self) -> float:
        return round(max(self.quantity, 0) * max(self.cost_price, 0), 2)

    @property
    def unrealized_pnl(self) -> float:
        return round(self.market_value - self.cost_value, 2)


@dataclass(slots=True)
class ExposureItem:
    key: str
    market_value: float
    percent: float
    limit: float | None = None
    status: AuditStatus = AuditStatus.PASS


@dataclass(slots=True)
class PositionGuardReport:
    total_market_value: float
    positions: list[ExposureItem] = field(default_factory=list)
    sectors: list[ExposureItem] = field(default_factory=list)
    themes: list[ExposureItem] = field(default_factory=list)
    markets: list[ExposureItem] = field(default_factory=list)
    currencies: list[ExposureItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Trade:
    symbol: str
    action: Action
    quantity: float = 0
    price: float = 0
    amount: float = 0
    fee: float = 0
    traded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class FinancialReportSummary:
    symbol: str
    period: str
    source: str
    material_type: str = "financial_report"
    ai_online_search: bool = False
    analysis_mode: str = "local_rules"
    ai_status: str = "not_requested"
    ai_error: str = ""
    revenue: str = ""
    profit: str = ""
    gross_margin: str = ""
    cash_flow: str = ""
    guidance: str = ""
    evidence_summary: list[str] = field(default_factory=list)
    key_insights: list[str] = field(default_factory=list)
    positive_factors: list[str] = field(default_factory=list)
    negative_factors: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    discipline_suggestions: list[str] = field(default_factory=list)
    card_suggestions: dict[str, list[str]] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class EvidenceItem:
    symbol: str
    evidence_type: str
    title: str
    content: str
    source: str = "manual"
    source_date: str = ""
    linked_decision_id: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(slots=True)
class Decision:
    symbol: str
    action: Action
    amount: float
    position_before_pct: float
    position_after_pct: float
    reason: str
    evidence: list[str] = field(default_factory=list)
    emotion: Emotion = Emotion.CALM
    is_before_earnings: bool = False
    thesis_changed: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass(slots=True)
class Violation:
    type: str
    message: str
    severity: Severity
    rule_id: str
    category: str = "general"
    remediation: str = ""
    weight: int = 0


@dataclass(slots=True)
class AuditResult:
    decision_id: str
    status: AuditStatus
    violations: list[Violation] = field(default_factory=list)
    warnings: list[Violation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def to_dict(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_dict(getattr(value, key)) for key in value.__dataclass_fields__}
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_dict(item) for key, item in value.items()}
    return value


def profile_from_dict(data: dict[str, Any]) -> InvestorProfile:
    payload = dict(data)
    payload.setdefault("style", "balanced")
    payload.setdefault("style_allocations", {})
    return InvestorProfile(**payload)


def card_from_dict(data: dict[str, Any]) -> DisciplineCard:
    return DisciplineCard(**data)


def position_from_dict(data: dict[str, Any]) -> Position:
    return Position(**data)


def trade_from_dict(data: dict[str, Any]) -> Trade:
    payload = dict(data)
    payload["action"] = Action(payload["action"])
    return Trade(**payload)


def financial_report_from_dict(data: dict[str, Any]) -> FinancialReportSummary:
    return FinancialReportSummary(**data)


def evidence_from_dict(data: dict[str, Any]) -> EvidenceItem:
    return EvidenceItem(**data)


def decision_from_dict(data: dict[str, Any]) -> Decision:
    payload = dict(data)
    payload["action"] = Action(payload["action"])
    payload["emotion"] = Emotion(payload.get("emotion", Emotion.CALM))
    return Decision(**payload)
