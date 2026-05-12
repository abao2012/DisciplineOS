from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from .ai_guardrails import input_hash, sanitize_ai_output
from .models import (
    AuditResult,
    Action,
    Decision,
    DisciplineCard,
    Emotion,
    EvidenceItem,
    FinancialReportSummary,
    InvestorProfile,
    Position,
    Trade,
    card_from_dict,
    decision_from_dict,
    evidence_from_dict,
    position_from_dict,
    profile_from_dict,
    to_dict,
    trade_from_dict,
)
from .adapters import import_records
from .ai_analysis import analyze_information_with_ai
from .card_generator import generate_card_from_answers, list_card_templates
from .connectors import build_connector
from .copilot import build_copilot_summary
from .financial_report import (
    apply_analysis_payload,
    read_document_text,
    summarize_financial_report,
    summarize_financial_report_text,
)
from .position_guard import build_position_guard_report, project_position_percent
from .review_engine import build_review_attribution, build_rule_revision_suggestions
from .rules import build_rule_results, evaluate_decision, list_rule_specs
from .scoring import calculate_discipline_score
from .repositories import DisciplineRepository
from .trade_reconciliation import reconcile_trades
from .violation_catalog import VIOLATION_CATALOG


class DisciplineService:
    def __init__(self, data_dir: Path | str) -> None:
        self.repository = DisciplineRepository(data_dir)
        self.store = self.repository.store

    def save_profile(self, profile: InvestorProfile) -> None:
        self.store.write("profile.json", to_dict(profile))

    def save_profile_dict(self, payload: dict) -> InvestorProfile:
        allocations = payload.get("style_allocations") or {}
        total = sum(float(value or 0) for value in allocations.values())
        if total > 100:
            raise ValueError("Style allocation total cannot exceed 100%.")
        profile = profile_from_dict(payload)
        self.save_profile(profile)
        return profile

    def load_profile(self) -> InvestorProfile:
        return profile_from_dict(self.store.read("profile.json", _default_profile()))

    def list_cards(self) -> dict:
        return self.store.read("cards.json", {})

    def list_card_templates(self) -> dict:
        return list_card_templates()

    def list_settings(self) -> dict:
        return self.repository.list_settings()

    def save_settings(self, payload: dict) -> dict:
        settings = {
            "storage_mode": str(payload.get("storage_mode", "sqlite")),
            "ai_enabled": bool(payload.get("ai_enabled", False)),
            "strict_mode": bool(payload.get("strict_mode", True)),
            "discipline_mode": str(payload.get("discipline_mode", "block")),
            "ai_api_token": str(payload.get("ai_api_token", "")),
            "ai_api_base_url": str(payload.get("ai_api_base_url", "")),
            "ai_model": str(payload.get("ai_model", "")),
        }
        return self.repository.save_settings(settings)

    def list_data_sources(self) -> list[dict]:
        return self.repository.list_data_sources()

    def save_data_source(self, payload: dict) -> dict:
        source = {
            "provider_name": str(payload.get("provider_name", "")).strip(),
            "provider_type": str(payload.get("provider_type", "")).strip(),
            "enabled": bool(payload.get("enabled", True)),
            "priority": int(payload.get("priority", 100)),
            "config": dict(payload.get("config", {})),
        }
        return self.repository.save_data_source(source)

    def list_capabilities(self) -> list[dict]:
        return self.repository.list_capabilities()

    def list_data_sync_logs(self, limit: int = 20) -> list[dict]:
        return self.repository.list_data_sync_logs(limit=limit)

    def list_data_sync_state(self) -> list[dict]:
        return self.repository.list_data_sync_state()

    def list_market_records(
        self,
        symbol: str | None = None,
        data_type: str | None = None,
        limit: int = 200,
    ) -> list[dict]:
        return self.repository.list_market_records(
            symbol=symbol,
            data_type=data_type,
            limit=limit,
        )

    def market_data_summary(self) -> dict:
        return self.repository.market_data_summary()

    def list_schema_migrations(self) -> list[dict]:
        return self.repository.list_schema_migrations()

    def schema_status(self) -> dict:
        return self.repository.schema_status()

    def update_position_prices_from_market_data(
        self,
        symbols: list[str] | None = None,
    ) -> dict:
        positions = self.list_positions()
        target_symbols = {
            str(symbol).strip().upper()
            for symbol in (symbols or positions.keys())
            if str(symbol).strip()
        }
        if not positions or not target_symbols:
            return {
                "updated_count": 0,
                "updated": [],
                "skipped": [],
                "warnings": [],
            }

        latest_prices: dict[str, dict] = {}
        for data_type in ("price_5min", "price_daily"):
            records = self.list_market_records(data_type=data_type, limit=1000)
            for record in records:
                symbol = str(record.get("symbol", "")).strip().upper()
                if symbol not in target_symbols:
                    continue
                close = _market_close(record)
                if close is None:
                    continue
                existing = latest_prices.get(symbol)
                if existing and str(existing.get("timestamp", "")) >= str(
                    record.get("timestamp", "")
                ):
                    continue
                latest_prices[symbol] = {
                    "symbol": symbol,
                    "data_type": data_type,
                    "timestamp": str(record.get("timestamp", "")),
                    "price": close,
                    "provider_name": str(record.get("provider_name", "")),
                }

        updated = []
        skipped = []
        for symbol in sorted(target_symbols):
            if symbol not in positions:
                skipped.append({"symbol": symbol, "reason": "no_position"})
                continue
            latest = latest_prices.get(symbol)
            if not latest:
                skipped.append({"symbol": symbol, "reason": "no_market_price"})
                continue
            position = dict(positions[symbol])
            old_price = float(position.get("current_price") or 0)
            position["current_price"] = latest["price"]
            positions[symbol] = position
            updated.append(
                {
                    **latest,
                    "old_price": old_price,
                    "new_price": latest["price"],
                }
            )
        if updated:
            self.store.write("positions.json", positions)
        return {
            "updated_count": len(updated),
            "updated": updated,
            "skipped": skipped,
            "warnings": [],
        }

    def save_capability(self, payload: dict) -> dict:
        mapping = {
            "capability": str(payload.get("capability", "")).strip(),
            "provider_name": str(payload.get("provider_name", "")).strip(),
            "fallback_provider": str(payload.get("fallback_provider", "")).strip(),
            "enabled": bool(payload.get("enabled", True)),
            "priority": int(payload.get("priority", 100)),
        }
        return self.repository.save_capability(mapping)

    def sync_capability(self, payload: dict) -> dict:
        capability = str(payload.get("capability", "")).strip()
        confirm = bool(payload.get("confirm", True))
        if capability not in {
            "positions",
            "trades",
            "price_daily",
            "price_5min",
            "volume",
            "financial_metrics",
        }:
            raise ValueError(
                f"Capability {capability or '<empty>'} is not importable yet. "
                "Supported: positions, trades, price_daily, price_5min, volume, financial_metrics."
            )
        symbol_filter = str(payload.get("symbol") or "").strip().upper()
        mapping = self._resolve_capability_mapping(capability)
        source = self._source_by_name(mapping["provider_name"])
        sync_policy = _sync_policy(source)

        started_at = datetime.now(timezone.utc).isoformat()
        try:
            if confirm:
                self._enforce_sync_budget(
                    source=source,
                    capability=capability,
                    symbol=symbol_filter,
                    sync_policy=sync_policy,
                )
            result, attempts = self._sync_from_connector_with_retries(
                source,
                capability,
                commit=confirm,
                symbol_filter=symbol_filter,
                max_retries=sync_policy["max_retries"],
            )
            if not confirm:
                status = "preview"
                action = "Previewed"
            else:
                status = "success" if not result.get("errors") else "partial"
                action = "Imported"
            message = (
                f"{action} {result.get('imported', 0)} {capability}; "
                f"skipped {result.get('skipped', 0)} from {result.get('source', '')}."
            )
            if attempts > 1:
                message += f" Attempts: {attempts}."
            result["attempts"] = attempts
        except Exception as exc:
            status = "error"
            message = str(exc)
            result = {
                "kind": capability,
                "source": str(source.get("config", {}).get("local_path", "")),
                "imported": 0,
                "skipped": 0,
                "errors": [message],
                "items": [],
                "attempts": 1,
            }
        finished_at = datetime.now(timezone.utc).isoformat()
        log = self.repository.save_data_sync_log(
            {
                "provider_name": source["provider_name"],
                "sync_type": capability,
                "status": status,
                "message": message,
                "started_at": started_at,
                "finished_at": finished_at,
            }
        )
        sync_state = None
        if confirm:
            sync_state = self.repository.save_data_sync_state(
                {
                    "provider_name": source["provider_name"],
                    "capability": capability,
                    "symbol": symbol_filter,
                    "status": status,
                    "row_count": result.get("imported", 0),
                    "last_success_at": finished_at if status != "error" else "",
                    "last_error": message if status == "error" else "",
                    "last_source_timestamp": _last_source_timestamp(result),
                }
            )
        return {
            "ok": status != "error",
            "capability": capability,
            "provider": source,
            "mapping": mapping,
            "result": result,
            "sync_log": log,
            "sync_state": sync_state,
        }

    def list_evidence(
        self,
        symbol: str | None = None,
        evidence_type: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        return self.repository.list_evidence(
            symbol=symbol,
            evidence_type=evidence_type,
            limit=limit,
        )

    def list_evidence_by_ids(self, ids: list[str]) -> list[dict]:
        return self.repository.list_evidence_by_ids(ids)

    def save_evidence(self, evidence: EvidenceItem) -> dict:
        return self.repository.save_evidence(to_dict(evidence))

    def save_evidence_dict(self, payload: dict) -> dict:
        evidence_payload = {
            "symbol": str(payload.get("symbol", "")).upper(),
            "evidence_type": str(payload.get("evidence_type", "user_note")),
            "title": str(payload.get("title", "")),
            "content": str(payload.get("content", "")),
            "source": str(payload.get("source", "manual")),
            "source_date": str(payload.get("source_date", "")),
            "linked_decision_id": str(payload.get("linked_decision_id", "")),
        }
        if payload.get("id"):
            evidence_payload["id"] = str(payload["id"])
        if payload.get("created_at"):
            evidence_payload["created_at"] = str(payload["created_at"])
        evidence = evidence_from_dict(evidence_payload)
        return self.save_evidence(evidence)

    def list_ai_runs(self, limit: int = 20) -> list[dict]:
        return self.repository.list_ai_runs(limit=limit)

    def list_rule_results(
        self, decision_id: str | None = None, limit: int = 200
    ) -> list[dict]:
        return self.repository.list_rule_results(decision_id=decision_id, limit=limit)

    def list_review_snapshots(
        self, month: str | None = None, limit: int = 12
    ) -> list[dict]:
        return self.repository.list_review_snapshots(period=month, limit=limit)

    def get_review_snapshot(self, snapshot_id: str) -> dict | None:
        return self.repository.get_review_snapshot(snapshot_id)

    def list_review_reports(self, limit: int = 20) -> list[dict]:
        reports_dir = self.store.data_dir / "reports"
        if not reports_dir.exists():
            return []
        reports = []
        for path in reports_dir.glob("*.md"):
            metadata = _parse_report_metadata(path)
            stat = path.stat()
            reports.append(
                {
                    "path": str(path),
                    "filename": path.name,
                    "bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).isoformat(),
                    **metadata,
                }
            )
        return sorted(
            reports,
            key=lambda item: item["modified_at"],
            reverse=True,
        )[:limit]

    def list_backups(self, limit: int = 20) -> list[dict]:
        backups_dir = self.store.data_dir / "backups"
        if not backups_dir.exists():
            return []
        backups = []
        for path in backups_dir.glob("*.zip"):
            stat = path.stat()
            metadata = _read_backup_manifest(path)
            backups.append(
                {
                    "path": str(path),
                    "filename": path.name,
                    "bytes": stat.st_size,
                    "created_at": metadata.get(
                        "created_at",
                        datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat(),
                    ),
                    "file_count": metadata.get("file_count", 0),
                    "format": metadata.get("format", "zip"),
                }
            )
        return sorted(
            backups,
            key=lambda item: item["created_at"],
            reverse=True,
        )[:limit]

    def data_health_check(self) -> dict:
        checks: list[dict] = []
        _add_health_check(
            checks,
            "storage",
            "SQLite database",
            "PASS" if self.repository.db_path.exists() else "BLOCKED",
            str(self.repository.db_path),
        )
        decisions = self.store.read("decisions.json", [])
        decision_ids = {item.get("id") for item in decisions}
        audits = self.store.read("audits.json", [])
        audit_decision_ids = {item.get("decision_id") for item in audits}
        rule_results = self.list_rule_results(limit=10000)
        rule_decision_ids = {item.get("decision_id") for item in rule_results}
        violations = self.store.read("violations.json", [])

        _add_health_check(
            checks,
            "audit",
            "Decision and audit linkage",
            "WARN" if decision_ids - audit_decision_ids else "PASS",
            f"{len(decision_ids - audit_decision_ids)} decisions have no audit record.",
        )
        _add_health_check(
            checks,
            "rules",
            "Rule result linkage",
            "WARN" if audit_decision_ids - rule_decision_ids else "PASS",
            f"{len(audit_decision_ids - rule_decision_ids)} audited decisions have no rule results.",
        )
        orphan_rule_results = rule_decision_ids - decision_ids
        _add_health_check(
            checks,
            "rules",
            "Orphan rule results",
            "BLOCKED" if orphan_rule_results else "PASS",
            f"{len(orphan_rule_results)} rule result decision ids are missing from decision history.",
        )
        orphan_violations = {
            item.get("decision_id")
            for item in violations
            if item.get("decision_id") and item.get("decision_id") not in decision_ids
        }
        _add_health_check(
            checks,
            "violations",
            "Violation linkage",
            "WARN" if orphan_violations else "PASS",
            f"{len(orphan_violations)} violation decision ids are missing from decision history.",
        )

        snapshots = self.list_review_snapshots(limit=100)
        snapshots_without_drilldown = [
            item for item in snapshots if not item.get("review", {}).get("drilldown")
        ]
        _add_health_check(
            checks,
            "reviews",
            "Review snapshots",
            "WARN" if snapshots_without_drilldown else "PASS",
            f"{len(snapshots)} snapshots, {len(snapshots_without_drilldown)} without drill-down.",
        )
        reports = self.list_review_reports(limit=100)
        missing_report_snapshots = [
            item
            for item in reports
            if item.get("snapshot_id")
            and not self.get_review_snapshot(str(item.get("snapshot_id")))
        ]
        _add_health_check(
            checks,
            "reports",
            "Report snapshot references",
            "WARN" if missing_report_snapshots else "PASS",
            f"{len(reports)} reports, {len(missing_report_snapshots)} reference missing snapshots.",
        )
        backups = self.list_backups(limit=100)
        _add_health_check(
            checks,
            "backups",
            "Local backup archive",
            "WARN" if not backups else "PASS",
            f"{len(backups)} backup archives found.",
        )
        schema_status = self.schema_status()
        _add_health_check(
            checks,
            "storage",
            "Schema migrations",
            "WARN" if schema_status["pending_count"] else "PASS",
            (
                f"{schema_status['applied_count']} migrations applied; "
                f"current version {schema_status['current_version'] or 'none'}."
            ),
        )

        sources = self.list_data_sources()
        source_by_name = {item.get("provider_name"): item for item in sources}
        mappings = self.list_capabilities()
        missing_sources = [
            item
            for item in mappings
            if item.get("provider_name") not in source_by_name
            and item.get("enabled", True)
        ]
        blocked_sources = [
            item
            for item in sources
            if item.get("enabled", True)
            and item.get("test_status") in {"blocked", "error"}
        ]
        _add_health_check(
            checks,
            "data_sources",
            "Capability mappings",
            "WARN" if missing_sources else "PASS",
            f"{len(missing_sources)} enabled mappings point to missing providers.",
        )
        _add_health_check(
            checks,
            "data_sources",
            "Enabled provider status",
            "WARN" if blocked_sources else "PASS",
            f"{len(blocked_sources)} enabled providers are blocked or errored.",
        )

        status_counts = Counter(item["status"] for item in checks)
        overall_status = "BLOCKED" if status_counts.get("BLOCKED") else (
            "WARN" if status_counts.get("WARN") else "PASS"
        )
        return {
            "status": overall_status,
            "summary": dict(status_counts),
            "check_count": len(checks),
            "checks": checks,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def save_ai_run(
        self,
        *,
        agent_type: str,
        input_payload: dict,
        output_payload: dict,
        compliance_status: str,
        ai_enabled: bool,
    ) -> dict:
        return self.repository.save_ai_run(
            {
                "id": str(uuid4()),
                "agent_type": agent_type,
                "input_hash": input_hash(input_payload),
                "output": output_payload,
                "compliance_status": compliance_status,
                "ai_enabled": ai_enabled,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def save_card(self, card: DisciplineCard) -> None:
        cards = self.store.read("cards.json", {})
        cards[card.symbol] = to_dict(card)
        self.store.write("cards.json", cards)

    def save_card_dict(self, payload: dict) -> DisciplineCard:
        card = card_from_dict(payload)
        self.save_card(card)
        return card

    def generate_card(self, payload: dict) -> DisciplineCard:
        card = generate_card_from_answers(payload)
        self.save_card(card)
        return card

    def delete_card(self, symbol: str) -> bool:
        cards = self.store.read("cards.json", {})
        if symbol not in cards:
            return False
        del cards[symbol]
        self.store.write("cards.json", cards)
        return True

    def load_card(self, symbol: str) -> DisciplineCard:
        cards = self.store.read("cards.json", {})
        if symbol not in cards:
            raise KeyError(f"No discipline card found for symbol: {symbol}")
        return card_from_dict(cards[symbol])

    def list_positions(self) -> dict:
        return self.store.read("positions.json", {})

    def load_positions(self) -> list[Position]:
        return [
            position_from_dict(item)
            for item in self.store.read("positions.json", {}).values()
        ]

    def save_position(self, position: Position) -> None:
        positions = self.store.read("positions.json", {})
        positions[position.symbol] = to_dict(position)
        self.store.write("positions.json", positions)

    def save_position_dict(self, payload: dict) -> Position:
        position = position_from_dict(payload)
        self.save_position(position)
        return position

    def delete_position(self, symbol: str) -> bool:
        positions = self.store.read("positions.json", {})
        if symbol not in positions:
            return False
        del positions[symbol]
        self.store.write("positions.json", positions)
        return True

    def list_trades(self) -> list[dict]:
        return self.store.read("trades.json", [])

    def save_trade(self, trade: Trade) -> None:
        self.store.append("trades.json", to_dict(trade))
        self.reconcile_trade_positions(commit=True)

    def save_trade_dict(self, payload: dict) -> Trade:
        trade = trade_from_dict(payload)
        self.save_trade(trade)
        return trade

    def reconcile_trade_positions(self, commit: bool = False) -> dict:
        current_positions = self.list_positions()
        report = reconcile_trades(
            self.list_trades(),
            position_metadata=current_positions,
        )
        if commit:
            merged = dict(current_positions)
            for symbol in list(report["by_symbol"].keys()):
                if symbol in merged:
                    del merged[symbol]
            merged.update(report["positions"])
            self.store.write("positions.json", merged)
        return report

    def preview_import_file(self, kind: str, path: str) -> dict:
        return self.import_file(kind, path, commit=False)

    def import_file(self, kind: str, path: str, commit: bool = True) -> dict:
        result = import_records(path, kind)
        payload = to_dict(result)
        payload["commit"] = commit
        payload["can_import"] = not payload.get("missing_columns") and bool(
            payload.get("items")
        )
        payload["sample_items"] = payload.get("items", [])[:5]
        if not commit:
            payload["items"] = []
            return payload
        if not payload["can_import"]:
            return payload
        if kind == "positions":
            for item in result.items:
                self.save_position_dict(item)
        elif kind == "trades":
            for item in result.items:
                self.save_trade_dict(item)
            payload["trade_reconciliation"] = self.reconcile_trade_positions(
                commit=True
            )
        return payload

    def sync_from_connector(
        self,
        source: dict,
        capability: str,
        commit: bool = True,
        symbol_filter: str = "",
    ) -> dict:
        source_for_connector = dict(source)
        if symbol_filter:
            config = dict(source_for_connector.get("config", {}))
            config["symbol"] = symbol_filter
            source_for_connector["config"] = config
        connector = build_connector(source_for_connector)
        result = connector.preview(capability)
        payload = to_dict(result)
        if symbol_filter:
            result.items = [
                item
                for item in result.items
                if str(item.get("symbol", "")).upper() == symbol_filter
            ]
            result.market_records = [
                item
                for item in result.market_records
                if str(item.get("symbol", "")).upper() == symbol_filter
            ]
            result.imported = len(result.items)
            payload = to_dict(result)
            payload["symbol_filter"] = symbol_filter
        payload["kind"] = capability
        payload["commit"] = commit
        payload["can_import"] = not payload.get("missing_columns") and bool(
            payload.get("items")
        )
        payload["sample_items"] = payload.get("items", [])[:5]
        payload["sample_market_records"] = payload.get("market_records", [])[:5]
        if not commit:
            payload["items"] = []
            payload["market_records"] = []
            return payload
        if not payload["can_import"]:
            return payload
        if capability == "positions":
            for item in result.items:
                self.save_position_dict(item)
        elif capability == "trades":
            for item in result.items:
                self.save_trade_dict(item)
            payload["trade_reconciliation"] = self.reconcile_trade_positions(
                commit=True
            )
        elif capability in {"price_daily", "price_5min", "volume", "financial_metrics"}:
            saved_market_records = self.repository.save_market_records(
                result.market_records
            )
            saved_items = []
            for item in result.items:
                item.setdefault("id", _stable_evidence_id(item, capability))
                saved_items.append(self.save_evidence_dict(item))
            payload["items"] = saved_items
            payload["market_records"] = saved_market_records
            payload["market_record_count"] = len(saved_market_records)
            if capability in {"price_daily", "price_5min"}:
                payload["position_price_update"] = (
                    self.update_position_prices_from_market_data(
                        symbols=[
                            str(item.get("symbol", "")).upper()
                            for item in saved_market_records
                        ]
                    )
                )
        return payload

    def _sync_from_connector_with_retries(
        self,
        source: dict,
        capability: str,
        *,
        commit: bool,
        symbol_filter: str,
        max_retries: int,
    ) -> tuple[dict, int]:
        attempts = max(1, max_retries + 1)
        last_result: dict | None = None
        for attempt in range(1, attempts + 1):
            result = self.sync_from_connector(
                source,
                capability,
                commit=commit,
                symbol_filter=symbol_filter,
            )
            last_result = result
            if not result.get("errors"):
                return result, attempt
            if result.get("missing_columns"):
                return result, attempt
        return last_result or {}, attempts

    def _enforce_sync_budget(
        self,
        *,
        source: dict,
        capability: str,
        symbol: str,
        sync_policy: dict[str, int],
    ) -> None:
        provider_name = str(source.get("provider_name", ""))
        min_interval = sync_policy["min_interval_seconds"]
        if min_interval > 0:
            previous = self._find_sync_state(provider_name, capability, symbol)
            previous_at = _parse_utc(previous.get("last_success_at") if previous else "")
            if previous_at:
                next_allowed_at = previous_at + timedelta(seconds=min_interval)
                now = datetime.now(timezone.utc)
                if now < next_allowed_at:
                    wait_seconds = int((next_allowed_at - now).total_seconds()) + 1
                    raise ValueError(
                        f"Sync rate limit active for {provider_name}/{capability}; "
                        f"retry after {wait_seconds} seconds."
                    )

        max_syncs = sync_policy["max_syncs_per_day"]
        if max_syncs > 0:
            day_start = datetime.now(timezone.utc).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            used = self.repository.count_data_sync_logs(
                provider_name=provider_name,
                sync_type=capability,
                since=day_start.isoformat(),
            )
            if used >= max_syncs:
                raise ValueError(
                    f"Daily sync quota exceeded for {provider_name}/{capability}: "
                    f"{used}/{max_syncs} successful syncs used."
                )

    def _find_sync_state(
        self,
        provider_name: str,
        capability: str,
        symbol: str,
    ) -> dict:
        normalized_symbol = symbol.strip().upper()
        for item in self.list_data_sync_state():
            if (
                item.get("provider_name") == provider_name
                and item.get("capability") == capability
                and str(item.get("symbol") or "").upper() == normalized_symbol
            ):
                return item
        return {}

    def list_financial_reports(self) -> list[dict]:
        return self.store.read("financial_reports.json", [])

    def save_financial_report(self, summary: FinancialReportSummary) -> None:
        self.store.append("financial_reports.json", to_dict(summary))
        for index, line in enumerate(summary.evidence_summary, 1):
            self.save_evidence(
                EvidenceItem(
                    symbol=summary.symbol.upper(),
                    evidence_type="financial_result",
                    title=f"{summary.period} 财报证据 {index}",
                    content=line,
                    source=summary.source,
                    source_date=summary.period,
                )
            )

    def summarize_financial_report_file(
        self,
        path: str,
        symbol: str,
        period: str,
        material_type: str = "financial_report",
        ai_online_search: bool = False,
    ) -> dict:
        summary = summarize_financial_report(
            path=path,
            symbol=symbol,
            period=period,
            material_type=material_type,
            ai_online_search=ai_online_search,
        )
        summary = self._enhance_information_summary(
            summary,
            text=read_document_text(path),
            ai_online_search=ai_online_search,
        )
        self.save_financial_report(summary)
        return to_dict(summary)

    def summarize_financial_report_text(self, payload: dict) -> dict:
        text = str(payload.get("text", ""))
        summary = summarize_financial_report_text(
            text=text,
            symbol=str(payload.get("symbol", "")),
            period=str(payload.get("period", "")),
            source="inline",
            material_type=str(payload.get("material_type", "financial_report")),
            ai_online_search=bool(payload.get("ai_online_search", False)),
        )
        summary = self._enhance_information_summary(
            summary,
            text=text,
            ai_online_search=bool(payload.get("ai_online_search", False)),
        )
        self.save_financial_report(summary)
        return to_dict(summary)

    def position_guard(self) -> dict:
        report = build_position_guard_report(self.load_profile(), self.load_positions())
        return to_dict(report)

    def check_decision(
        self,
        decision: Decision,
        referenced_evidence_items: list[dict] | None = None,
    ) -> AuditResult:
        profile = self.load_profile()
        card = self.load_card(decision.symbol)
        result = evaluate_decision(profile, card, decision)
        rule_results = self._build_and_save_rule_results(profile, card, decision)

        decision_payload = to_dict(decision)
        if referenced_evidence_items:
            decision_payload["referenced_evidence_ids"] = [
                item["id"] for item in referenced_evidence_items
            ]
        self.store.append("decisions.json", decision_payload)
        self.store.append("audits.json", to_dict(result))
        for item in rule_results:
            self.store.append("rule_results.json", item)
        for violation in result.violations + result.warnings:
            self.store.append(
                "violations.json",
                {
                    "id": str(uuid4()),
                    "decision_id": result.decision_id,
                    "symbol": decision.symbol,
                    "status": "open",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "resolved_at": None,
                    "resolution_note": "",
                    **to_dict(violation),
                },
            )
        return result

    def check_decision_payload(self, payload: dict) -> dict:
        enriched = self._enrich_decision_payload(payload)
        referenced_evidence_items = enriched.pop("_referenced_evidence_items", [])
        decision = decision_from_dict(enriched)
        result = self.check_decision(decision, referenced_evidence_items)
        return {
            **to_dict(result),
            "rule_results": self.list_rule_results(decision_id=decision.id),
            "referenced_evidence_items": referenced_evidence_items,
        }

    def check_decision_dict(self, payload: dict) -> AuditResult:
        payload = self._enrich_decision_payload(payload)
        referenced_evidence_items = payload.pop("_referenced_evidence_items", [])
        return self.check_decision(decision_from_dict(payload), referenced_evidence_items)

    def dashboard(self, month: str) -> dict:
        dashboard = {
            "profile": to_dict(self.load_profile()),
            "settings": self.list_settings(),
            "data_sources": self.list_data_sources(),
            "data_capabilities": self.list_capabilities(),
            "data_sync_logs": self.list_data_sync_logs(limit=10),
            "data_sync_state": self.list_data_sync_state(),
            "market_data_summary": self.market_data_summary(),
            "card_templates": self.list_card_templates(),
            "rule_specs": list_rule_specs(),
            "violation_catalog": {
                key: to_dict(value) for key, value in VIOLATION_CATALOG.items()
            },
            "cards": self.list_cards(),
            "positions": self.list_positions(),
            "trades": self.list_trades(),
            "trade_reconciliation": self.reconcile_trade_positions(commit=False),
            "financial_reports": self.list_financial_reports(),
            "evidence_items": self.list_evidence(limit=30),
            "ai_runs": self.list_ai_runs(limit=8),
            "position_guard": self.position_guard(),
            "decisions": self.store.read("decisions.json", []),
            "audits": self.store.read("audits.json", []),
            "rule_results": self.list_rule_results(limit=300),
            "violations": self.store.read("violations.json", []),
            "review": self.monthly_review(month),
            "review_snapshots": self.list_review_snapshots(month=month, limit=6),
            "review_reports": self.list_review_reports(limit=8),
            "backup_archives": self.list_backups(limit=8),
            "data_health": self.data_health_check(),
        }
        dashboard["copilot"] = self._build_copilot(dashboard)
        return dashboard

    def copilot(self, month: str) -> dict:
        return self.dashboard(month)["copilot"]

    def _build_copilot(self, dashboard: dict) -> dict:
        settings = dashboard.get("settings", {})
        ai_enabled = bool(settings.get("ai_enabled", False))
        output = build_copilot_summary(dashboard)
        sanitized, compliance_status = sanitize_ai_output(output)
        if ai_enabled:
            self.save_ai_run(
                agent_type="copilot",
                input_payload={
                    "month": dashboard.get("review", {}).get("month"),
                    "decision_count": dashboard.get("review", {}).get("decision_count"),
                    "violation_count": len(dashboard.get("violations", [])),
                },
                output_payload=sanitized,
                compliance_status=compliance_status,
                ai_enabled=True,
            )
        sanitized["ai_enabled"] = ai_enabled
        sanitized["compliance_status"] = compliance_status
        sanitized["final_status_source"] = "rule_engine"
        if not ai_enabled:
            sanitized["mode"] = "deterministic_local"
        return sanitized

    def _enhance_information_summary(
        self,
        summary: FinancialReportSummary,
        *,
        text: str,
        ai_online_search: bool,
    ) -> FinancialReportSummary:
        settings = self.list_settings()
        if not settings.get("ai_enabled"):
            summary.analysis_mode = "local_rules"
            summary.ai_status = "disabled"
            return summary
        try:
            ai_payload = analyze_information_with_ai(
                text=text,
                symbol=summary.symbol,
                period=summary.period,
                material_type=summary.material_type,
                ai_online_search=ai_online_search,
                settings=settings,
            )
            sanitized, compliance_status = sanitize_ai_output(ai_payload)
            summary = apply_analysis_payload(
                summary,
                sanitized,
                mode="ai",
                ai_status=compliance_status,
            )
            self.save_ai_run(
                agent_type="info_analysis",
                input_payload={
                    "symbol": summary.symbol,
                    "period": summary.period,
                    "material_type": summary.material_type,
                    "source": summary.source,
                    "ai_online_search": ai_online_search,
                    "text_chars": len(text),
                },
                output_payload=sanitized,
                compliance_status=compliance_status,
                ai_enabled=True,
            )
        except Exception as exc:
            summary.analysis_mode = "local_rules"
            summary.ai_status = "failed"
            summary.ai_error = str(exc)
        return summary

    def resolve_violation(self, violation_id: str, note: str = "") -> bool:
        violations = self.store.read("violations.json", [])
        updated = False
        for violation in violations:
            if violation.get("id") == violation_id:
                violation["status"] = "resolved"
                violation["resolved_at"] = datetime.now(timezone.utc).isoformat()
                violation["resolution_note"] = note
                updated = True
                break
        if updated:
            self.store.write("violations.json", violations)
        return updated

    def monthly_review(self, month: str) -> dict:
        decisions = [
            item
            for item in self.store.read("decisions.json", [])
            if item.get("created_at", "").startswith(month)
        ]
        audits = self.store.read("audits.json", [])
        audit_by_id = {item["decision_id"]: item for item in audits}

        monthly_audits = [
            audit_by_id[item["id"]] for item in decisions if item["id"] in audit_by_id
        ]
        all_violations = self.store.read("violations.json", [])
        monthly_violations = [
            item
            for item in all_violations
            if item.get("decision_id")
            in {audit["decision_id"] for audit in monthly_audits}
        ]
        statuses = Counter(item["status"] for item in monthly_audits)
        violation_types = Counter()
        violation_weight = 0
        for audit in monthly_audits:
            for item in audit.get("violations", []) + audit.get("warnings", []):
                violation_types[item["type"]] += 1
                violation_weight += int(item.get("weight", 0))

        total = len(monthly_audits)
        pass_count = statuses.get("PASS", 0)
        pass_rate = round(pass_count / total * 100, 1) if total else 100.0
        score_report = calculate_discipline_score(monthly_audits)
        attribution = build_review_attribution(decisions, monthly_audits)
        revision_suggestions = build_rule_revision_suggestions(monthly_violations)

        return {
            "month": month,
            "decision_count": total,
            "status_counts": dict(statuses),
            "discipline_score": score_report["score"],
            "pass_rate": pass_rate,
            "score_report": score_report,
            "attribution": attribution,
            "rule_revision_suggestions": revision_suggestions,
            "violation_weight": violation_weight,
            "violation_types": dict(violation_types),
            "next_month_forbidden_behaviors": _suggest_forbidden_behaviors(
                violation_types
            ),
            "disclaimer": (
                "This review evaluates discipline consistency only. "
                "It is not investment advice."
            ),
        }

    def monthly_review_drilldown(self, month: str) -> dict:
        decisions = [
            item
            for item in self.store.read("decisions.json", [])
            if item.get("created_at", "").startswith(month)
        ]
        decision_ids = {item["id"] for item in decisions}
        audits = [
            item
            for item in self.store.read("audits.json", [])
            if item.get("decision_id") in decision_ids
        ]
        violations = [
            item
            for item in self.store.read("violations.json", [])
            if item.get("decision_id") in decision_ids
        ]
        rule_results: list[dict] = []
        for decision_id in sorted(decision_ids):
            rule_results.extend(
                self.list_rule_results(decision_id=decision_id, limit=200)
            )

        evidence_ids: list[str] = []
        for decision in decisions:
            evidence_ids.extend(
                str(item)
                for item in decision.get("referenced_evidence_ids", [])
                if str(item).strip()
            )
        evidence_items = self.list_evidence_by_ids(evidence_ids)

        return {
            "decisions": decisions,
            "audits": audits,
            "rule_results": rule_results,
            "violations": violations,
            "evidence_items": evidence_items,
            "counts": {
                "decisions": len(decisions),
                "audits": len(audits),
                "rule_results": len(rule_results),
                "violations": len(violations),
                "evidence_items": len(evidence_items),
            },
        }

    def save_review_snapshot(self, month: str) -> dict:
        review = self.monthly_review(month)
        review["drilldown"] = self.monthly_review_drilldown(month)
        snapshot = {
            "id": str(uuid4()),
            "period": month,
            "review": review,
            "discipline_score": review.get("discipline_score", 0),
            "decision_count": review.get("decision_count", 0),
            "status_summary": review.get("status_counts", {}),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        saved = self.repository.save_review_snapshot(snapshot)
        self.store.append("reviews.json", saved)
        return saved

    def export_review_snapshot(
        self,
        snapshot_id: str,
        export_format: str = "markdown",
    ) -> dict:
        snapshot = self.get_review_snapshot(snapshot_id)
        if not snapshot:
            raise KeyError(f"No review snapshot found: {snapshot_id}")
        if export_format not in {"markdown", "md"}:
            raise ValueError("Only markdown export is supported.")

        content = _render_review_markdown(snapshot)
        reports_dir = self.store.data_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"review-{_safe_slug(snapshot['period'])}-{snapshot_id[:8]}.md"
        path = reports_dir / filename
        path.write_text(content, encoding="utf-8")
        return {
            "snapshot_id": snapshot_id,
            "format": "markdown",
            "path": str(path),
            "bytes": path.stat().st_size,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def compare_review_snapshots(
        self,
        left_snapshot_id: str,
        right_snapshot_id: str,
    ) -> dict:
        left = self.get_review_snapshot(left_snapshot_id)
        right = self.get_review_snapshot(right_snapshot_id)
        if not left:
            raise KeyError(f"No review snapshot found: {left_snapshot_id}")
        if not right:
            raise KeyError(f"No review snapshot found: {right_snapshot_id}")

        left_review = left.get("review", {})
        right_review = right.get("review", {})
        left_drilldown = left_review.get("drilldown", {})
        right_drilldown = right_review.get("drilldown", {})
        left_symbol_counts = _symbol_violation_counts(left_drilldown)
        right_symbol_counts = _symbol_violation_counts(right_drilldown)
        suggestion_delta = _suggestion_delta(
            left_review.get("rule_revision_suggestions", []),
            right_review.get("rule_revision_suggestions", []),
        )
        score_delta = _as_number(right_review.get("discipline_score")) - _as_number(
            left_review.get("discipline_score")
        )
        violation_weight_delta = _as_number(
            right_review.get("violation_weight")
        ) - _as_number(left_review.get("violation_weight"))

        return {
            "left": _snapshot_compare_summary(left),
            "right": _snapshot_compare_summary(right),
            "delta": {
                "discipline_score": round(score_delta, 2),
                "pass_rate": round(
                    _as_number(right_review.get("pass_rate"))
                    - _as_number(left_review.get("pass_rate")),
                    2,
                ),
                "decision_count": int(
                    _as_number(right_review.get("decision_count"))
                    - _as_number(left_review.get("decision_count"))
                ),
                "violation_weight": round(violation_weight_delta, 2),
                "status_counts": _diff_counts(
                    left_review.get("status_counts", {}),
                    right_review.get("status_counts", {}),
                ),
                "violation_types": _diff_counts(
                    left_review.get("violation_types", {}),
                    right_review.get("violation_types", {}),
                ),
            },
            "repeated_symbols": [
                {
                    "symbol": symbol,
                    "left_violations": left_symbol_counts[symbol],
                    "right_violations": right_symbol_counts[symbol],
                    "delta": right_symbol_counts[symbol] - left_symbol_counts[symbol],
                }
                for symbol in sorted(
                    set(left_symbol_counts).intersection(right_symbol_counts)
                )
            ],
            "rule_suggestions": suggestion_delta,
            "interpretation": _compare_interpretation(
                score_delta=score_delta,
                violation_weight_delta=violation_weight_delta,
                suggestion_delta=suggestion_delta,
            ),
        }

    def create_backup(self) -> dict:
        backups_dir = self.store.data_dir / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(timezone.utc).isoformat()
        filename = f"disciplineos-backup-{_safe_slug(created_at)}.zip"
        path = backups_dir / filename
        source_files = [
            item
            for item in self.store.data_dir.rglob("*")
            if item.is_file()
            and backups_dir not in item.parents
            and item.name != filename
        ]
        manifest = {
            "format": "disciplineos-backup-v1",
            "created_at": created_at,
            "file_count": len(source_files),
            "files": [
                item.relative_to(self.store.data_dir).as_posix()
                for item in source_files
            ],
        }
        with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("backup_manifest.json", json.dumps(manifest, indent=2))
            for item in source_files:
                archive.write(
                    item,
                    arcname=item.relative_to(self.store.data_dir).as_posix(),
                )
        return {
            "path": str(path),
            "filename": path.name,
            "bytes": path.stat().st_size,
            "created_at": created_at,
            "file_count": len(source_files),
            "format": manifest["format"],
        }

    def restore_backup(self, filename: str) -> dict:
        backup_path = _resolve_backup_path(self.store.data_dir, filename)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {filename}")
        _validate_backup_archive(backup_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            with zipfile.ZipFile(backup_path) as archive:
                archive.extractall(temp_path)
            restored_files = []
            for item in temp_path.rglob("*"):
                if not item.is_file() or item.name == "backup_manifest.json":
                    continue
                relative = item.relative_to(temp_path)
                target = self.store.data_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
                restored_files.append(relative.as_posix())
        return {
            "filename": backup_path.name,
            "path": str(backup_path),
            "restored_count": len(restored_files),
            "restored_files": restored_files,
            "restored_at": datetime.now(timezone.utc).isoformat(),
        }

    def _enrich_decision_payload(self, payload: dict) -> dict:
        enriched = dict(payload)
        auto_position = bool(enriched.pop("auto_position", False))
        missing_before = "position_before_pct" not in enriched
        missing_after = "position_after_pct" not in enriched
        if missing_before or missing_after or auto_position:
            before, after = project_position_percent(
                self.load_positions(),
                symbol=str(enriched["symbol"]),
                action=str(enriched["action"]),
                amount=float(enriched.get("amount", 0)),
            )
            enriched["position_before_pct"] = before
            enriched["position_after_pct"] = after
        evidence_item_ids = [
            str(item).strip()
            for item in enriched.pop("evidence_item_ids", [])
            if str(item).strip()
        ]
        if evidence_item_ids:
            evidence_items = self.list_evidence_by_ids(evidence_item_ids)
            existing_evidence = list(enriched.get("evidence") or [])
            enriched["evidence"] = existing_evidence + [
                f"{item['title']}: {item['content']}" for item in evidence_items
            ]
            enriched["_referenced_evidence_items"] = evidence_items
            return enriched
        if not enriched.get("evidence"):
            evidence_items = self.list_evidence(symbol=str(enriched["symbol"]), limit=5)
            enriched["evidence"] = [
                f"{item['title']}: {item['content']}" for item in evidence_items
            ]
            enriched["_referenced_evidence_items"] = evidence_items
        return enriched

    def _resolve_capability_mapping(self, capability: str) -> dict:
        mappings = [
            item
            for item in self.list_capabilities()
            if item.get("capability") == capability and item.get("enabled", True)
        ]
        if not mappings:
            raise ValueError(f"No enabled provider mapping for capability: {capability}")
        return sorted(mappings, key=lambda item: int(item.get("priority", 100)))[0]

    def _source_by_name(self, provider_name: str) -> dict:
        for source in self.list_data_sources():
            if source.get("provider_name") == provider_name and source.get("enabled", True):
                return source
        raise ValueError(f"No enabled data source found: {provider_name}")

    def _build_and_save_rule_results(
        self,
        profile: InvestorProfile,
        card: DisciplineCard,
        decision: Decision,
    ) -> list[dict]:
        created_at = datetime.now(timezone.utc).isoformat()
        items = []
        for item in build_rule_results(profile, card, decision):
            items.append(
                {
                    "id": str(uuid4()),
                    "created_at": created_at,
                    **item,
                }
            )
        return self.repository.save_rule_results(items)


def seed_demo_data(service: DisciplineService) -> None:
    service.save_profile(profile_from_dict(_default_profile()))
    service.save_card(
        DisciplineCard(
            symbol="SAMPLE",
            name="Sample Asset",
            asset_type="stock",
            sector="technology",
            thesis=["Business quality remains intact.", "Valuation is monitored."],
            max_position_pct=15,
            no_buy_conditions=["Valuation exceeds discipline range."],
            add_conditions=["New evidence confirms the thesis."],
            reduce_conditions=["Position exceeds limit.", "Thesis weakens."],
            invalid_conditions=["Core metrics miss expectations twice."],
            forbidden_behaviors=[
                "Buy only because price has fallen.",
                "Add before earnings without a plan.",
            ],
        )
    )
    service.save_position(
        Position(
            symbol="SAMPLE",
            name="Sample Asset",
            asset_type="stock",
            market="HK",
            sector="technology",
            theme="AI",
            currency="HKD",
            quantity=1000,
            cost_price=10,
            current_price=10,
        )
    )
    service.check_decision(
        Decision(
            symbol="SAMPLE",
            action=Action.ADD,
            amount=10000,
            position_before_pct=10,
            position_after_pct=18,
            reason="Price has fallen a lot and I want to reduce my average cost.",
            evidence=[],
            emotion=Emotion.ANXIOUS,
        )
    )


def _default_profile() -> dict:
    return {
        "name": "default",
        "style": "balanced",
        "style_allocations": {
            "value": 20,
            "growth": 40,
            "cycle": 10,
            "dividend": 10,
            "cash_defensive": 20,
        },
        "max_single_position_pct": 15,
        "max_sector_position_pct": 30,
        "max_drawdown_pct": 20,
        "allow_pre_earnings_add": False,
        "behavioral_weaknesses": ["emotional_averaging_down", "fomo"],
    }


def _suggest_forbidden_behaviors(violation_types: Counter) -> list[str]:
    suggestions = []
    if violation_types.get("Position Overweight"):
        suggestions.append("Do not add to positions already above the limit.")
    if violation_types.get("Emotional Averaging Down"):
        suggestions.append("Do not add only to reduce average cost.")
    if violation_types.get("No Evidence Trade"):
        suggestions.append("Do not buy or add without explicit new evidence.")
    if violation_types.get("Earnings Bet"):
        suggestions.append("Do not increase exposure before earnings without a plan.")
    return suggestions


def _render_review_markdown(snapshot: dict) -> str:
    review = snapshot.get("review", {})
    drilldown = review.get("drilldown", {})
    decisions = drilldown.get("decisions", [])
    audits_by_decision = {
        item.get("decision_id"): item for item in drilldown.get("audits", [])
    }
    rules_by_decision = _group_items(drilldown.get("rule_results", []), "decision_id")
    violations_by_decision = _group_items(drilldown.get("violations", []), "decision_id")
    evidence_by_id = {
        item.get("id"): item for item in drilldown.get("evidence_items", [])
    }

    lines = [
        f"# DisciplineOS Monthly Review {snapshot.get('period', '')}",
        "",
        f"- Snapshot ID: {snapshot.get('id', '')}",
        f"- Created At: {snapshot.get('created_at', '')}",
        f"- Discipline Score: {review.get('discipline_score', '--')}",
        f"- Pass Rate: {review.get('pass_rate', '--')}%",
        f"- Decision Count: {review.get('decision_count', 0)}",
        f"- Status Counts: {_format_mapping(review.get('status_counts', {}))}",
        f"- Violation Weight: {review.get('violation_weight', 0)}",
        "",
        f"> {review.get('disclaimer', 'This report is not investment advice.')}",
        "",
        "## Violation Types",
        "",
        _bullet_block(review.get("violation_types", {})),
        "",
        "## Next Month Forbidden Behaviors",
        "",
        _bullet_block(review.get("next_month_forbidden_behaviors", [])),
        "",
        "## Attribution",
        "",
    ]
    attribution = review.get("attribution", {})
    for bucket in ["market", "security", "portfolio", "behavior"]:
        summary = attribution.get(bucket, {}).get("summary", f"No {bucket} issue recorded.")
        lines.append(f"- {bucket}: {summary}")

    lines.extend(["", "## Rule Revision Suggestions", ""])
    suggestions = review.get("rule_revision_suggestions", [])
    if suggestions:
        for item in suggestions:
            lines.append(
                f"- {item.get('scope', '')} / {item.get('trigger', '')}: "
                f"{item.get('suggestion', '')}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Decision Drill-down", ""])
    if not decisions:
        lines.append("- No decision history.")
    for index, decision in enumerate(decisions, 1):
        audit = audits_by_decision.get(decision.get("id"), {})
        lines.extend(
            [
                f"### {index}. {decision.get('symbol', '')} {decision.get('action', '')}",
                "",
                f"- Decision ID: {decision.get('id', '')}",
                f"- Created At: {decision.get('created_at', '')}",
                f"- Status: {audit.get('status', 'UNKNOWN')}",
                f"- Emotion: {decision.get('emotion', '')}",
                f"- Position After: {decision.get('position_after_pct', '--')}%",
                f"- Reason: {decision.get('reason', '')}",
                "",
                "#### Referenced Evidence",
                "",
            ]
        )
        evidence_items = [
            evidence_by_id[item]
            for item in decision.get("referenced_evidence_ids", [])
            if item in evidence_by_id
        ]
        if evidence_items:
            for item in evidence_items:
                lines.append(
                    f"- {item.get('symbol', '')} / {item.get('evidence_type', '')} / "
                    f"{item.get('title', '')}: {item.get('content', '')}"
                )
        else:
            lines.append("- None")

        lines.extend(["", "#### Violations", ""])
        violations = violations_by_decision.get(decision.get("id"), [])
        if violations:
            for item in violations:
                lines.append(
                    f"- {item.get('type', '')} / {item.get('severity', '')}: "
                    f"{item.get('message', '')}"
                )
        else:
            lines.append("- None")

        lines.extend(["", "#### Rule Results", ""])
        rule_results = sorted(
            rules_by_decision.get(decision.get("id"), []),
            key=lambda item: str(item.get("rule_code", "")),
        )
        if rule_results:
            for item in rule_results:
                lines.append(
                    f"- {item.get('rule_code', '')} / {item.get('status', '')}: "
                    f"{item.get('message', '')}"
                )
        else:
            lines.append("- None")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _group_items(items: list[dict], key: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(str(item.get(key, "")), []).append(item)
    return grouped


def _format_mapping(value: dict) -> str:
    if not value:
        return "None"
    return " / ".join(f"{key} {item}" for key, item in value.items())


def _bullet_block(value: dict | list) -> str:
    if isinstance(value, dict):
        if not value:
            return "- None"
        return "\n".join(f"- {key}: {item}" for key, item in value.items())
    if not value:
        return "- None"
    return "\n".join(f"- {item}" for item in value)


def _safe_slug(value: str) -> str:
    return "".join(
        char if char.isalnum() or char in {"-", "_"} else "-"
        for char in value
    ).strip("-") or "review"


def _parse_report_metadata(path: Path) -> dict:
    metadata = {
        "snapshot_id": "",
        "period": "",
        "title": path.stem,
    }
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[:12]
    except OSError:
        return metadata
    for line in lines:
        if line.startswith("# "):
            metadata["title"] = line[2:].strip()
            parts = metadata["title"].split()
            if parts:
                metadata["period"] = parts[-1]
        if line.startswith("- Snapshot ID:"):
            metadata["snapshot_id"] = line.split(":", 1)[1].strip()
    return metadata


def _read_backup_manifest(path: Path) -> dict:
    try:
        with zipfile.ZipFile(path) as archive:
            with archive.open("backup_manifest.json") as file:
                return json.loads(file.read().decode("utf-8"))
    except (OSError, KeyError, zipfile.BadZipFile, json.JSONDecodeError):
        return {}


def _resolve_backup_path(data_dir: Path, filename: str) -> Path:
    backups_dir = (data_dir / "backups").resolve()
    candidate = (backups_dir / Path(filename).name).resolve()
    if backups_dir not in candidate.parents or candidate.suffix.lower() != ".zip":
        raise ValueError("Invalid backup filename.")
    return candidate


def _validate_backup_archive(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            member = Path(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise ValueError(f"Unsafe backup entry: {info.filename}")
            if info.filename.startswith("backups/"):
                raise ValueError(f"Backup archives cannot restore backups/: {info.filename}")


def _add_health_check(
    checks: list[dict],
    category: str,
    title: str,
    status: str,
    message: str,
) -> None:
    checks.append(
        {
            "category": category,
            "title": title,
            "status": status,
            "message": message,
        }
    )


def _snapshot_compare_summary(snapshot: dict) -> dict:
    review = snapshot.get("review", {})
    return {
        "id": snapshot.get("id", ""),
        "period": snapshot.get("period", ""),
        "created_at": snapshot.get("created_at", ""),
        "discipline_score": review.get("discipline_score", 0),
        "pass_rate": review.get("pass_rate", 0),
        "decision_count": review.get("decision_count", 0),
        "violation_weight": review.get("violation_weight", 0),
        "status_counts": review.get("status_counts", {}),
        "violation_types": review.get("violation_types", {}),
    }


def _diff_counts(left: dict, right: dict) -> dict:
    keys = sorted(set(left) | set(right))
    return {
        key: int(_as_number(right.get(key)) - _as_number(left.get(key)))
        for key in keys
        if _as_number(right.get(key)) - _as_number(left.get(key)) != 0
    }


def _symbol_violation_counts(drilldown: dict) -> Counter:
    counts: Counter = Counter()
    for item in drilldown.get("violations", []):
        symbol = str(item.get("symbol", "")).strip().upper()
        if symbol:
            counts[symbol] += 1
    return counts


def _suggestion_delta(left: list[dict], right: list[dict]) -> dict:
    left_keys = {_suggestion_key(item): item for item in left}
    right_keys = {_suggestion_key(item): item for item in right}
    return {
        "persistent": [
            right_keys[key] for key in sorted(set(left_keys).intersection(right_keys))
        ],
        "added": [right_keys[key] for key in sorted(set(right_keys) - set(left_keys))],
        "removed": [left_keys[key] for key in sorted(set(left_keys) - set(right_keys))],
    }


def _suggestion_key(item: dict) -> str:
    return f"{item.get('scope', '')}|{item.get('trigger', '')}|{item.get('suggestion', '')}"


def _compare_interpretation(
    *,
    score_delta: float,
    violation_weight_delta: float,
    suggestion_delta: dict,
) -> str:
    added = len(suggestion_delta.get("added", []))
    removed = len(suggestion_delta.get("removed", []))
    if score_delta > 0 and violation_weight_delta <= 0 and added <= removed:
        return "improving"
    if score_delta < 0 or violation_weight_delta > 0 or added > removed:
        return "deteriorating"
    return "mixed"


def _as_number(value: object) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _as_non_negative_int(value: object) -> int:
    try:
        return max(0, int(float(value or 0)))
    except (TypeError, ValueError):
        return 0


def _sync_policy(source: dict) -> dict[str, int]:
    config = dict(source.get("config", {}) or {})
    return {
        "min_interval_seconds": _as_non_negative_int(
            config.get("min_interval_seconds")
        ),
        "max_syncs_per_day": _as_non_negative_int(config.get("max_syncs_per_day")),
        "max_retries": min(5, _as_non_negative_int(config.get("max_retries"))),
    }


def _parse_utc(value: object) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _market_close(record: dict) -> float | None:
    fields = record.get("fields") or {}
    if not isinstance(fields, dict):
        return None
    value = fields.get("close")
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _stable_evidence_id(item: dict, capability: str) -> str:
    raw = "|".join(
        [
            str(item.get("source", "")),
            str(capability),
            str(item.get("symbol", "")).upper(),
            str(item.get("evidence_type", "")),
            str(item.get("title", "")),
            str(item.get("source_date", "")),
            str(item.get("content", "")),
        ]
    )
    return f"ev-{sha256(raw.encode('utf-8')).hexdigest()[:32]}"


def _last_source_timestamp(result: dict) -> str:
    timestamps: list[str] = []
    for item in result.get("market_records", []) or []:
        timestamp = str(item.get("timestamp", "")).strip()
        if timestamp:
            timestamps.append(timestamp)
    for item in result.get("items", []) or []:
        timestamp = str(item.get("source_date", "")).strip()
        if timestamp:
            timestamps.append(timestamp)
    return max(timestamps) if timestamps else ""
