from __future__ import annotations

import hashlib
import json
import re
from typing import Any


PROHIBITED_PATTERNS = [
    r"\brecommend\s+(buy|sell|hold)\b",
    r"\b(strong\s+)?buy\s+recommendation\b",
    r"\b(strong\s+)?sell\s+recommendation\b",
    r"\btarget\s+price\b",
    r"\bprice\s+target\b",
    r"\bguaranteed\s+return\b",
    r"\bwill\s+(rise|fall|double|surge|crash)\b",
    r"建议\s*(买入|卖出|持有)",
    r"(买入|卖出|持有)\s*建议",
    r"目标价",
    r"保证收益",
    r"必然上涨",
    r"一定上涨",
    r"会涨",
    r"会跌",
]

REDACTION = "[removed: investment advice outside DisciplineOS scope]"


def input_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sanitize_ai_output(payload: Any) -> tuple[Any, str]:
    """Return sanitized payload and compliance status."""

    status = "pass"
    if isinstance(payload, str):
        sanitized, changed = _sanitize_text(payload)
        return sanitized, "redacted" if changed else status
    if isinstance(payload, list):
        values = []
        for item in payload:
            sanitized, item_status = sanitize_ai_output(item)
            values.append(sanitized)
            if item_status != "pass":
                status = item_status
        return values, status
    if isinstance(payload, dict):
        values = {}
        for key, value in payload.items():
            sanitized, item_status = sanitize_ai_output(value)
            values[key] = sanitized
            if item_status != "pass":
                status = item_status
        return values, status
    return payload, status


def has_prohibited_advice(text: str) -> bool:
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in PROHIBITED_PATTERNS
    )


def _sanitize_text(text: str) -> tuple[str, bool]:
    sanitized = text
    changed = False
    for pattern in PROHIBITED_PATTERNS:
        sanitized, count = re.subn(
            pattern,
            REDACTION,
            sanitized,
            flags=re.IGNORECASE,
        )
        changed = changed or count > 0
    return sanitized, changed
