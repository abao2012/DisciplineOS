from pathlib import Path

from disciplineos.services import DisciplineService
from disciplineos.trade_reconciliation import reconcile_trades


def test_reconcile_trades_uses_moving_average_cost() -> None:
    result = reconcile_trades(
        [
            {
                "symbol": "AAA",
                "action": "buy",
                "quantity": 100,
                "price": 10,
                "fee": 1,
                "traded_at": "2026-05-01T10:00:00+00:00",
            },
            {
                "symbol": "AAA",
                "action": "add",
                "quantity": 100,
                "price": 20,
                "fee": 1,
                "traded_at": "2026-05-02T10:00:00+00:00",
            },
            {
                "symbol": "AAA",
                "action": "reduce",
                "quantity": 50,
                "price": 25,
                "fee": 1,
                "traded_at": "2026-05-03T10:00:00+00:00",
            },
        ]
    )

    ledger = result["by_symbol"]["AAA"]
    position = result["positions"]["AAA"]

    assert ledger["quantity"] == 150
    assert ledger["realized_pnl"] == 498.5
    assert position["quantity"] == 150
    assert position["cost_price"] == 15.01
    assert position["current_price"] == 25
    assert result["totals"]["cash_flow"] == -1753


def test_reconcile_trades_warns_when_sell_exceeds_position() -> None:
    result = reconcile_trades(
        [
            {
                "symbol": "AAA",
                "action": "buy",
                "quantity": 10,
                "price": 10,
                "traded_at": "2026-05-01T10:00:00+00:00",
            },
            {
                "symbol": "AAA",
                "action": "reduce",
                "quantity": 20,
                "price": 12,
                "traded_at": "2026-05-02T10:00:00+00:00",
            },
        ]
    )

    assert result["warnings"]
    assert result["positions"] == {}
    assert result["by_symbol"]["AAA"]["realized_pnl"] == 20


def test_service_import_trades_updates_position_book(tmp_path: Path) -> None:
    csv_path = tmp_path / "trades.csv"
    csv_path.write_text(
        "symbol,action,quantity,price,fee,traded_at\n"
        "AAA,buy,100,10,1,2026-05-01T10:00:00+00:00\n"
        "AAA,reduce,40,15,1,2026-05-02T10:00:00+00:00\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")

    result = service.import_file("trades", str(csv_path), commit=True)
    positions = service.list_positions()
    reconciliation = service.reconcile_trade_positions(commit=False)

    assert result["imported"] == 2
    assert result["trade_reconciliation"]["totals"]["trade_count"] == 2
    assert positions["AAA"]["quantity"] == 60
    assert positions["AAA"]["cost_price"] == 10.01
    assert reconciliation["by_symbol"]["AAA"]["realized_pnl"] == 198.6


def test_service_trade_import_preserves_manual_metadata(tmp_path: Path) -> None:
    csv_path = tmp_path / "trades.csv"
    csv_path.write_text(
        "symbol,action,quantity,price,traded_at\n"
        "AAA,buy,10,5,2026-05-01T10:00:00+00:00\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_position_dict(
        {
            "symbol": "AAA",
            "name": "AAA Corp",
            "asset_type": "stock",
            "market": "创业板",
            "sector": "新能源",
            "theme": "储能",
            "currency": "CNY",
            "quantity": 1,
            "cost_price": 1,
            "current_price": 1,
        }
    )

    service.import_file("trades", str(csv_path), commit=True)
    position = service.list_positions()["AAA"]

    assert position["name"] == "AAA Corp"
    assert position["market"] == "创业板"
    assert position["sector"] == "新能源"
    assert position["quantity"] == 10
