import zipfile

import pytest

from disciplineos.services import DisciplineService, seed_demo_data


def test_backup_restore_round_trip_restores_data(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    backup = service.create_backup()

    service.save_profile_dict(
        {
            "name": "changed",
            "style": "momentum",
            "max_single_position_pct": 5,
            "max_sector_position_pct": 10,
            "max_drawdown_pct": 8,
            "allow_pre_earnings_add": True,
            "behavioral_weaknesses": ["fomo"],
        }
    )
    assert service.load_profile().name == "changed"

    restored = service.restore_backup(backup["filename"])

    assert restored["restored_count"] > 0
    assert service.load_profile().name == "default"
    assert service.list_backups()[0]["filename"] == backup["filename"]


def test_restore_rejects_unsafe_backup_entries(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    backups_dir = tmp_path / "backups"
    backups_dir.mkdir()
    unsafe = backups_dir / "unsafe.zip"
    with zipfile.ZipFile(unsafe, "w") as archive:
        archive.writestr("../outside.txt", "bad")

    with pytest.raises(ValueError):
        service.restore_backup("unsafe.zip")
