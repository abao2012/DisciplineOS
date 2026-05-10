from pathlib import Path
import types

import disciplineos.services as services_module
from disciplineos.connectors import build_connector
from disciplineos.connectors import ConnectorResult
from disciplineos.services import DisciplineService


def test_csv_connector_previews_price_daily_as_evidence(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close,change_pct\n"
        "AAA,2026-05-01,12.5,2.1\n",
        encoding="utf-8",
    )
    source = {
        "provider_name": "local_prices",
        "provider_type": "csv",
        "config": {"local_path": str(csv_path)},
    }

    result = build_connector(source).preview("price_daily")

    assert result.imported == 1
    assert result.items[0]["evidence_type"] == "price_condition"
    assert result.items[0]["symbol"] == "AAA"
    assert "close=12.5" in result.items[0]["content"]
    assert result.market_records[0]["data_type"] == "price_daily"
    assert result.market_records[0]["fields"]["close"] == 12.5


def test_csv_connector_accepts_chinese_market_headers(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices_cn.csv"
    csv_path.write_text(
        "股票代码,日期,收盘价,涨跌幅,成交量\n"
        "300750,2026-05-01,210.5,2.1%,\"10,000\"\n",
        encoding="utf-8",
    )
    source = {
        "provider_name": "local_prices",
        "provider_type": "csv",
        "config": {"local_path": str(csv_path)},
    }

    result = build_connector(source).preview("price_daily")

    assert result.imported == 1
    assert result.items[0]["symbol"] == "300750"
    assert "change_pct=2.1" in result.items[0]["content"]
    assert result.market_records[0]["fields"]["close"] == 210.5
    assert result.market_records[0]["fields"]["volume"] == 10000.0


def test_service_syncs_price_daily_to_evidence_after_confirm(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close,change_pct\n"
        "AAA,2026-05-01,12.5,2.1\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    preview = service.sync_capability({"capability": "price_daily", "confirm": False})
    evidence_after_preview = service.list_evidence(
        symbol="AAA",
        evidence_type="price_condition",
    )
    confirmed = service.sync_capability({"capability": "price_daily", "confirm": True})

    assert preview["result"]["commit"] is False
    assert preview["result"]["can_import"] is True
    assert evidence_after_preview == []
    assert confirmed["result"]["commit"] is True
    assert confirmed["result"]["imported"] == 1
    assert confirmed["result"]["market_record_count"] == 1
    assert service.list_evidence(symbol="AAA", evidence_type="price_condition")
    market_records = service.list_market_records(symbol="AAA", data_type="price_daily")
    assert market_records[0]["fields"]["close"] == 12.5
    assert service.market_data_summary()["by_type"][0]["row_count"] == 1


def test_service_upserts_market_records_when_sync_repeats(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close,change_pct\n"
        "AAA,2026-05-01,12.5,2.1\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    service.sync_capability({"capability": "price_daily", "confirm": True})
    csv_path.write_text(
        "symbol,date,close,change_pct\n"
        "AAA,2026-05-01,13.5,3.1\n",
        encoding="utf-8",
    )
    service.sync_capability({"capability": "price_daily", "confirm": True})

    market_records = service.list_market_records(symbol="AAA", data_type="price_daily")
    assert len(market_records) == 1
    assert market_records[0]["fields"]["close"] == 13.5


def test_service_sync_state_and_evidence_are_idempotent(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close\n"
        "AAA,2026-05-01,12.5\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    first = service.sync_capability({"capability": "price_daily", "confirm": True})
    second = service.sync_capability({"capability": "price_daily", "confirm": True})

    evidence = service.list_evidence(symbol="AAA", evidence_type="price_condition")
    sync_state = service.list_data_sync_state()[0]
    assert first["sync_state"]["last_source_timestamp"] == "2026-05-01"
    assert second["sync_state"]["row_count"] == 1
    assert len(evidence) == 1
    assert sync_state["provider_name"] == "local_prices"
    assert sync_state["capability"] == "price_daily"


def test_price_sync_updates_existing_position_current_price(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close\n"
        "AAA,2026-05-01,12.5\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_position_dict(
        {
            "symbol": "AAA",
            "name": "AAA Corp",
            "quantity": 100,
            "cost_price": 10,
            "current_price": 9,
        }
    )
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability({"capability": "price_daily", "confirm": True})
    position = service.list_positions()["AAA"]

    assert result["result"]["position_price_update"]["updated_count"] == 1
    assert position["current_price"] == 12.5
    assert service.position_guard()["total_market_value"] == 1250


def test_service_sync_filters_market_data_by_symbol(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close\n"
        "AAA,2026-05-01,12.5\n"
        "BBB,2026-05-01,8.5\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability(
        {"capability": "price_daily", "confirm": True, "symbol": "BBB"}
    )

    assert result["result"]["imported"] == 1
    assert service.list_evidence(symbol="AAA") == []
    assert service.list_evidence(symbol="BBB", evidence_type="price_condition")
    assert service.list_market_records(symbol="AAA") == []
    assert service.list_market_records(symbol="BBB")[0]["fields"]["close"] == 8.5


def test_service_enforces_sync_rate_limit_and_preserves_last_success(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close\n"
        "AAA,2026-05-01,12.5\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {
                "local_path": str(csv_path),
                "min_interval_seconds": 3600,
            },
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    first = service.sync_capability({"capability": "price_daily", "confirm": True})
    second = service.sync_capability({"capability": "price_daily", "confirm": True})
    sync_state = service.list_data_sync_state()[0]

    assert first["ok"] is True
    assert second["ok"] is False
    assert "rate limit" in second["result"]["errors"][0]
    assert sync_state["status"] == "error"
    assert sync_state["last_success_at"] == first["sync_state"]["last_success_at"]


def test_service_enforces_daily_sync_quota(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date,close\n"
        "AAA,2026-05-01,12.5\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {
                "local_path": str(csv_path),
                "max_syncs_per_day": 1,
            },
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    service.sync_capability({"capability": "price_daily", "confirm": True})
    result = service.sync_capability({"capability": "price_daily", "confirm": True})

    assert result["ok"] is False
    assert "quota exceeded" in result["result"]["errors"][0]


def test_service_retries_transient_connector_errors(tmp_path: Path, monkeypatch) -> None:
    calls: list[str] = []

    class FlakyConnector:
        def preview(self, capability: str) -> ConnectorResult:
            calls.append(capability)
            if len(calls) == 1:
                return ConnectorResult(
                    provider_name="local_prices",
                    provider_type="csv",
                    capability=capability,
                    source="test",
                    errors=["temporary failure"],
                )
            return ConnectorResult(
                provider_name="local_prices",
                provider_type="csv",
                capability=capability,
                source="test",
                row_count=1,
                imported=1,
                items=[
                    {
                        "symbol": "AAA",
                        "evidence_type": "price_condition",
                        "title": "2026-05-01 close",
                        "content": "close=12.5",
                        "source": "test",
                        "source_date": "2026-05-01",
                    }
                ],
                market_records=[
                    {
                        "provider_name": "local_prices",
                        "provider_type": "csv",
                        "data_type": "price_daily",
                        "symbol": "AAA",
                        "timestamp": "2026-05-01",
                        "fields": {"close": 12.5},
                        "source": "test",
                    }
                ],
            )

    monkeypatch.setattr(
        services_module,
        "build_connector",
        lambda source: FlakyConnector(),
    )
    source_path = tmp_path / "prices.csv"
    source_path.write_text("symbol,date,close\n", encoding="utf-8")
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "local_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(source_path), "max_retries": 1},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "local_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability({"capability": "price_daily", "confirm": True})

    assert result["ok"] is True
    assert result["result"]["attempts"] == 2
    assert calls == ["price_daily", "price_daily"]


def test_csv_connector_previews_5min_k_as_evidence(tmp_path: Path) -> None:
    csv_path = tmp_path / "5min.csv"
    csv_path.write_text(
        "symbol,datetime,close,volume\n"
        "AAA,2026-05-01 09:35,12.5,10000\n",
        encoding="utf-8",
    )
    source = {
        "provider_name": "local_5min",
        "provider_type": "csv",
        "config": {"local_path": str(csv_path)},
    }

    result = build_connector(source).preview("price_5min")

    assert result.imported == 1
    assert result.items[0]["title"] == "2026-05-01 09:35 5min K"
    assert "volume=10000" in result.items[0]["content"]
    assert result.market_records[0]["timestamp"] == "2026-05-01 09:35"


def test_market_connector_missing_columns_is_not_importable(tmp_path: Path) -> None:
    csv_path = tmp_path / "prices.csv"
    csv_path.write_text(
        "symbol,date\n"
        "AAA,2026-05-01\n",
        encoding="utf-8",
    )
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "bad_prices",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "bad_prices",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability({"capability": "price_daily", "confirm": True})

    assert result["result"]["can_import"] is False
    assert result["result"]["missing_columns"] == ["close"]
    assert service.list_evidence(symbol="AAA") == []


class _FakeFrame:
    def __init__(self, records: list[dict]) -> None:
        self.records = records

    def to_dict(self, orient: str) -> list[dict]:
        assert orient == "records"
        return self.records


def test_akshare_connector_previews_daily_price(monkeypatch) -> None:
    fake = types.SimpleNamespace(
        stock_zh_a_hist=lambda **kwargs: _FakeFrame(
            [{"日期": "2026-05-01", "收盘": 12.5, "涨跌幅": 2.1, "成交量": 10000}]
        )
    )
    monkeypatch.setitem(__import__("sys").modules, "akshare", fake)
    source = {
        "provider_name": "ak",
        "provider_type": "akshare",
        "config": {"symbol": "300750"},
    }

    result = build_connector(source).preview("price_daily")

    assert result.imported == 1
    assert result.items[0]["symbol"] == "300750"
    assert result.items[0]["source"] == "ak"
    assert "change_pct=2.1" in result.items[0]["content"]
    assert result.market_records[0]["fields"]["volume"] == 10000.0


def test_tushare_connector_previews_daily_price(monkeypatch) -> None:
    class FakePro:
        def daily(self, **kwargs):
            assert kwargs["ts_code"] == "300750.SZ"
            return _FakeFrame(
                [{"trade_date": "20260501", "close": 12.5, "pct_chg": 2.1, "vol": 10000}]
            )

    fake = types.SimpleNamespace(
        set_token=lambda token: None,
        pro_api=lambda token: FakePro(),
    )
    monkeypatch.setitem(__import__("sys").modules, "tushare", fake)
    source = {
        "provider_name": "ts",
        "provider_type": "tushare",
        "config": {"symbol": "300750", "api_token": "fake-token"},
    }

    result = build_connector(source).preview("price_daily")

    assert result.imported == 1
    assert result.items[0]["symbol"] == "300750"
    assert result.items[0]["source_date"] == "2026-05-01"
    assert result.market_records[0]["timestamp"] == "2026-05-01"


def test_service_syncs_fake_akshare_with_symbol_filter(tmp_path: Path, monkeypatch) -> None:
    fake = types.SimpleNamespace(
        stock_zh_a_hist=lambda **kwargs: _FakeFrame(
            [{"日期": "2026-05-01", "收盘": 12.5, "涨跌幅": 2.1, "成交量": 10000}]
        )
    )
    monkeypatch.setitem(__import__("sys").modules, "akshare", fake)
    monkeypatch.setattr("importlib.util.find_spec", lambda name: object() if name == "akshare" else None)
    service = DisciplineService(tmp_path / "data")
    service.save_data_source(
        {
            "provider_name": "ak",
            "provider_type": "akshare",
            "enabled": True,
            "priority": 10,
            "config": {},
        }
    )
    service.save_capability(
        {
            "capability": "price_daily",
            "provider_name": "ak",
            "fallback_provider": "",
            "priority": 10,
        }
    )

    result = service.sync_capability(
        {"capability": "price_daily", "confirm": True, "symbol": "300750"}
    )

    assert result["ok"] is True
    assert result["result"]["imported"] == 1
    assert service.list_evidence(symbol="300750", evidence_type="price_condition")
    assert service.list_market_records(symbol="300750", data_type="price_daily")
