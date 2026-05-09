from pathlib import Path

from openpyxl import Workbook

from disciplineos.adapters import import_records
from disciplineos.services import DisciplineService


def test_import_positions_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text(
        "symbol,name,quantity,cost_price,current_price,sector\n"
        "AAA,AAA Corp,10,5,6,technology\n",
        encoding="utf-8",
    )

    result = import_records(csv_path, "positions")

    assert result.imported == 1
    assert result.items[0]["symbol"] == "AAA"
    assert result.items[0]["quantity"] == 10
    assert result.items[0]["current_price"] == 6


def test_import_positions_csv_accepts_chinese_headers_and_number_formats(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions_cn.csv"
    csv_path.write_text(
        "股票代码,股票名称,持仓数量,成本价,当前价,行业\n"
        "300750,宁德时代,\"1,000\",200.5,210.75,新能源\n",
        encoding="utf-8",
    )

    result = import_records(csv_path, "positions")

    assert result.imported == 1
    assert result.items[0]["symbol"] == "300750"
    assert result.items[0]["name"] == "宁德时代"
    assert result.items[0]["quantity"] == 1000
    assert result.items[0]["current_price"] == 210.75
    assert result.items[0]["sector"] == "新能源"


def test_import_trades_excel(tmp_path: Path) -> None:
    xlsx_path = tmp_path / "trades.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["symbol", "action", "quantity", "price", "fee", "traded_at"])
    sheet.append(["AAA", "buy", 10, 5, 1, "2026-04-10T10:00:00+00:00"])
    workbook.save(xlsx_path)

    result = import_records(xlsx_path, "trades")

    assert result.imported == 1
    assert result.items[0]["amount"] == 50


def test_import_trades_excel_accepts_chinese_headers_and_actions(tmp_path: Path) -> None:
    xlsx_path = tmp_path / "trades_cn.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["证券代码", "操作", "数量", "成交价", "手续费", "成交时间"])
    sheet.append(["300750", "买入", "100", "210.5", "1.5", "2026-05-01 10:00"])
    workbook.save(xlsx_path)

    result = import_records(xlsx_path, "trades")

    assert result.imported == 1
    assert result.items[0]["symbol"] == "300750"
    assert result.items[0]["action"] == "buy"
    assert result.items[0]["amount"] == 21050
    assert result.items[0]["fee"] == 1.5


def test_service_import_file_persists_positions(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text(
        "symbol,name,quantity,cost_price,current_price\n"
        "AAA,AAA Corp,10,5,6\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")

    result = service.import_file("positions", str(csv_path))

    assert result["imported"] == 1
    assert "AAA" in service.list_positions()


def test_service_import_preview_does_not_persist_until_confirmed(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text(
        "symbol,name,quantity,cost_price,current_price\n"
        "AAA,AAA Corp,10,5,6\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")

    preview = service.preview_import_file("positions", str(csv_path))

    assert preview["commit"] is False
    assert preview["can_import"] is True
    assert preview["row_count"] == 1
    assert preview["sample_items"][0]["symbol"] == "AAA"
    assert "AAA" not in service.list_positions()
    confirmed = service.import_file("positions", str(csv_path), commit=True)
    assert confirmed["commit"] is True
    assert "AAA" in service.list_positions()


def test_import_missing_required_columns_is_not_importable(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text(
        "symbol,name,quantity\n"
        "AAA,AAA Corp,10\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")

    result = service.import_file("positions", str(csv_path), commit=True)

    assert result["can_import"] is False
    assert result["missing_columns"] == ["cost_price", "current_price"]
    assert "AAA" not in service.list_positions()


def test_service_syncs_positions_from_mapped_provider(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text(
        "symbol,name,quantity,cost_price,current_price\n"
        "SYNC,Sync Corp,20,7,8\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_positions",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "positions",
            "provider_name": "local_positions",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability({"capability": "positions"})

    assert result["ok"] is True
    assert result["result"]["imported"] == 1
    assert "SYNC" in service.list_positions()
    assert service.list_data_sync_logs()[0]["status"] == "success"


def test_service_sync_preview_does_not_persist_positions(tmp_path: Path) -> None:
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text(
        "symbol,name,quantity,cost_price,current_price\n"
        "SYNC,Sync Corp,20,7,8\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_positions",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "positions",
            "provider_name": "local_positions",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability({"capability": "positions", "confirm": False})

    assert result["ok"] is True
    assert result["result"]["commit"] is False
    assert result["result"]["can_import"] is True
    assert "SYNC" not in service.list_positions()
    assert service.list_data_sync_logs()[0]["status"] == "preview"
