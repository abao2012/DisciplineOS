from disciplineos.models import Action, Decision, DisciplineCard, Emotion, InvestorProfile
from disciplineos.rules import build_rule_results
from disciplineos.services import DisciplineService


def test_build_rule_results_records_pass_and_required_statuses() -> None:
    profile = InvestorProfile(name="tester", style="value", max_single_position_pct=15)
    card = DisciplineCard(
        symbol="AAA",
        name="AAA",
        asset_type="stock",
        sector="technology",
        thesis=["Test thesis"],
        max_position_pct=15,
    )
    decision = Decision(
        symbol="AAA",
        action=Action.BUY,
        amount=1000,
        position_before_pct=0,
        position_after_pct=5,
        reason="Initial position.",
        evidence=[],
        emotion=Emotion.CALM,
    )

    results = build_rule_results(profile, card, decision)
    by_code = {item["rule_code"]: item for item in results}

    assert by_code["position.max_single"]["status"] == "PASS"
    assert by_code["evidence.required_for_buy_or_add"]["status"] == "EVIDENCE_REQUIRED"
    assert by_code["position.max_single"]["params"]["effective_limit_pct"] == 15


def test_service_persists_rule_results_for_decision(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    service.save_profile_dict(
        {
            "name": "tester",
            "style": "value",
            "max_single_position_pct": 15,
            "max_sector_position_pct": 30,
            "max_drawdown_pct": 20,
            "allow_pre_earnings_add": False,
            "behavioral_weaknesses": [],
        }
    )
    service.save_card_dict(
        {
            "symbol": "AAA",
            "name": "AAA",
            "asset_type": "stock",
            "sector": "technology",
            "thesis": ["Test thesis"],
            "max_position_pct": 15,
        }
    )

    result = service.check_decision_payload(
        {
            "symbol": "AAA",
            "action": "buy",
            "amount": 1000,
            "position_before_pct": 0,
            "position_after_pct": 5,
            "reason": "Initial position.",
            "evidence": [],
            "emotion": "calm",
        }
    )

    persisted = service.list_rule_results(decision_id=result["decision_id"])
    assert result["status"] == "EVIDENCE_REQUIRED"
    assert result["rule_results"]
    assert len(persisted) == len(result["rule_results"])
    assert (tmp_path / "rule_results.json").exists()
