from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .adapters import import_records, read_tabular_rows


@dataclass(slots=True)
class ConnectorResult:
    provider_name: str
    provider_type: str
    capability: str
    source: str
    row_count: int = 0
    imported: int = 0
    skipped: int = 0
    missing_columns: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    items: list[dict[str, Any]] = field(default_factory=list)
    market_records: list[dict[str, Any]] = field(default_factory=list)


class ProviderConnector(Protocol):
    def preview(self, capability: str) -> ConnectorResult:
        ...


class CsvExcelConnector:
    def __init__(self, source: dict[str, Any]) -> None:
        self.source = source
        self.provider_name = str(source.get("provider_name", ""))
        self.provider_type = str(source.get("provider_type", "csv"))
        self.path = str(source.get("config", {}).get("local_path", "")).strip()

    def preview(self, capability: str) -> ConnectorResult:
        if not self.path:
            return ConnectorResult(
                provider_name=self.provider_name,
                provider_type=self.provider_type,
                capability=capability,
                source="",
                errors=[f"Provider {self.provider_name} has no local_path."],
            )
        if capability in {"positions", "trades"}:
            imported = import_records(self.path, capability)
            return ConnectorResult(
                provider_name=self.provider_name,
                provider_type=self.provider_type,
                capability=capability,
                source=imported.source,
                row_count=imported.row_count,
                imported=imported.imported,
                skipped=imported.skipped,
                missing_columns=imported.missing_columns,
                errors=imported.errors,
                items=imported.items,
            )
        return _preview_market_evidence(
            provider_name=self.provider_name,
            provider_type=self.provider_type,
            path=self.path,
            capability=capability,
        )


def build_connector(source: dict[str, Any]) -> ProviderConnector:
    provider_type = str(source.get("provider_type", "")).lower()
    if provider_type in {"csv", "excel"}:
        return CsvExcelConnector(source)
    if provider_type == "akshare":
        return AkShareConnector(source)
    if provider_type == "tushare":
        return TuShareConnector(source)
    raise ValueError(
        f"Provider type {source.get('provider_type')} has no executable connector yet."
    )


class AkShareConnector:
    def __init__(self, source: dict[str, Any]) -> None:
        self.source = source
        self.provider_name = str(source.get("provider_name", "akshare"))
        self.provider_type = "akshare"
        self.config = dict(source.get("config", {}))
        self.symbol = _normalize_symbol(str(self.config.get("symbol", "")))

    def preview(self, capability: str) -> ConnectorResult:
        if not self.symbol:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                "AkShare sync requires a symbol filter, for example 300750.",
            )
        try:
            akshare = importlib.import_module("akshare")
        except ImportError:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                "AkShare Python package is not installed. Install optional data dependencies first.",
            )

        try:
            if capability in {"price_daily", "volume"}:
                records = _frame_records(
                    akshare.stock_zh_a_hist(
                        symbol=self.symbol,
                        period="daily",
                        start_date=_date_compact(self.config.get("start_date")),
                        end_date=_date_compact(self.config.get("end_date")) or _today_compact(),
                        adjust=str(self.config.get("adjust", "")),
                    )
                )
                return _market_records_to_result(
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                    capability=capability,
                    source="akshare.stock_zh_a_hist",
                    records=records,
                    date_key="日期",
                    close_key="收盘",
                    change_key="涨跌幅",
                    volume_key="成交量",
                    symbol=self.symbol,
                )
            if capability == "price_5min":
                records = _frame_records(
                    akshare.stock_zh_a_hist_min_em(
                        symbol=self.symbol,
                        period="5",
                        adjust=str(self.config.get("adjust", "")),
                    )
                )
                return _market_records_to_result(
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                    capability=capability,
                    source="akshare.stock_zh_a_hist_min_em",
                    records=records,
                    date_key="时间",
                    close_key="收盘",
                    volume_key="成交量",
                    symbol=self.symbol,
                )
            if capability == "financial_metrics":
                records = _frame_records(
                    akshare.stock_financial_analysis_indicator(symbol=self.symbol)
                )
                return _financial_records_to_result(
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                    source="akshare.stock_financial_analysis_indicator",
                    symbol=self.symbol,
                    records=records,
                    period_keys=("日期", "报告期", "period", "end_date"),
                )
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                f"Unsupported AkShare capability: {capability}",
            )
        except Exception as exc:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                f"AkShare sync failed: {exc}",
            )


