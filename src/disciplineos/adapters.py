from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import Position, Trade, position_from_dict, to_dict, trade_from_dict


@dataclass(slots=True)
class ImportResult:
    kind: str
    source: str
    row_count: int = 0
    imported: int = 0
    skipped: int = 0
    missing_columns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    items: list[dict[str, Any]] = field(default_factory=list)


REQUIRED_COLUMNS = {
    "positions": {"symbol", "quantity", "cost_price", "current_price"},
    "trades": {"symbol", "action", "quantity", "price"},
}


def import_records(path: str | Path, kind: str) -> ImportResult:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Import file not found: {source}")
    headers, rows = read_tabular_rows(source)
    if kind == "positions":
        return _import_positions(source, headers, rows)
    if kind == "trades":
        return _import_trades(source, headers, rows)
    raise ValueError(f"Unsupported import kind: {kind}")


def read_tabular_rows(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = [str(item or "").strip() for item in reader.fieldnames or []]
            return headers, [dict(row) for row in reader]
    if suffix in {".xlsx", ".xlsm"}:
        return _read_excel_rows(path)
    raise ValueError(f"Unsupported import file type: {path.suffix}")


def _read_excel_rows(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("Excel import requires openpyxl.") from exc

    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return [], []
    headers = [str(value or "").strip() for value in rows[0]]
    records: list[dict[str, Any]] = []
    for row in rows[1:]:
        if not any(value is not None and str(value).strip() for value in row):
            continue
        records.append(
            {
                headers[index]: row[index] if index < len(row) else None
                for index in range(len(headers))
                if headers[index]
            }
        )
    return headers, records


def _import_positions(
    source: Path,
    headers: list[str],
    rows: list[dict[str, Any]],
) -> ImportResult:
    result = ImportResult(
        kind="positions",
        source=str(source),
        row_count=len(rows),
        missing_columns=_missing_columns(headers, "positions"),
    )
    if result.missing_columns:
        result.skipped = len(rows)
        result.errors.append(
            f"missing required columns: {', '.join(result.missing_columns)}"
        )
        return result
    for index, row in enumerate(rows, start=2):
        try:
            position = position_from_dict(
                {
                    "symbol": _text(row, "symbol").upper(),
                    "name": _text(row, "name") or _text(row, "symbol").upper(),
                    "asset_type": _text(row, "asset_type", "stock"),
                    "market": _text(row, "market", "A"),
                    "sector": _text(row, "sector", "unknown"),
                    "theme": _text(row, "theme", "unknown"),
                    "currency": _text(row, "currency", "CNY"),
                    "quantity": _number(row, "quantity"),
                    "cost_price": _number(row, "cost_price"),
                    "current_price": _number(row, "current_price"),
                }
            )
            if not position.symbol:
                raise ValueError("symbol is required")
            result.items.append(to_dict(position))
            result.imported += 1
        except Exception as exc:
            result.skipped += 1
            result.errors.append(f"row {index}: {exc}")
    return result


def _import_trades(
    source: Path,
    headers: list[str],
    rows: list[dict[str, Any]],
) -> ImportResult:
    result = ImportResult(
        kind="trades",
        source=str(source),
        row_count=len(rows),
        missing_columns=_missing_columns(headers, "trades"),
    )
    if result.missing_columns:
        result.skipped = len(rows)
        result.errors.append(
            f"missing required columns: {', '.join(result.missing_columns)}"
        )
        return result
    for index, row in enumerate(rows, start=2):
        try:
            amount = _number(row, "amount")
            quantity = _number(row, "quantity")
            price = _number(row, "price")
            if amount == 0 and quantity and price:
                amount = quantity * price
            trade = trade_from_dict(
                {
                    "symbol": _text(row, "symbol").upper(),
                    "action": _text(row, "action", "buy").lower(),
                    "quantity": quantity,
                    "price": price,
                    "amount": amount,
                    "fee": _number(row, "fee"),
                    "traded_at": _text(row, "traded_at"),
                    "note": _text(row, "note"),
                }
            )
            if not trade.symbol:
                raise ValueError("symbol is required")
            result.items.append(to_dict(trade))
            result.imported += 1
        except Exception as exc:
            result.skipped += 1
            result.errors.append(f"row {index}: {exc}")
    return result


def _missing_columns(headers: list[str], kind: str) -> list[str]:
    normalized = {item.strip() for item in headers if item.strip()}
    return sorted(REQUIRED_COLUMNS[kind] - normalized)


def _text(row: dict[str, Any], key: str, default: str = "") -> str:
    value = row.get(key, default)
    if value is None:
        return default
    return str(value).strip()


def _number(row: dict[str, Any], key: str) -> float:
    value = row.get(key, 0)
    if value in (None, ""):
        return 0.0
    return float(value)
