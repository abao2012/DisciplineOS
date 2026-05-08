from disciplineos.copilot import COMPLIANCE_NOTICE, build_copilot_summary
from disciplineos.services import DisciplineService


def test_copilot_summary_keeps_compliance_boundary() -> None:
    dashboard = {
        "cards": {
            "AAA": {
                "symbol": "AAA",
                "thesis": ["Original thesis"],
            }
        },
        "violations": [
            {
                "symbol": "AAA",
                "type": "Thesis Drift",
                "status": "open",
            }
        ],
        "review": {
            "discipline_score": 70,
            "pass_rate": 50,
            "violation_types": {"Thesis Drift": 1},
            "attribution": {},
            "rule_revision_suggestions": [{"scope": "card:AAA"}],
        },
    }

    summary = build_copilot_summary(dashboard)

    assert summary["notice"] == COMPLIANCE_NOTICE
    assert "not investment advice" in summary["notice"]
    assert summary["thesis_drift_alerts"][0]["symbol"] == "AAA"
    assert "buy" not in summary["next_actions"][0].lower()


def test_service_dashboard_includes_copilot(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    dashboard = service.dashboard("2026-04")

    assert "copilot" in dashboard
    assert "monthly_review_draft" in dashboard["copilot"]