class TuShareConnector:
    def __init__(self, source: dict[str, Any]) -> None:
        self.source = source
        self.provider_name = str(source.get("provider_name", "tushare"))
        self.provider_type = "tushare"
        self.config = dict(source.get("config", {}))
        self.symbol = _normalize_symbol(str(self.config.get("symbol", "")))
        self.token = str(self.config.get("api_token") or self.config.get("token") or "").strip()

    def preview(self, capability: str) -> ConnectorResult:
        if not self.token:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                "TuShare sync requires api_token in provider config.",
            )
        if not self.symbol:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                "TuShare sync requires a symbol filter, for example 300750.",
            )
        try:
            tushare = importlib.import_module("tushare")
        except ImportError:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                "TuShare Python package is not installed. Install optional data dependencies first.",
            )

        try:
            if hasattr(tushare, "set_token"):
                tushare.set_token(self.token)
            pro = tushare.pro_api(self.token) if callable(getattr(tushare, "pro_api", None)) else None
            if pro is None:
                return _connector_error(
                    self.provider_name,
                    self.provider_type,
                    capability,
                    "TuShare module does not expose pro_api.",
                )
            ts_code = _to_tushare_code(self.symbol)
            if capability in {"price_daily", "volume"}:
                records = _frame_records(
                    pro.daily(ts_code=ts_code, **_tushare_date_kwargs(self.config))
                )
                return _market_records_to_result(
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                    capability=capability,
                    source="tushare.pro.daily",
                    records=records,
                    date_key="trade_date",
                    close_key="close",
                    change_key="pct_chg",
                    volume_key="vol",
                    symbol=self.symbol,
                )
            if capability == "price_5min":
                if not callable(getattr(tushare, "pro_bar", None)):
                    return _connector_error(
                        self.provider_name,
                        self.provider_type,
                        capability,
                        "TuShare pro_bar is unavailable; cannot sync 5min K.",
                    )
                records = _frame_records(
                    tushare.pro_bar(
                        ts_code=ts_code,
                        freq="5min",
                        asset="E",
                        adj=str(self.config.get("adjust", "")) or None,
                        **_tushare_datetime_kwargs(self.config),
                    )
                )
                return _market_records_to_result(
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                    capability=capability,
                    source="tushare.pro_bar",
                    records=records,
                    date_key="trade_time",
                    close_key="close",
                    volume_key="vol",
                    symbol=self.symbol,
                )
            if capability == "financial_metrics":
                records = _frame_records(
                    pro.fina_indicator(ts_code=ts_code, **_tushare_date_kwargs(self.config))
                )
                return _financial_records_to_result(
                    provider_name=self.provider_name,
                    provider_type=self.provider_type,
                    source="tushare.pro.fina_indicator",
                    symbol=self.symbol,
                    records=records,
                    period_keys=("end_date", "ann_date", "period"),
                )
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                f"Unsupported TuShare capability: {capability}",
            )
        except Exception as exc:
            return _connector_error(
                self.provider_name,
                self.provider_type,
                capability,
                f"TuShare sync failed: {exc}",
            )


def _preview_market_evidence(
    *,
    provider_name: str,
    provider_type: str,
    path: str,
    capability: str,
) -> ConnectorResult:
    source = Path(path)
    headers, rows = read_tabular_rows(source)
    required = _required_columns(capability)
    missing = sorted(required - {item.strip() for item in headers if item.strip()})
    result = ConnectorResult(
        provider_name=provider_name,
        provider_type=provider_type,
        capability=capability,
        source=str(source),
        row_count=len(rows),
        missing_columns=missing,
    )
    if missing:
        result.skipped = len(rows)
        result.errors.append(f"missing required columns: {', '.join(missing)}")
        return result

    for index, row in enumerate(rows, start=2):
        try:
            item = _row_to_evidence(row, capability, provider_name)
            result.items.append(item)
            result.market_records.append(
                _row_to_market_record(
                    row=row,
                    capability=capability,
                    provider_name=provider_name,
                    provider_type=provider_type,
                    source=str(source),
                )
            )
            result.imported += 1
        except Exception as exc:
            result.skipped += 1
            result.errors.append(f"row {index}: {exc}")
    return result


