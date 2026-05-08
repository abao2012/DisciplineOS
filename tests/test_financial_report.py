from pathlib import Path

from disciplineos.financial_report import summarize_financial_report, summarize_financial_report_text
from disciplineos.services import DisciplineService


REPORT_TEXT = """
Revenue increased 18% year over year to 12.4 billion.
Net profit increased 9% year over year to 1.8 billion.
Gross margin improved to 42.5%.
Operating cash flow was 2.1 billion.
Management guidance: full-year revenue growth is expected to remain double digit.
"""


def test_summarize_financial_report_text_extracts_metrics() -> None:
    summary = summarize_financial_report_text(
        text=REPORT_TEXT,
        symbol="sample",
        period="2026Q1",
    )

    assert summary.symbol == "SAMPLE"
    assert "Revenue increased" in summary.revenue
    assert "Net profit" in summary.profit
    assert "Gross margin" in summary.gross_margin
    assert len(summary.evidence_summary) >= 4


def test_summarize_financial_report_file(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    report_path.write_text(REPORT_TEXT, encoding="utf-8")

    summary = summarize_financial_report(report_path, "SAMPLE", "2026Q1")

    assert summary.source == str(report_path)
    assert "guidance" in summary.guidance.lower()


def test_service_saves_financial_report_summary(tmp_path: Path) -> None:
    service = DisciplineService(tmp_path)

    result = service.summarize_financial_report_text(
        {"symbol": "SAMPLE", "period": "2026Q1", "text": REPORT_TEXT}
    )

    assert result["symbol"] == "SAMPLE"
    assert result["analysis_mode"] == "local_rules"
    assert result["key_insights"]
    assert service.list_financial_reports()[0]["period"] == "2026Q1"


def test_service_uses_ai_information_analysis_when_enabled(tmp_path: Path, monkeypatch) -> None:
    service = DisciplineService(tmp_path)
    service.save_settings(
        {
            "storage_mode": "sqlite",
            "ai_enabled": True,
            "strict_mode": True,
            "ai_api_token": "token",
            "ai_api_base_url": "https://api.example.test/v1",
            "ai_model": "test-model",
        }
    )

    def fake_analyze_information_with_ai(**kwargs):
        assert kwargs["symbol"] == "SAMPLE"
        return {
            "key_insights": ["Profit quality improved."],
            "positive_factors": ["Revenue and profit grew together."],
            "negative_factors": [],
            "risk_flags": ["Watch cash conversion."],
            "discipline_suggestions": ["Raise limit only after cash flow confirms."],
            "card_suggestions": {
                "raise_position": ["Cash flow and profit quality both improve."],
                "lower_position": ["Cash flow diverges from profit."],
            },
            "evidence_summary": ["AI extracted evidence."],
        }

    monkeypatch.setattr(
        "disciplineos.services.analyze_information_with_ai",
        fake_analyze_information_with_ai,
    )

    result = service.summarize_financial_report_text(
        {"symbol": "SAMPLE", "period": "2026Q1", "text": REPORT_TEXT}
    )

    assert result["analysis_mode"] == "ai"
    assert result["ai_status"] == "pass"
    assert result["key_insights"] == ["Profit quality improved."]
    assert result["card_suggestions"]["raise_position"] == [
        "Cash flow and profit quality both improve."
    ]
    assert service.list_ai_runs()[0]["agent_type"] == "info_analysis"


def test_service_falls_back_to_local_rules_when_ai_config_missing(tmp_path: Path) -> None:
    service = DisciplineService(tmp_path)
    service.save_settings(
        {"storage_mode": "sqlite", "ai_enabled": True, "strict_mode": True}
    )

    result = service.summarize_financial_report_text(
        {"symbol": "SAMPLE", "period": "2026Q1", "text": REPORT_TEXT}
    )

    assert result["analysis_mode"] == "local_rules"
    assert result["ai_status"] == "failed"
    assert "Token" in result["ai_error"]
