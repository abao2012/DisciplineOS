from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import Action, Position, Trade, to_dict, trade_from_dict


@dataclass(slots=True)
class SymbolLedger:
    symbol: str
    quantity: float = 0
    cost_basis: float = 0
    realized_pnl: float = 0
    fees: float = 0
    buy_amount: float = 0
    sell_amount: float = 0
    trade_count: int = 0
    last_price: float = 0
    last_traded_at: str = ""
    warnings: list[str] = field(default_factory=list)

    @property
    def cost_price(self) -> float:
        return round(self.cost_basis / self.quantity, 6) if self.quantity > 0 else 0.0

    @property
    def market_value(self) -> float:
        return round(max(self.quantity, 0) * max(self.last_price, 0), 2)

    @property
    def unrealized_pnl(self) -> float:
        return round(self.market_value - max(self.cost_basis, 0), 2)


def reconcile_trades(
    trades: list[dict[str, Any] | Trade],
    *,
    position_metadata: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    ledgers: dict[str, SymbolLedger] = {}
    warnings: list[str] = []
    cash_flow = 0.0
    parsed_trades = [_coerce_trade(item) for item in trades]

    for trade in sorted(parsed_trades, key=_trade_sort_key):
        symbol = trade.symbol.upper()
        ledger = ledgers.setdefault(symbol, SymbolLedger(symbol=symbol))
        amount = _trade_amount(trade)
        fee = max(float(trade.fee or 0), 0.0)
        quantity = max(float(trade.quantity or 0), 0.0)
        price = float(trade.price or 0)

        ledger.trade_count += 1
        ledger.fees = round(ledger.fees + fee, 2)
        if price > 0:
            ledger.last_price = price
        if trade.traded_at:
            ledger.last_traded_at = trade.traded_at

        if trade.action in {Action.BUY, Action.ADD}:
            ledger.quantity = round(ledger.quantity + quantity, 6)
            ledger.cost_basis = round(ledger.cost_basis + amount + fee, 2)
            ledger.buy_amount = round(ledger.buy_amount + amount + fee, 2)
            cash_flow = round(cash_flow - amount - fee, 2)
            continue

        if trade.action in {Action.REDUCE, Action.SELL}:
            if quantity > ledger.quantity:
                message = (
                    f"{symbol} sell quantity {quantity} exceeds current quantity "
                    f"{round(ledger.quantity, 6)}."
                )
                ledger.warnings.append(message)
                warnings.append(message)
            sold_quantity = min(quantity, ledger.quantity)
            avg_cost = ledger.cost_price
            cost_removed = round(avg_cost * sold_quantity, 2)
            proceeds_ratio = sold_quantity / quantity if quantity else 0
            effective_amount = round(amount * proceeds_ratio, 2)
            effective_fee = round(fee * proceeds_ratio, 2)
            proceeds = round(effective_amount - effective_fee, 2)
            ledger.quantity = round(ledger.quantity - sold_quantity, 6)
            ledger.cost_basis = round(max(ledger.cost_basis - cost_removed, 0), 2)
            ledger.realized_pnl = round(ledger.realized_pnl + proceeds - cost_removed, 2)
            ledger.sell_amount = round(ledger.sell_amount + proceeds, 2)
            cash_flow = round(cash_flow + proceeds, 2)
            if trade.action == Action.SELL or ledger.quantity <= 0:
                ledger.quantity = 0.0
                ledger.cost_basis = 0.0
            continue

        message = f"{symbol} unsupported trade action: {trade.action}"
        ledger.warnings.append(message)
        warnings.append(message)

    positions = _ledgers_to_positions(ledgers, position_metadata or {})
    totals = {
        "cash_flow": round(cash_flow, 2),
        "realized_pnl": round(sum(item.realized_pnl for item in ledgers.values()), 2),
        "unrealized_pnl": round(sum(item.unrealized_pnl for item in ledgers.values()), 2),
        "fees": round(sum(item.fees for item in ledgers.values()), 2),
        "market_value": round(sum(item.market_value for item in ledgers.values()), 2),
        "open_position_count": len(positions),
        "trade_count": len(parsed_trades),
    }
    return {
        "positions": positions,
        "by_symbol": {
            symbol: _ledger_to_dict(ledger)
            for symbol, ledger in sorted(ledgers.items())
        },
        "totals": totals,
        "warnings": warnings,
    }


def _ledgers_to_positions(
    ledgers: dict[str, SymbolLedger],
    position_metadata: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    positions: dict[str, dict[str, Any]] = {}
    for symbol, ledger in sorted(ledgers.items()):
        if ledger.quantity <= 0:
            continue
        metadata = position_metadata.get(symbol, {})
        position = Position(
            symbol=symbol,
            name=str(metadata.get("name") or symbol),
            asset_type=str(metadata.get("asset_type") or "stock"),
            market=str(metadata.get("market") or "A"),
            sector=str(metadata.get("sector") or "unknown"),
            theme=str(metadata.get("theme") or "unknown"),
            currency=str(metadata.get("currency") or "CNY"),
            quantity=ledger.quantity,
            cost_price=ledger.cost_price,
            current_price=ledger.last_price or float(metadata.get("current_price") or 0),
        )
        positions[symbol] = to_dict(position)
    return positions


def _ledger_to_dict(ledger: SymbolLedger) -> dict[str, Any]:
    return {
        "symbol": ledger.symbol,
        "quantity": ledger.quantity,
        "cost_basis": ledger.cost_basis,
        "cost_price": ledger.cost_price,
        "last_price": ledger.last_price,
        "market_value": ledger.market_value,
        "realized_pnl": round(ledger.realized_pnl, 2),
        "unrealized_pnl": ledger.unrealized_pnl,
        "fees": round(ledger.fees, 2),
        "buy_amount": round(ledger.buy_amount, 2),
        "sell_amount": round(ledger.sell_amount, 2),
        "trade_count": ledger.trade_count,
        "last_traded_at": ledger.last_traded_at,
        "warnings": ledger.warnings,
    }


def _coerce_trade(item: dict[str, Any] | Trade) -> Trade:
    if isinstance(item, Trade):
        return item
    return trade_from_dict(dict(item))


def _trade_sort_key(trade: Trade) -> tuple[str, str]:
    return (trade.traded_at or "", trade.id)


def _trade_amount(trade: Trade) -> float:
    amount = float(trade.amount or 0)
    if amount:
        return amount
    return round(float(trade.quantity or 0) * float(trade.price or 0), 2)