def _required_columns(capability: str) -> set[str]:
    if capability == "price_daily":
        return {"symbol", "date", "close"}
    if capability == "price_5min":
        return {"symbol", "datetime", "close"}
    if capability == "volume":
        return {"symbol", "date", "volume"}
    if capability == "financial_metrics":
        return {"symbol", "period", "metric", "value"}
    raise ValueError(f"Unsupported connector capability: {capability}")


def _row_to_evidence(
    row: dict[str, Any],
    capability: str,
    provider_name: str,
) -> dict[str, Any]:
    symbol = _text(row, "symbol").upper()
    if not symbol:
        raise ValueError("symbol is required")
    if capability == "price_daily":
        date = _text(row, "date")
        close = _number(row, "close")
        change_pct = _text(row, "change_pct")
        return {
            "symbol": symbol,
            "evidence_type": "price_condition",
            "title": f"{date} close price",
            "content": f"close={close}" + (f", change_pct={change_pct}" if change_pct else ""),
            "source": provider_name,
            "source_date": date,
        }
    if capability == "price_5min":
        timestamp = _text(row, "datetime")
        close = _number(row, "close")
        volume = _text(row, "volume")
        return {
            "symbol": symbol,
            "evidence_type": "price_condition",
            "title": f"{timestamp} 5min K",
            "content": f"close={close}" + (f", volume={volume}" if volume else ""),
            "source": provider_name,
            "source_date": timestamp[:10],
        }
    if capability == "volume":
        date = _text(row, "date")
        volume = _number(row, "volume")
        return {
            "symbol": symbol,
            "evidence_type": "volume_signal",
            "title": f"{date} volume",
            "content": f"volume={volume}",
            "source": provider_name,
            "source_date": date,
        }
    if capability == "financial_metrics":
        period = _text(row, "period")
        metric = _text(row, "metric")
        value = _text(row, "value")
        if not metric:
            raise ValueError("metric is required")
        return {
            "symbol": symbol,
            "evidence_type": "financial_result",
            "title": f"{period} {metric}",
            "content": f"{metric}={value}",
            "source": provider_name,
            "source_date": period,
        }
    raise ValueError(f"Unsupported connector capability: {capability}")


def _row_to_market_record(
    *,
    row: dict[str, Any],
    capability: str,
    provider_name: str,
    provider_type: str,
    source: str,
) -> dict[str, Any]:
    symbol = _text(row, "symbol").upper()
    if not symbol:
        raise ValueError("symbol is required")
    if capability == "price_daily":
        date = _text(row, "date")
        return _market_record(
            provider_name=provider_name,
            provider_type=provider_type,
            source=source,
            data_type=capability,
            symbol=symbol,
            timestamp=date,
            fields={
                "close": _number(row, "close"),
                "change_pct": _optional_text(row, "change_pct"),
                "volume": _optional_number(row, "volume"),
            },
        )
    if capability == "price_5min":
        timestamp = _text(row, "datetime")
        return _market_record(
            provider_name=provider_name,
            provider_type=provider_type,
            source=source,
            data_type=capability,
            symbol=symbol,
            timestamp=timestamp,
            fields={
                "close": _number(row, "close"),
                "volume": _optional_number(row, "volume"),
            },
        )
    if capability == "volume":
        date = _text(row, "date")
        return _market_record(
            provider_name=provider_name,
            provider_type=provider_type,
            source=source,
            data_type=capability,
            symbol=symbol,
            timestamp=date,
            fields={"volume": _number(row, "volume")},
        )
    if capability == "financial_metrics":
        period = _text(row, "period")
        metric = _text(row, "metric")
        return _market_record(
            provider_name=provider_name,
            provider_type=provider_type,
            source=source,
            data_type=capability,
            symbol=symbol,
            timestamp=period,
            metric=metric,
            fields={"metric": metric, "value": _text(row, "value")},
        )
    raise ValueError(f"Unsupported connector capability: {capability}")


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


