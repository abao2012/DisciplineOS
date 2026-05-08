from disciplineos.ai_guardrails import REDACTION, sanitize_ai_output
from disciplineos.services import DisciplineService


def test_ai_guardrails_redact_investment_advice() -> None:
    payload = {
        "draft": "This is a buy recommendation with target price 100.",
        "safe": "This decision lacks evidence.",
    }

    sanitized, status = sanitize_ai_output(payload)

    assert status == "redacted"
    assert REDACTION in sanitized["draft"]
    assert "target price" not in sanitized["draft"].lower()
    assert sanitized["safe"] == "This decision lacks evidence."


def test_copilot_does_not_create_ai_run_when_ai_disabled(tmp_path) -> None:
    service = DisciplineService(tmp_path)

    dashboard = service.dashboard("2026-05")

    assert dashboard["copilot"]["ai_enabled"] is False
    assert dashboard["copilot"]["final_status_source"] == "rule_engine"
    assert service.list_ai_runs() == []


def test_copilot_audits_output_when_ai_enabled(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    service.save_settings(
        {"storage_mode": "sqlite", "ai_enabled": True, "strict_mode": True}
    )

    dashboard = service.dashboard("2026-05")
    runs = service.list_ai_runs()

    assert dashboard["copilot"]["ai_enabled"] is True
    assert runs
    assert runs[0]["agent_type"] == "copilot"
    assert runs[0]["compliance_status"] == "pass"
