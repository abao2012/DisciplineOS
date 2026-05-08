from __future__ import annotations

import json
import string
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .models import to_dict
from .services import DisciplineService, seed_demo_data


STATIC_DIR = Path(__file__).parent / "static"


def run(data_dir: str, host: str = "127.0.0.1", port: int = 8765) -> None:
    service = DisciplineService(data_dir)

    class Handler(DisciplineHandler):
        discipline_service = service

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"DisciplineOS web UI: http://{host}:{port}")
    print(f"Data directory: {data_dir}")
    server.serve_forever()


class DisciplineHandler(BaseHTTPRequestHandler):
    discipline_service: DisciplineService

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/app.js":
            self._send_file(STATIC_DIR / "app.js", "text/javascript; charset=utf-8")
            return
        if parsed.path == "/styles.css":
            self._send_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
            return
        if parsed.path == "/api/dashboard":
            month = parse_qs(parsed.query).get("month", [_current_month()])[0]
            self._send_json(self.discipline_service.dashboard(month))
            return
        if parsed.path == "/api/card-templates":
            self._send_json(self.discipline_service.list_card_templates())
            return
        if parsed.path == "/api/settings":
            self._send_json(self.discipline_service.list_settings())
            return
        if parsed.path == "/api/data-sources":
            self._send_json(
                {
                    "data_sources": self.discipline_service.list_data_sources(),
                    "data_capabilities": self.discipline_service.list_capabilities(),
                    "data_sync_logs": self.discipline_service.list_data_sync_logs(),
                }
            )
            return
        if parsed.path == "/api/evidence":
            query = parse_qs(parsed.query)
            symbol = query.get("symbol", [None])[0]
            evidence_type = query.get("evidence_type", [None])[0]
            self._send_json(
                {
                    "evidence_items": self.discipline_service.list_evidence(
                        symbol=symbol,
                        evidence_type=evidence_type,
                    )
                }
            )
            return
        if parsed.path == "/api/ai-runs":
            self._send_json({"ai_runs": self.discipline_service.list_ai_runs()})
            return
        if parsed.path == "/api/rule-results":
            query = parse_qs(parsed.query)
            decision_id = query.get("decision_id", [None])[0]
            self._send_json(
                {
                    "rule_results": self.discipline_service.list_rule_results(
                        decision_id=decision_id
                    )
                }
            )
            return
        if parsed.path == "/api/reviews":
            query = parse_qs(parsed.query)
            month = query.get("month", [None])[0]
            self._send_json(
                {
                    "review_snapshots": self.discipline_service.list_review_snapshots(
                        month=month
                    )
                }
            )
            return
        if parsed.path == "/api/reports":
            self._send_json(
                {"review_reports": self.discipline_service.list_review_reports()}
            )
            return
        if parsed.path == "/api/backups":
            self._send_json(
                {"backup_archives": self.discipline_service.list_backups()}
            )
            return
        if parsed.path == "/api/health":
            self._send_json(self.discipline_service.data_health_check())
            return
        if parsed.path == "/api/path-browser":
            query = parse_qs(parsed.query)
            path = query.get("path", [""])[0]
            extensions = query.get("extensions", [""])[0]
            try:
                self._send_json(_browse_path(path, extensions=extensions))
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
            return
        if parsed.path == "/api/copilot":
            month = parse_qs(parsed.query).get("month", [_current_month()])[0]
            self._send_json(self.discipline_service.copilot(month))
            return

        self._send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/demo":
            seed_demo_data(self.discipline_service)
            self._send_json({"ok": True})
            return

        if parsed.path == "/api/check":
            payload = self._read_json()
            try:
                result = self.discipline_service.check_decision_payload(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json(result)
            return

        if parsed.path == "/api/profile":
            payload = self._read_json()
            try:
                profile = self.discipline_service.save_profile_dict(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "profile": to_dict(profile)})
            return

        if parsed.path == "/api/settings":
            payload = self._read_json()
            try:
                settings = self.discipline_service.save_settings(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "settings": settings})
            return

        if parsed.path == "/api/data-sources":
            payload = self._read_json()
            try:
                source = self.discipline_service.save_data_source(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "source": source})
            return

        if parsed.path == "/api/data-capabilities":
            payload = self._read_json()
            try:
                mapping = self.discipline_service.save_capability(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "mapping": mapping})
            return

        if parsed.path == "/api/data-sync":
            payload = self._read_json()
            try:
                result = self.discipline_service.sync_capability(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json(result)
            return

        if parsed.path == "/api/evidence":
            payload = self._read_json()
            try:
                evidence = self.discipline_service.save_evidence_dict(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "evidence": evidence})
            return

        if parsed.path == "/api/reviews":
            payload = self._read_json()
            month = str(payload.get("month") or _current_month())
            try:
                snapshot = self.discipline_service.save_review_snapshot(month)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "review_snapshot": snapshot})
            return

        if parsed.path == "/api/reviews/export":
            payload = self._read_json()
            snapshot_id = str(payload.get("snapshot_id", "")).strip()
            if not snapshot_id:
                self._send_error(HTTPStatus.BAD_REQUEST, "Missing snapshot_id")
                return
            try:
                report = self.discipline_service.export_review_snapshot(
                    snapshot_id=snapshot_id,
                    export_format=str(payload.get("format", "markdown")),
                )
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "report": report})
            return

        if parsed.path == "/api/reviews/compare":
            payload = self._read_json()
            left_snapshot_id = str(payload.get("left_snapshot_id", "")).strip()
            right_snapshot_id = str(payload.get("right_snapshot_id", "")).strip()
            if not left_snapshot_id or not right_snapshot_id:
                self._send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Missing left_snapshot_id or right_snapshot_id",
                )
                return
            try:
                comparison = self.discipline_service.compare_review_snapshots(
                    left_snapshot_id=left_snapshot_id,
                    right_snapshot_id=right_snapshot_id,
                )
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "comparison": comparison})
            return

        if parsed.path == "/api/backups":
            try:
                backup = self.discipline_service.create_backup()
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "backup": backup})
            return

        if parsed.path == "/api/backups/restore":
            payload = self._read_json()
            filename = str(payload.get("filename", "")).strip()
            if not filename:
                self._send_error(HTTPStatus.BAD_REQUEST, "Missing filename")
                return
            try:
                restored = self.discipline_service.restore_backup(filename)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "restore": restored})
            return

        if parsed.path == "/api/cards":
            payload = self._read_json()
            try:
                card = self.discipline_service.save_card_dict(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "card": to_dict(card)})
            return

        if parsed.path == "/api/generate-card":
            payload = self._read_json()
            try:
                card = self.discipline_service.generate_card(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "card": to_dict(card)})
            return

        if parsed.path == "/api/positions":
            payload = self._read_json()
            try:
                position = self.discipline_service.save_position_dict(payload)
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "position": to_dict(position)})
            return

        if parsed.path == "/api/import":
            payload = self._read_json()
            try:
                result = self.discipline_service.import_file(
                    kind=str(payload.get("kind", "")),
                    path=str(payload.get("path", "")),
                    commit=bool(payload.get("confirm", True)),
                )
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "result": result})
            return

        if parsed.path == "/api/import-preview":
            payload = self._read_json()
            try:
                result = self.discipline_service.preview_import_file(
                    kind=str(payload.get("kind", "")),
                    path=str(payload.get("path", "")),
                )
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "result": result})
            return

        if parsed.path == "/api/financial-report":
            payload = self._read_json()
            try:
                if payload.get("path"):
                    summary = self.discipline_service.summarize_financial_report_file(
                        path=str(payload.get("path", "")),
                        symbol=str(payload.get("symbol", "")),
                        period=str(payload.get("period", "")),
                        material_type=str(
                            payload.get("material_type", "financial_report")
                        ),
                        ai_online_search=bool(payload.get("ai_online_search", False)),
                    )
                else:
                    summary = self.discipline_service.summarize_financial_report_text(
                        payload
                    )
            except Exception as exc:
                self._send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._send_json({"ok": True, "summary": summary})
            return

        if parsed.path == "/api/violations/resolve":
            payload = self._read_json()
            violation_id = str(payload.get("id", ""))
            if not violation_id:
                self._send_error(HTTPStatus.BAD_REQUEST, "Missing violation id")
                return
            resolved = self.discipline_service.resolve_violation(
                violation_id,
                note=str(payload.get("note", "")),
            )
            self._send_json({"ok": True, "resolved": resolved})
            return

        self._send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/cards":
            symbol = parse_qs(parsed.query).get("symbol", [""])[0]
            if not symbol:
                self._send_error(HTTPStatus.BAD_REQUEST, "Missing symbol")
                return
            deleted = self.discipline_service.delete_card(symbol)
            self._send_json({"ok": True, "deleted": deleted})
            return

        if parsed.path == "/api/positions":
            symbol = parse_qs(parsed.query).get("symbol", [""])[0]
            if not symbol:
                self._send_error(HTTPStatus.BAD_REQUEST, "Missing symbol")
                return
            deleted = self.discipline_service.delete_position(symbol)
            self._send_json({"ok": True, "deleted": deleted})
            return

        self._send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._send_error(HTTPStatus.NOT_FOUND, "Static file not found")
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_error(self, status: HTTPStatus, message: str) -> None:
        data = json.dumps({"ok": False, "error": message}, ensure_ascii=False).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def _current_month() -> str:
    return datetime.now().strftime("%Y-%m")