def _optional_text(row: dict[str, Any], key: str) -> str:
    return _text(row, key) if key in row and row.get(key) not in (None, "") else ""


def _optional_number(row: dict[str, Any], key: str) -> float | None:
    if key not in row or row.get(key) in (None, ""):
        return None
    return _number(row, key)


def _connector_error(
    provider_name: str,
    provider_type: str,
    capability: str,
    message: str,
) -> ConnectorResult:
    return ConnectorResult(
        provider_name=provider_name,
        provider_type=provider_type,
        capability=capability,
        source=provider_type,
        errors=[message],
    )


def _frame_records(frame: Any) -> list[dict[str, Any]]:
    if frame is None:
        return []
    if isinstance(frame, list):
        return [dict(item) for item in frame if isinstance(item, dict)]
    if isinstance(frame, tuple):
        return [dict(item) for item in frame if isinstance(item, dict)]
    if hasattr(frame, "to_dict"):
        records = frame.to_dict("records")
        return [dict(item) for item in records]
    return []


def _market_records_to_result(
    *,
    provider_name: str,
    provider_type: str,
    capability: str,
    source: str,
    records: list[dict[str, Any]],
    date_key: str,
    close_key: str,
    volume_key: str = "volume",
    change_key: str = "",
    symbol: str = "",
) -> ConnectorResult:
    result = ConnectorResult(
        provider_name=provider_name,
        provider_type=provider_type,
        capability=capability,
        source=source,
        row_count=len(records),
    )
    if not records:
        result.errors.append("No rows returned by provider.")
        return result
    for index, row in enumerate(records, start=1):
        row_symbol = _normalize_symbol(str(row.get("symbol") or row.get("ts_code") or symbol))
        if not row_symbol and symbol:
            row_symbol = symbol
        try:
            if capability == "price_daily":
                date = _text_any(row, date_key)
                close = _number_any(row, close_key)
                change_pct = _text_any(row, change_key) if change_key else ""
                volume = _optional_number_any(row, volume_key)
                result.items.append(
                    {
                        "symbol": row_symbol,
                        "evidence_type": "price_condition",
                        "title": f"{date} 日K收盘价",
                        "content": f"close={close}"
                        + (f", change_pct={change_pct}" if change_pct else ""),
                        "source": provider_name,
                        "source_date": _source_date(date),
                    }
                )
                result.market_records.append(
                    _market_record(
                        provider_name=provider_name,
                        provider_type=provider_type,
                        source=source,
                        data_type=capability,
                        symbol=row_symbol,
                        timestamp=_source_date(date),
                        fields={
                            "close": close,
                            "change_pct": change_pct,
                            "volume": volume,
                        },
                    )
                )
            elif capability == "price_5min":
                timestamp = _text_any(row, date_key)
                close = _number_any(row, close_key)
                volume = _text_any(row, volume_key)
                result.items.append(
                    {
                        "symbol": row_symbol,
                        "evidence_type": "price_condition",
                        "title": f"{timestamp} 5分钟K线",
                        "content": f"close={close}"
                        + (f", volume={volume}" if volume else ""),
                        "source": provider_name,
                        "source_date": _source_date(timestamp),
                    }
                )
                result.market_records.append(
                    _market_record(
                        provider_name=provider_name,
                        provider_type=provider_type,
                        source=source,
                        data_type=capability,
                        symbol=row_symbol,
                        timestamp=timestamp,
                        fields={
                            "close": close,
                            "volume": _number_or_text(volume),
                        },
                    )
                )
            elif capability == "volume":
                date = _text_any(row, date_key)
                volume = _number_any(row, volume_key)
                result.items.append(
                    {
                        "symbol": row_symbol,
                        "evidence_type": "volume_signal",
                        "title": f"{date} 成交量",
                        "content": f"volume={volume}",
                        "source": provider_name,
                        "source_date": _source_date(date),
                    }
                )
                result.market_records.append(
                    _market_record(
                        provider_name=provider_name,
                        provider_type=provider_type,
                        source=source,
                        data_type=capability,
                        symbol=row_symbol,
                        timestamp=_source_date(date),
                        fields={"volume": volume},
                    )
                )
        except Exception as exc:
            result.skipped += 1
            result.errors.append(f"row {index}: {exc}")
    result.imported = len(result.items)
    return result


