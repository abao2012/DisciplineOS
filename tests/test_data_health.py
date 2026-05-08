from disciplineos.services import DisciplineService, seed_demo_data


def test_data_health_warns_until_backup_exists(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)

    before = service.data_health_check()
    service.create_backup()
    after = service.data_health_check()

    before_backup = _check_by_title(before, "Local backup archive")
    after_backup = _check_by_title(after, "Local backup archive")
    assert before_backup["status"] == "WARN"
    assert after_backup["status"] == "PASS"
    assert after["status"] == "PASS"


def test_data_health_warns_for_report_with_missing_snapshot(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    service.create_backup()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    reports_dir.joinpath("orphan.md").write_text(
        "# DisciplineOS Monthly Review 2026-05\n\n"
        "- Snapshot ID: missing-snapshot\n",
        encoding="utf-8",
    )

    health = service.data_health_check()
    report_check = _check_by_title(health, "Report snapshot references")

    assert report_check["status"] == "WARN"
    assert health["status"] == "WARN"


def _check_by_title(health: dict, title: str) -> dict:
    return next(item for item in health["checks"] if item["title"] == title)