def _browse_path(raw_path: str, extensions: str = "") -> dict:
    allowed_extensions = {
        extension.strip().lower()
        for extension in extensions.split(",")
        if extension.strip()
    }
    if not raw_path:
        return {
            "current_path": "",
            "parent_path": "",
            "entries": _path_roots(),
        }
    path = Path(raw_path).expanduser()
    if path.is_file():
        path = path.parent
    if not path.exists():
        path = Path.cwd()
    entries = []
    for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        try:
            if allowed_extensions and child.is_file() and child.suffix.lower() not in allowed_extensions:
                continue
            entries.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "is_dir": child.is_dir(),
                }
            )
        except OSError:
            continue
        if len(entries) >= 300:
            break
    return {
        "current_path": str(path),
        "parent_path": str(path.parent) if path.parent != path else "",
        "entries": entries,
    }


def _path_roots() -> list[dict]:
    roots = []
    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:\\")
        if root.exists():
            roots.append({"name": str(root), "path": str(root), "is_dir": True})
    home = Path.home()
    if home.exists():
        roots.append({"name": f"Home ({home})", "path": str(home), "is_dir": True})
    cwd = Path.cwd()
    roots.append({"name": f"Workspace ({cwd})", "path": str(cwd), "is_dir": True})
    return roots