def _financial_records_to_result(
    *,
    provider_name: str,
    provider_type: str,
    source: str,
    symbol: str,
    records: list[dict[str, Any]],
    period_keys: tuple[str, ...],
) -> ConnectorResult:
    result = ConnectorResult(
        provider_name=provider_name,
        provider_type=provider_type,
        capability="financial_metrics",
        source=source,
        row_count=len(records),
    )
    if not records:
        result.errors.append("No rows returned by provider.")
        return result
    latest = records[0]
    period = next((_text_any(latest, key) for key in period_keys if _text_any(latest, key)), "")
    ignored = {key.lower() for key in period_keys} | {"symbol", "ts_code", "股票代码"}
    for key, value in latest.items():
        if key.lower() in ignored or value in (None, ""):
            continue
        result.items.append(
            {
                "symbol": symbol,
                "evidence_type": "financial_result",
                "title": f"{period} {key}",
                "content": f"{key}={value}",
                "source": provider_name,
                "source_date": _source_date(period),
            }
        )
        result.market_records.append(
            _market_record(
                provider_name=provider_name,
                provider_type=provider_type,
                source=source,
                data_type="financial_metrics",
                symbol=symbol,
                timestamp=_source_date(period),
                metric=str(key),
                fields={"metric": str(key), "value": value},
            )
        )
    result.imported = len(result.items)
    if not result.items:
        result.errors.append("No financial metric fields were found in provider response.")
    return result


def _normalize_symbol(value: str) -> str:
    clean = value.strip().upper()
    if "." in clean:
        clean = clean.split(".", 1)[0]
    return clean


def _to_tushare_code(symbol: str) -> str:
    raw = str(symbol or "").strip().upper()
    if raw.endswith((".SH", ".SZ", ".BJ")):
        return raw
    clean = _normalize_symbol(raw)
    if clean.startswith("6"):
        return f"{clean}.SH"
    if clean.startswith(("0", "3")):
        return f"{clean}.SZ"
    if clean.startswith(("4", "8", "9")):
        return f"{clean}.BJ"
    return clean


def _date_compact(value: Any) -> str:
    text = str(value or "").strip()
    return text.replace("-", "")[:8]


def _today_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _tushare_date_kwargs(config: dict[str, Any]) -> dict[str, str]:
    kwargs = {}
    start = _date_compact(config.get("start_date"))
    end = _date_compact(config.get("end_date"))
    if start:
        kwargs["start_date"] = start
    if end:
        kwargs["end_date"] = end
    return kwargs


def _tushare_datetime_kwargs(config: dict[str, Any]) -> dict[str, str]:
    kwargs = {}
    if config.get("start_date"):
        kwargs["start_date"] = str(config["start_date"])
    if config.get("end_date"):
        kwargs["end_date"] = str(config["end_date"])
    return kwargs


def _text_any(row: dict[str, Any], key: str, default: str = "") -> str:
    if not key:
        return default
    value = row.get(key, default)
    if value is None:
        return default
    return str(value).strip()


def _number_any(row: dict[str, Any], key: str) -> float:
    value = row.get(key, 0)
    if value in (None, ""):
        return 0.0
    return float(value)


def _optional_number_any(row: dict[str, Any], key: str) -> float | None:
    if not key or key not in row or row.get(key) in (None, ""):
        return None
    return _number_any(row, key)


def _number_or_text(value: Any) -> float | str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        return float(text)
    except ValueError:
        return text


def _source_date(value: str) -> str:
    text = str(value or "").strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    if len(text) >= 8 and text[:8].isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return text[:10]


def _market_record(
    *,
    provider_name: str,
    provider_type: str,
    source: str,
    data_type: str,
    symbol: str,
    timestamp: str,
    fields: dict[str, Any],
    metric: str = "",
) -> dict[str, Any]:
    return {
        "provider_name": provider_name,
        "provider_type": provider_type,
        "source": source,
        "data_type": data_type,
        "symbol": str(symbol or "").strip().upper(),
        "timestamp": str(timestamp or "").strip(),
        "metric": str(metric or "").strip(),
        "fields": {key: value for key, value in fields.items() if value not in (None, "")},
    }
