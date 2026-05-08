from __future__ import annotations

from pathlib import Path
from typing import Any

from .storage import SQLiteStore


class DisciplineRepository:
    """Repository facade for v0.2 SQLite-backed persistence."""

    def __init__(self, data_dir: Path | str) -> None:
        self.store = SQLiteStore(data_dir)

    @property
    def db_path(self) -> Path:
        return self.store.db_path

    def read_document(self, name: str, default: Any) -> Any:
        return self.store.read(name, default)

    def write_document(self, name: str, data: Any) -> None:
        self.store.write(name, data)

    def append_document(self, name: str, item: Any) -> None:
        self.store.append(name, item)

    def list_settings(self) -> dict[str, Any]:
        return self.store.list_settings()

    def save_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        for key in (
            "storage_mode",
            "ai_enabled",
            "strict_mode",
            "discipline_mode",
            "ai_api_token",
            "ai_api_base_url",
            "ai_model",
        ):
            if key in settings:
                self.store.set_setting(key, settings[key])
        return self.list_settings()

    def list_data_sources(self) -> list[dict[str, Any]]:
        return self.store.list_data_sources()

    def save_data_source(self, source: dict[str, Any]) -> dict[str, Any]:
        return self.store.save_data_source(source)

    def list_capabilities(self) -> list[dict[str, Any]]:
        return self.store.list_capabilities()

    def save_capability(self, mapping: dict[str, Any]) -> dict[str, Any]:
        return self.store.save_capability(mapping)

    def save_data_sync_log(self, item: dict[str, Any]) -> dict[str, Any]:
        return self.store.save_data_sync_log(item)

    def list_data_sync_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.store.list_data_sync_logs(limit=limit)

    def save_evidence(self, item: dict[str, Any]) -> dict[str, Any]:
        return self.store.save_evidence(item)

    def list_evidence(
        self,
        symbol: str | None = None,
        evidence_type: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        return self.store.list_evidence(
            symbol=symbol,
            evidence_type=evidence_type,
            limit=limit,
        )

    def list_evidence_by_ids(self, ids: list[str]) -> list[dict[str, Any]]:
        return self.store.list_evidence_by_ids(ids)

    def save_ai_run(self, item: dict[str, Any]) -> dict[str, Any]:
        return self.store.save_ai_run(item)

    def list_ai_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.store.list_ai_runs(limit=limit)

    def save_rule_results(
        self, items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return self.store.save_rule_results(items)

    def list_rule_results(
        self,
        decision_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        return self.store.list_rule_results(decision_id=decision_id, limit=limit)

    def save_review_snapshot(self, item: dict[str, Any]) -> dict[str, Any]:
        return self.store.save_review_snapshot(item)

    def list_review_snapshots(
        self,
        period: str | None = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        return self.store.list_review_snapshots(period=period, limit=limit)

    def get_review_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        return self.store.get_review_snapshot(snapshot_id)
