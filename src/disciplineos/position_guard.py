from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .models import (
    AuditStatus,
    ExposureItem,
    InvestorProfile,
    Position,
    PositionGuardReport,
)


def build_position_guard_report(
    profile: InvestorProfile,
    positions: Iterable[Position],
) -> PositionGuardReport:
    position_list = list(positions)
    total = round(sum(position.market_value for position in position_list), 2)

    report = PositionGuardReport(
        total_market_value=total,
        positions=[
            _position_item(position, total, profile.max_single_position_pct)
            for position in position_list
        ],
        sectors=_group_items(
            position_list,
            total,
            key_name="sector",
            limit=profile.max_sector_position_pct,
        ),
        themes=_group_items(position_list, total, key_name="theme", limit=None),
        markets=_group_items(position_list, total, key_name="market", limit=None),
        currencies=_group_items(position_list, total, key_name="currency", limit=None),
    )

    report.warnings = _warnings(report)
    return report


def project_position_percent(
    positions: Iterable[Position],
    symbol: str,
    action: str,
    amount: float,
) -> tuple[float, float]:
    position_list = list(positions)
    total = sum(position.market_value for position in position_list)
    current_value = sum(
        position.market_value for position in position_list if position.symbol == symbol
    )

    before_pct = _percent(current_value, total)
    signed_amount = amount if action in {"buy", "add"} else -amount
    after_value = max(current_value + signed_amount, 0)
    after_total = total + amount if action in {"buy", "add"} else total
    after_pct = _percent(after_value, after_total)
    return before_pct, after_pct


def _position_item(position: Position, total: float, limit: float) -> ExposureItem:
    percent = _percent(position.market_value, total)
    return ExposureItem(
        key=position.symbol,
        market_value=position.market_value,
        percent=percent,
        limit=limit,
        status=_status(percent, limit),
    )


def _group_items(
    positions: list[Position],
    total: float,
    key_name: str,
    limit: float | None,
) -> list[ExposureItem]:
    groups: dict[str, float] = defaultdict(float)
    for position in positions:
        groups[str(getattr(position, key_name) or "unknown")] += position.market_value

    return sorted(
        [
            ExposureItem(
                key=key,
                market_value=round(value, 2),
                percent=_percent(value, total),
                limit=limit,
                status=_status(_percent(value, total), limit),
            )
            for key, value in groups.items()
        ],
        key=lambda item: item.market_value,
        reverse=True,
    )


def _status(percent: float, limit: float | None) -> AuditStatus:
    if limit is None:
        return AuditStatus.PASS
    if percent > limit:
        return AuditStatus.BLOCKED
    if percent > limit * 0.8:
        return AuditStatus.WARN
    return AuditStatus.PASS


def _warnings(report: PositionGuardReport) -> list[str]:
    warnings = []
    for item in [*report.positions, *report.sectors]:
        if item.status == AuditStatus.BLOCKED:
            warnings.append(f"{item.key} exposure is {item.percent:.1f}%, above {item.limit:.1f}%.")
        elif item.status == AuditStatus.WARN:
            warnings.append(f"{item.key} exposure is {item.percent:.1f}%, close to {item.limit:.1f}%.")
    return warnings


def _percent(value: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return round(value / total * 100, 2)

