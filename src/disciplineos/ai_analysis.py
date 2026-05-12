from __future__ import annotations

import json
import time
from typing import Any
from urllib import error, request


INFO_ANALYSIS_SCHEMA = {
    "key_insights": [],
    "positive_factors": [],
    "negative_factors": [],
    "risk_flags": [],
    "discipline_suggestions": [],
    "card_suggestions": {
        "why_buy": [],
        "no_buy": [],
        "add_when": [],
        "reduce_when": [],
        "raise_position": [],
        "lower_position": [],
        "invalid_when": [],
        "forbidden_behaviors": [],
    },
    "evidence_summary": [],
}


def analyze_information_with_ai(
    *,
    text: str,
    symbol: str,
    period: str,
    material_type: str,
    ai_online_search: bool,
    settings: dict[str, Any],
) -> dict[str, Any]:
    token = str(settings.get("ai_api_token", "")).strip()
    base_url = str(settings.get("ai_api_base_url", "")).strip().rstrip("/")
    model = str(settings.get("ai_model", "")).strip() or "gpt-5.5"
    max_retries = _non_negative_int(settings.get("ai_max_retries", 1))
    if not token:
        raise ValueError("AI Token is empty. Please configure it in Settings first.")
    if not base_url:
        raise ValueError("AI API Base URL is empty. Please configure it in Settings first.")

    endpoint = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are DisciplineOS information analyst. Extract evidence and "
                    "discipline-rule implications from financial reports, research, "
                    "announcements, news, and market events. Do not provide direct "
                    "buy/sell/hold recommendations or target prices. Return JSON only."
                ),
            },
            {
                "role": "user",
                "content": _build_prompt(
                    text=text,
                    symbol=symbol,
                    period=period,
                    material_type=material_type,
                    ai_online_search=ai_online_search,
                ),
            },
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    response = _post_json(endpoint, token, payload, max_retries=max_retries)
    content = _extract_content(response)
    parsed = _parse_json_content(content)
    normalized = _normalize_ai_payload(parsed)
    normalized["_ai_usage"] = _normalize_usage(response.get("usage") or {})
    normalized["_ai_model"] = model
    return normalized


def _build_prompt(
    *,
    text: str,
    symbol: str,
    period: str,
    material_type: str,
    ai_online_search: bool,
) -> str:
    online_note = (
        "The user requested online search. If your runtime has browsing/search tools, "
        "use them to supplement the material; otherwise state that only the supplied "
        "material was analyzed."
        if ai_online_search
        else "Analyze only the supplied material."
    )
    schema = json.dumps(INFO_ANALYSIS_SCHEMA, ensure_ascii=False, indent=2)
    clipped = text[:16000]
    return (
        f"Symbol: {symbol}\n"
        f"Period/Event date: {period}\n"
        f"Material type: {material_type}\n"
        f"{online_note}\n\n"
        "Return JSON in this exact shape. Keep each list item concise and evidence-based:\n"
        f"{schema}\n\n"
        "Rules:\n"
        "- discipline_suggestions should describe how to update evidence gates, position "
        "limits, reduce conditions, or invalidation rules.\n"
        "- card_suggestions must be usable as DisciplineOS card clauses.\n"
        "- Avoid direct investment advice, target prices, or certainty claims.\n\n"
        "Material:\n"
        f"{clipped}"
    )


def _post_json(
    endpoint: str,
    token: str,
    payload: dict[str, Any],
    *,
    max_retries: int = 1,
) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    attempts = max(1, max_retries + 1)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"AI API request failed: HTTP {exc.code} {body}")
            if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise last_error from exc
        except error.URLError as exc:
            last_error = RuntimeError(f"AI API request failed: {exc.reason}")
        if attempt < attempts:
            time.sleep(min(0.2 * attempt, 1.0))
    if last_error:
        raise last_error
    raise RuntimeError("AI API request failed.")


def _extract_content(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        raise RuntimeError("AI API response has no choices.")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
            else:
                parts.append(str(item))
        content = "\n".join(parts)
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("AI API response has empty content.")
    return content.strip()


def _parse_json_content(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI API response was not valid JSON.") from exc
    if not isinstance(value, dict):
        raise RuntimeError("AI API response JSON must be an object.")
    return value


def _normalize_ai_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(INFO_ANALYSIS_SCHEMA)
    normalized.update(payload)
    normalized["card_suggestions"] = {
        **INFO_ANALYSIS_SCHEMA["card_suggestions"],
        **(payload.get("card_suggestions") or {}),
    }
    return normalized


def _normalize_usage(usage: dict[str, Any]) -> dict[str, int]:
    return {
        "prompt_tokens": _non_negative_int(
            usage.get("prompt_tokens") or usage.get("input_tokens")
        ),
        "completion_tokens": _non_negative_int(
            usage.get("completion_tokens") or usage.get("output_tokens")
        ),
        "total_tokens": _non_negative_int(usage.get("total_tokens")),
    }


def _non_negative_int(value: object) -> int:
    try:
        return max(0, int(float(value or 0)))
    except (TypeError, ValueError):
        return 0
