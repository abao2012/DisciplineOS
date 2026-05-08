from pathlib import Path

from disciplineos.services import DisciplineService


def test_sqlite_store_is_created_and_keeps_legacy_json_export(tmp_path: Path) -> None:
    service = DisciplineService(tmp_path)

    service.save_profile_dict(
        {
            "name": "tester",
            "style": "value",
            "max_single_position_pct": 15,
            "max_sector_position_pct": 30,
            "max_drawdown_pct": 20,
            "allow_pre_earnings_add": False,
            "behavioral_weaknesses": [],
        }
    )

    assert (tmp_path / "disciplineos.db").exists()
    assert (tmp_path / "profile.json").exists()
    assert service.load_profile().name == "tester"


def test_settings_and_data_source_configuration_persist(tmp_path: Path) -> None:
    service = DisciplineService(tmp_path)

    settings = service.save_settings(
        {
            "storage_mode": "sqlite",
            "ai_enabled": True,
            "strict_mode": False,
            "discipline_mode": "warn",
            "ai_api_token": "token-123",
            "ai_api_base_url": "https://api.example.test/v1",
            "ai_model": "test-model",
        }
    )
    source = service.save_data_source(
        {
            "provider_name": "manual",
            "provider_type": "manual",
            "enabled": True,
            "priority": 10,
            "config": {},
        }
    )
    service.save_capability(
        {
            "capability": "positions",
            "provider_name": "manual",
            "fallback_provider": "csv",
            "priority": 10,
        }
    )

    reloaded = DisciplineService(tmp_path)
    assert settings["ai_enabled"] is True
    assert settings["discipline_mode"] == "warn"
    assert settings["ai_api_token"] == "token-123"
    assert settings["ai_api_base_url"] == "https://api.example.test/v1"
    assert settings["ai_model"] == "test-model"
    assert source["test_status"] == "ok"
    assert reloaded.list_settings()["strict_mode"] is False
    assert reloaded.list_data_sources()[0]["provider_name"] == "manual"
    assert reloaded.list_capabilities()[0]["fallback_provider"] == "csv"


def test_provider_statuses_are_specific(tmp_path: Path) -> None:
    service = DisciplineService(tmp_path)
    csv_path = tmp_path / "positions.csv"
    csv_path.write_text("symbol,name,quantity,cost_price,current_price\n", encoding="utf-8")

    csv_source = service.save_data_source(
        {
            "provider_name": "csv_ready",
            "provider_type": "csv",
            "enabled": True,
            "priority": 10,
            "config": {"local_path": str(csv_path)},
        }
    )
    missing_token = service.save_data_source(
        {
            "provider_name": "tushare_missing",
            "provider_type": "tushare",
            "enabled": True,
            "priority": 20,
            "config": {},
        }
    )
    qmt_missing = service.save_data_source(
        {
            "provider_name": "qmt_missing",
            "provider_type": "qmt",
            "enabled": True,
            "priority": 30,
            "config": {"local_path": str(tmp_path / "missing")},
        }
    )

    assert csv_source["test_status"] == "ok"
    assert missing_token["test_status"] == "blocked"
    assert "api_token" in missing_token["test_message"]
    assert qmt_missing["test_status"] == "blocked"
