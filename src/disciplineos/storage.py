from __future__ import annotations

import json
import importlib.util
import sqlite3
from hashlib import sha256
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonStore:
    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def read(self, name: str, default: Any) -> Any:
        path = self.data_dir / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, name: str, data: Any) -> None:
        path = self.data_dir / name
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def append(self, name: str, item: Any) -> None:
        items = self.read(name, [])
        items.append(item)
        self.write(name, items)


class SQLiteStore:
    """SQLite-backed JSON document store with v0.2 settings/provider tables."""

    def __init__(self, data_dir: Path | str, db_name: str = "disciplineos.db") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / db_name
        self.legacy = JsonStore(self.data_dir)
        self._connect().close()
        self._ensure_schema()

    def read(self, name: str, default: Any) -> Any:
        with self._connect() as conn:
            row = conn.execute(
                "select data_json from json_documents where name = ?",
                (name,),
            ).fetchone()
        if row:
            return json.loads(row["data_json"])

        legacy_value = self.legacy.read(name, default)
        if legacy_value != default:
            self.write(name, legacy_value)
        return legacy_value

    def write(self, name: str, data: Any) -> None:
        payload = json.dumps(data, ensure_ascii=False)
        updated_at = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                insert into json_documents(name, data_json, updated_at)
                values (?, ?, ?)
                on conflict(name) do update set
                  data_json = excluded.data_json,
                  updated_at = excluded.updated_at
                """,
                (name, payload, updated_at),
            )
        self.legacy.write(name, data)

    def append(self, name: str, item: Any) -> None:
        items = self.read(name, [])
        items.append(item)
        self.write(name, items)

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._connect() as conn:
            row = conn.execute(
                "select value_json from system_settings where key = ?",
                (key,),
            ).fetchone()
        return json.loads(row["value_json"]) if row else default

    def set_setting(self, key: str, value: Any) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into system_settings(key, value_json, updated_at)
                values (?, ?, ?)
                on conflict(key) do update set
                  value_json = excluded.value_json,
                  updated_at = excluded.updated_at
                """,
                (key, json.dumps(value, ensure_ascii=False), _utc_now()),
            )

    def list_settings(self) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "select key, value_json from system_settings order by key"
            ).fetchall()
        settings = {row["key"]: json.loads(row["value_json"]) for row in rows}
        defaults = {
            "storage_mode": "sqlite",
            "ai_enabled": False,
            "strict_mode": True,
            "discipline_mode": "block",
            "ai_api_token": "",
            "ai_api_base_url": "",
            "ai_model": "gpt-5.5",
        }
        return {**defaults, **settings}

    def save_data_source(self, source: dict[str, Any]) -> dict[str, Any]:
        provider_name = str(source.get("provider_name", "")).strip()
        if not provider_name:
            raise ValueError("provider_name is required")
        provider_type = str(source.get("provider_type") or provider_name).strip()
        enabled = bool(source.get("enabled", True))
        priority = int(source.get("priority", 100))
        config = dict(source.get("config", {}))
        tested = self._test_provider(provider_type, config)
        with self._connect() as conn:
            conn.execute(
                """
                insert into data_sources(
                  provider_name, provider_type, enabled, priority, config_json,
                  test_status, test_message, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(provider_name) do update set
                  provider_type = excluded.provider_type,
                  enabled = excluded.enabled,
                  priority = excluded.priority,
                  config_json = excluded.config_json,
                  test_status = excluded.test_status,
                  test_message = excluded.test_message,
                  updated_at = excluded.updated_at
                """,
                (
                    provider_name,
                    provider_type,
                    1 if enabled else 0,
                    priority,
                    json.dumps(config, ensure_ascii=False),
                    tested["status"],
                    tested["message"],
                    _utc_now(),
                ),
            )
        return {
            "provider_name": provider_name,
            "provider_type": provider_type,
            "enabled": enabled,
            "priority": priority,
            "config": config,
            "test_status": tested["status"],
            "test_message": tested["message"],
        }

    def list_data_sources(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select provider_name, provider_type, enabled, priority, config_json,
                       test_status, test_message, updated_at
                from data_sources
                order by priority, provider_name
                """
            ).fetchall()
        return [
            {
                "provider_name": row["provider_name"],
                "provider_type": row["provider_type"],
                "enabled": bool(row["enabled"]),
                "priority": row["priority"],
                "config": json.loads(row["config_json"] or "{}"),
                "test_status": row["test_status"],
                "test_message": row["test_message"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def save_capability(self, mapping: dict[str, Any]) -> dict[str, Any]:
        capability = str(mapping.get("capability", "")).strip()
        provider_name = str(mapping.get("provider_name", "")).strip()
        if not capability or not provider_name:
            raise ValueError("capability and provider_name are required")
        enabled = bool(mapping.get("enabled", True))
        priority = int(mapping.get("priority", 100))
        fallback_provider = str(mapping.get("fallback_provider", "")).strip()
        with self._connect() as conn:
            conn.execute(
                """
                insert into data_capabilities(
                  capability, provider_name, enabled, priority, fallback_provider,
                  updated_at
                )
                values (?, ?, ?, ?, ?, ?)
                on conflict(capability, provider_name) do update set
                  enabled = excluded.enabled,
                  priority = excluded.priority,
                  fallback_provider = excluded.fallback_provider,
                  updated_at = excluded.updated_at
                """,
                (
                    capability,
                    provider_name,
                    1 if enabled else 0,
                    priority,
                    fallback_provider,
                    _utc_now(),
                ),
            )
        return mapping

    def list_capabilities(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select capability, provider_name, enabled, priority,
                       fallback_provider, updated_at
                from data_capabilities
                order by capability, priority, provider_name
                """
            ).fetchall()
        return [
            {
                "capability": row["capability"],
                "provider_name": row["provider_name"],
                "enabled": bool(row["enabled"]),
                "priority": row["priority"],
                "fallback_provider": row["fallback_provider"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def save_data_sync_log(self, item: dict[str, Any]) -> dict[str, Any]:
        log = {
            "provider_name": str(item["provider_name"]),
            "sync_type": str(item["sync_type"]),
            "status": str(item["status"]),
            "message": str(item.get("message", "")),
            "started_at": str(item["started_at"]),
            "finished_at": str(item.get("finished_at") or ""),
        }
        with self._connect() as conn:
            cursor = conn.execute(
                """
                insert into data_sync_logs(
                    provider_name, sync_type, status, message, started_at, finished_at
                )
                values (?, ?, ?, ?, ?, ?)
                """,
                (
                    log["provider_name"],
                    log["sync_type"],
                    log["status"],
                    log["message"],
                    log["started_at"],
                    log["finished_at"] or None,
                ),
            )
            log["id"] = cursor.lastrowid
        return log

    def list_data_sync_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select id, provider_name, sync_type, status, message,
                       started_at, finished_at
                from data_sync_logs
                order by id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_data_sync_state(self, item: dict[str, Any]) -> dict[str, Any]:
        state = {
            "provider_name": str(item["provider_name"]),
            "capability": str(item["capability"]),
            "symbol": str(item.get("symbol", "")).strip().upper(),
            "status": str(item["status"]),
            "row_count": int(item.get("row_count", 0)),
            "last_success_at": str(item.get("last_success_at", "")),
            "last_error": str(item.get("last_error", "")),
            "last_source_timestamp": str(item.get("last_source_timestamp", "")),
            "updated_at": _utc_now(),
        }
        with self._connect() as conn:
            conn.execute(
                """
                insert into data_sync_state(
                    provider_name, capability, symbol, status, row_count,
                    last_success_at, last_error, last_source_timestamp, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(provider_name, capability, symbol) do update set
                    status = excluded.status,
                    row_count = excluded.row_count,
                    last_success_at = excluded.last_success_at,
                    last_error = excluded.last_error,
                    last_source_timestamp = excluded.last_source_timestamp,
                    updated_at = excluded.updated_at
                """,
                (
                    state["provider_name"],
                    state["capability"],
                    state["symbol"],
                    state["status"],
                    state["row_count"],
                    state["last_success_at"] or None,
                    state["last_error"],
                    state["last_source_timestamp"],
                    state["updated_at"],
                ),
            )
        return state

    def list_data_sync_state(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select provider_name, capability, symbol, status, row_count,
                       last_success_at, last_error, last_source_timestamp, updated_at
                from data_sync_state
                order by updated_at desc, provider_name, capability, symbol
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def save_market_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        saved: list[dict[str, Any]] = []
        now = _utc_now()
        with self._connect() as conn:
            for item in records:
                record = _normalize_market_record(item, now)
                conn.execute(
                    """
                    insert into market_data(
                        id, provider_name, provider_type, data_type, symbol,
                        timestamp, metric, fields_json, source, created_at, updated_at
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    on conflict(id) do update set
                        provider_type = excluded.provider_type,
                        fields_json = excluded.fields_json,
                        source = excluded.source,
                        updated_at = excluded.updated_at
                    """,
                    (
                        record["id"],
                        record["provider_name"],
                        record["provider_type"],
                        record["data_type"],
                        record["symbol"],
                        record["timestamp"],
                        record["metric"],
                        json.dumps(record["fields"], ensure_ascii=False),
                        record["source"],
                        record["created_at"],
                        record["updated_at"],
                    ),
                )
                saved.append(record)
        return saved

    def list_market_records(
        self,
        symbol: str | None = None,
        data_type: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        params: list[Any] = []
        clauses: list[str] = []
        if symbol:
            clauses.append("symbol = ?")
            params.append(symbol.strip().upper())
        if data_type:
            clauses.append("data_type = ?")
            params.append(data_type.strip())
        where = f"where {' and '.join(clauses)}" if clauses else ""
        sql = f"""
            select id, provider_name, provider_type, data_type, symbol,
                   timestamp, metric, fields_json, source, created_at, updated_at
            from market_data
            {where}
            order by timestamp desc, updated_at desc
            limit ?
        """
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [_market_row_to_dict(row) for row in rows]

    def market_data_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            by_type = conn.execute(
                """
                select data_type, count(*) as row_count,
                       min(timestamp) as first_timestamp,
                       max(timestamp) as last_timestamp
                from market_data
                group by data_type
                order by data_type
                """
            ).fetchall()
            by_symbol = conn.execute(
                """
                select symbol, count(*) as row_count,
                       min(timestamp) as first_timestamp,
                       max(timestamp) as last_timestamp
                from market_data
                group by symbol
                order by row_count desc, symbol
                limit 20
                """
            ).fetchall()
        return {
            "by_type": [dict(row) for row in by_type],
            "top_symbols": [dict(row) for row in by_symbol],
        }

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                create table if not exists json_documents (
                    name text primary key,
                    data_json text not null,
                    updated_at text not null
                );
                create table if not exists system_settings (
                    key text primary key,
                    value_json text not null,
                    updated_at text not null
                );
                create table if not exists data_sources (
                    provider_name text primary key,
                    provider_type text not null,
                    enabled integer not null default 1,
                    priority integer not null default 100,
                    config_json text not null default '{}',
                    test_status text not null default 'untested',
                    test_message text not null default '',
                    updated_at text not null
                );
                create table if not exists data_capabilities (
                    capability text not null,
                    provider_name text not null,
                    enabled integer not null default 1,
                    priority integer not null default 100,
                    fallback_provider text not null default '',
                    updated_at text not null,
                    primary key (capability, provider_name)
                );
                create table if not exists data_sync_logs (
                    id integer primary key autoincrement,
                    provider_name text not null,
                    sync_type text not null,
                    status text not null,
                    message text not null default '',
                    started_at text not null,
                    finished_at text
                );
                create table if not exists data_sync_state (
                    provider_name text not null,
                    capability text not null,
                    symbol text not null default '',
                    status text not null,
                    row_count integer not null default 0,
                    last_success_at text,
                    last_error text not null default '',
                    last_source_timestamp text not null default '',
                    updated_at text not null,
                    primary key (provider_name, capability, symbol)
                );
                create table if not exists market_data (
                    id text primary key,
                    provider_name text not null,
                    provider_type text not null,
                    data_type text not null,
                    symbol text not null,
                    timestamp text not null,
                    metric text not null default '',
                    fields_json text not null default '{}',
                    source text not null default '',
                    created_at text not null,
                    updated_at text not null
                );
                create index if not exists idx_market_data_symbol_type_time
                    on market_data(symbol, data_type, timestamp);
                create index if not exists idx_market_data_type_time
                    on market_data(data_type, timestamp);
                create table if not exists evidence_items (
                    id text primary key,
                    symbol text not null,
                    evidence_type text not null,
                    title text not null,
                    content text not null,
                    source text not null default 'manual',
                    source_date text not null default '',
                    linked_decision_id text not null default '',
                    created_at text not null
                );
                create index if not exists idx_evidence_symbol_created
                    on evidence_items(symbol, created_at);
                create table if not exists ai_runs (
                    id text primary key,
                    agent_type text not null,
                    input_hash text not null,
                    output_json text not null,
                    compliance_status text not null,
                    ai_enabled integer not null default 0,
                    created_at text not null
                );
                create index if not exists idx_ai_runs_created
                    on ai_runs(created_at);
                create table if not exists rule_results (
                    id text primary key,
                    decision_id text not null,
                    rule_code text not null,
                    rule_name text not null,
                    status text not null,
                    severity text not null,
                    category text not null,
                    message text not null,
                    params_json text not null default '{}',
                    created_at text not null
                );
                create index if not exists idx_rule_results_decision
                    on rule_results(decision_id);
                create index if not exists idx_rule_results_created
                    on rule_results(created_at);
                create table if not exists reviews (
                    id text primary key,
                    period text not null,
                    review_json text not null,
                    discipline_score real not null default 0,
                    decision_count integer not null default 0,
                    status_summary text not null default '{}',
                    created_at text not null
                );
                create index if not exists idx_reviews_period_created
                    on reviews(period, created_at);
                """
            )
            for key, value in {
                "storage_mode": "sqlite",
                "ai_enabled": False,
                "strict_mode": True,
                "discipline_mode": "block",
                "ai_api_token": "",
                "ai_api_base_url": "",
                "ai_model": "gpt-5.5",
            }.items():
                conn.execute(
                    """
                    insert or ignore into system_settings(key, value_json, updated_at)
                    values (?, ?, ?)
                    """,
                    (key, json.dumps(value), _utc_now()),
                )

    def _test_provider(self, provider_type: str, config: dict[str, Any]) -> dict[str, str]:
        normalized = provider_type.lower()
        path = str(config.get("local_path", "")).strip()
        token = str(config.get("api_token") or config.get("token") or "").strip()
        base_url = str(config.get("api_base_url") or config.get("base_url") or "").strip()

        if normalized == "manual":
            return {
                "status": "ok",
                "message": "Manual provider is available; data can be entered or imported locally.",
            }
        if normalized == "csv":
            return _test_local_file(path, {".csv"}, "CSV")
        if normalized == "excel":
            return _test_local_file(path, {".xlsx", ".xlsm"}, "Excel")
        if normalized == "qmt":
            if not path:
                return {
                    "status": "blocked",
                    "message": "QMT provider requires local_path pointing to the QMT/xtquant data directory.",
                }
            if not Path(path).exists():
                return {
                    "status": "blocked",
                    "message": f"QMT local_path does not exist: {path}",
                }
            return {
                "status": "not_implemented",
                "message": "QMT path is reachable, but the QMT connector is not implemented yet.",
            }
        if normalized == "tushare":
            if not token:
                return {
                    "status": "blocked",
                    "message": "TuShare provider requires api_token in config.",
                }
            if importlib.util.find_spec("tushare") is None:
                return {
                    "status": "blocked",
                    "message": "TuShare token is configured, but the tushare Python package is not installed.",
                }
            return {
                "status": "ok",
                "message": "TuShare provider is ready. Sync requires a symbol filter to avoid large data pulls.",
            }
        if normalized == "akshare":
            if importlib.util.find_spec("akshare") is None:
                return {
                    "status": "blocked",
                    "message": "AkShare provider requires the akshare Python package, which is not installed.",
                }
            return {
                "status": "ok",
                "message": "AkShare provider is ready. Sync requires a symbol filter to avoid large data pulls.",
            }
        if normalized == "eastmoney":
            return {
                "status": "not_implemented",
                "message": "Eastmoney connector is not implemented yet; configuration was saved for future use.",
            }
        if normalized in {"yahoo", "yahoo finance", "yahoo_finance"}:
            return {
                "status": "not_implemented",
                "message": "Yahoo Finance connector is not implemented yet; configuration was saved for future use.",
            }
        if normalized in {"custom", "custom api", "custom_api"}:
            if not base_url:
                return {
                    "status": "blocked",
                    "message": "Custom API provider requires api_base_url in config.",
                }
            return {
                "status": "not_implemented",
                "message": "Custom API base URL is configured, but field mapping connector is not implemented yet.",
            }
        return {
            "status": "not_implemented",
            "message": f"Provider type {provider_type} is saved, but no connector exists yet.",
        }

    def save_evidence(self, item: dict[str, Any]) -> dict[str, Any]:
        evidence = {
            "id": str(item["id"]),
            "symbol": str(item["symbol"]).strip().upper(),
            "evidence_type": str(item.get("evidence_type", "user_note")),
            "title": str(item.get("title", "")).strip(),
            "content": str(item.get("content", "")).strip(),
            "source": str(item.get("source", "manual")).strip() or "manual",
            "source_date": str(item.get("source_date", "")).strip(),
            "linked_decision_id": str(item.get("linked_decision_id", "")).strip(),
            "created_at": str(item["created_at"]),
        }
        if not evidence["symbol"] or not evidence["title"] or not evidence["content"]:
            raise ValueError("symbol, title, and content are required")
        with self._connect() as conn:
            conn.execute(
                """
                insert into evidence_items(
                    id, symbol, evidence_type, title, content, source,
                    source_date, linked_decision_id, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(id) do update set
                    symbol = excluded.symbol,
                    evidence_type = excluded.evidence_type,
                    title = excluded.title,
                    content = excluded.content,
                    source = excluded.source,
                    source_date = excluded.source_date,
                    linked_decision_id = excluded.linked_decision_id,
                    created_at = excluded.created_at
                """,
                (
                    evidence["id"],
                    evidence["symbol"],
                    evidence["evidence_type"],
                    evidence["title"],
                    evidence["content"],
                    evidence["source"],
                    evidence["source_date"],
                    evidence["linked_decision_id"],
                    evidence["created_at"],
                ),
            )
        return evidence

    def list_evidence(
        self,
        symbol: str | None = None,
        evidence_type: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        params: list[Any] = []
        clauses: list[str] = []
        if symbol:
            clauses.append("symbol = ?")
            params.append(symbol.strip().upper())
        if evidence_type:
            clauses.append("evidence_type = ?")
            params.append(evidence_type.strip())
        where = f"where {' and '.join(clauses)}" if clauses else ""
        sql = f"""
            select id, symbol, evidence_type, title, content, source, source_date,
                   linked_decision_id, created_at
            from evidence_items
            {where}
            order by created_at desc
        """
        if limit:
            sql += " limit ?"
            params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def list_evidence_by_ids(self, ids: list[str]) -> list[dict[str, Any]]:
        clean_ids = [str(item).strip() for item in ids if str(item).strip()]
        if not clean_ids:
            return []
        placeholders = ", ".join("?" for _ in clean_ids)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                select id, symbol, evidence_type, title, content, source, source_date,
                       linked_decision_id, created_at
                from evidence_items
                where id in ({placeholders})
                order by created_at desc
                """,
                clean_ids,
            ).fetchall()
        by_id = {row["id"]: dict(row) for row in rows}
        return [by_id[item] for item in clean_ids if item in by_id]

    def save_ai_run(self, item: dict[str, Any]) -> dict[str, Any]:
        run = {
            "id": str(item["id"]),
            "agent_type": str(item.get("agent_type", "copilot")),
            "input_hash": str(item["input_hash"]),
            "output_json": json.dumps(item.get("output", {}), ensure_ascii=False),
            "compliance_status": str(item.get("compliance_status", "pass")),
            "ai_enabled": 1 if item.get("ai_enabled") else 0,
            "created_at": str(item["created_at"]),
        }
        with self._connect() as conn:
            conn.execute(
                """
                insert into ai_runs(
                    id, agent_type, input_hash, output_json, compliance_status,
                    ai_enabled, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run["id"],
                    run["agent_type"],
                    run["input_hash"],
                    run["output_json"],
                    run["compliance_status"],
                    run["ai_enabled"],
                    run["created_at"],
                ),
            )
        return {
            **run,
            "output": item.get("output", {}),
            "ai_enabled": bool(run["ai_enabled"]),
        }

    def list_ai_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                select id, agent_type, input_hash, output_json, compliance_status,
                       ai_enabled, created_at
                from ai_runs
                order by created_at desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "id": row["id"],
                "agent_type": row["agent_type"],
                "input_hash": row["input_hash"],
                "output": json.loads(row["output_json"]),
                "compliance_status": row["compliance_status"],
                "ai_enabled": bool(row["ai_enabled"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def save_rule_results(
        self, items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        normalized = []
        for item in items:
            normalized.append(
                {
                    "id": str(item["id"]),
                    "decision_id": str(item["decision_id"]),
                    "rule_code": str(item["rule_code"]),
                    "rule_name": str(item.get("rule_name", "")),
                    "status": str(item["status"]),
                    "severity": str(item.get("severity", "info")),
                    "category": str(item.get("category", "general")),
                    "message": str(item.get("message", "")),
                    "params": dict(item.get("params", {})),
                    "created_at": str(item["created_at"]),
                }
            )
        with self._connect() as conn:
            conn.executemany(
                """
                insert into rule_results(
                    id, decision_id, rule_code, rule_name, status, severity,
                    category, message, params_json, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item["id"],
                        item["decision_id"],
                        item["rule_code"],
                        item["rule_name"],
                        item["status"],
                        item["severity"],
                        item["category"],
                        item["message"],
                        json.dumps(item["params"], ensure_ascii=False),
                        item["created_at"],
                    )
                    for item in normalized
                ],
            )
        return normalized

    def list_rule_results(
        self,
        decision_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        params: list[Any] = []
        where = ""
        if decision_id:
            where = "where decision_id = ?"
            params.append(decision_id)
        sql = f"""
            select id, decision_id, rule_code, rule_name, status, severity,
                   category, message, params_json, created_at
            from rule_results
            {where}
            order by created_at desc
            limit ?
        """
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [
            {
                "id": row["id"],
                "decision_id": row["decision_id"],
                "rule_code": row["rule_code"],
                "rule_name": row["rule_name"],
                "status": row["status"],
                "severity": row["severity"],
                "category": row["category"],
                "message": row["message"],
                "params": json.loads(row["params_json"] or "{}"),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def save_review_snapshot(self, item: dict[str, Any]) -> dict[str, Any]:
        review = dict(item.get("review", {}))
        snapshot = {
            "id": str(item["id"]),
            "period": str(item["period"]),
            "review": review,
            "discipline_score": float(item.get("discipline_score", 0)),
            "decision_count": int(item.get("decision_count", 0)),
            "status_summary": dict(item.get("status_summary", {})),
            "created_at": str(item["created_at"]),
        }
        with self._connect() as conn:
            conn.execute(
                """
                insert into reviews(
                    id, period, review_json, discipline_score, decision_count,
                    status_summary, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot["id"],
                    snapshot["period"],
                    json.dumps(snapshot["review"], ensure_ascii=False),
                    snapshot["discipline_score"],
                    snapshot["decision_count"],
                    json.dumps(snapshot["status_summary"], ensure_ascii=False),
                    snapshot["created_at"],
                ),
            )
        return snapshot

    def list_review_snapshots(
        self,
        period: str | None = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        params: list[Any] = []
        where = ""
        if period:
            where = "where period = ?"
            params.append(period)
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                select id, period, review_json, discipline_score, decision_count,
                       status_summary, created_at
                from reviews
                {where}
                order by created_at desc
                limit ?
                """,
                params,
            ).fetchall()
        return [
            {
                "id": row["id"],
                "period": row["period"],
                "review": json.loads(row["review_json"]),
                "discipline_score": row["discipline_score"],
                "decision_count": row["decision_count"],
                "status_summary": json.loads(row["status_summary"] or "{}"),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_review_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                select id, period, review_json, discipline_score, decision_count,
                       status_summary, created_at
                from reviews
                where id = ?
                """,
                (snapshot_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "period": row["period"],
            "review": json.loads(row["review_json"]),
            "discipline_score": row["discipline_score"],
            "decision_count": row["decision_count"],
            "status_summary": json.loads(row["status_summary"] or "{}"),
            "created_at": row["created_at"],
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _test_local_file(
    path: str,
    allowed_suffixes: set[str],
    label: str,
) -> dict[str, str]:
    if not path:
        return {
            "status": "blocked",
            "message": f"{label} provider requires config.local_path.",
        }
    source = Path(path)
    if not source.exists():
        return {
            "status": "blocked",
            "message": f"{label} local_path does not exist: {path}",
        }
    if source.suffix.lower() not in allowed_suffixes:
        allowed = ", ".join(sorted(allowed_suffixes))
        return {
            "status": "warning",
            "message": f"{label} provider expected {allowed}; got {source.suffix or '<none>'}.",
        }
    return {
        "status": "ok",
        "message": f"{label} provider is ready: {path}",
    }


def _normalize_market_record(item: dict[str, Any], now: str) -> dict[str, Any]:
    provider_name = str(item.get("provider_name", "")).strip() or "unknown"
    data_type = str(item.get("data_type", "")).strip()
    symbol = str(item.get("symbol", "")).strip().upper()
    timestamp = str(item.get("timestamp", "")).strip()
    metric = str(item.get("metric", "")).strip()
    if not data_type or not symbol or not timestamp:
        raise ValueError("market record requires data_type, symbol, and timestamp")
    fields = item.get("fields", {})
    if not isinstance(fields, dict):
        fields = {"value": fields}
    return {
        "id": _market_record_id(provider_name, data_type, symbol, timestamp, metric),
        "provider_name": provider_name,
        "provider_type": str(item.get("provider_type", "")).strip(),
        "data_type": data_type,
        "symbol": symbol,
        "timestamp": timestamp,
        "metric": metric,
        "fields": fields,
        "source": str(item.get("source", "")).strip(),
        "created_at": str(item.get("created_at") or now),
        "updated_at": now,
    }


def _market_record_id(
    provider_name: str,
    data_type: str,
    symbol: str,
    timestamp: str,
    metric: str,
) -> str:
    raw = "|".join([provider_name, data_type, symbol, timestamp, metric])
    return sha256(raw.encode("utf-8")).hexdigest()[:32]


def _market_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["fields"] = json.loads(item.pop("fields_json") or "{}")
    return item
