from disciplineos.models import Action, AuditStatus, Decision, DisciplineCard, Emotion, InvestorProfile
from disciplineos.rules import evaluate_decision


def make_profile() -> InvestorProfile:
    return InvestorProfile(
        name="tester",
        style="value",
        max_single_position_pct=15,
        allow_pre_earnings_add=False,
    )


def make_card() -> DisciplineCard:
    return DisciplineCard(
        symbol="SAMPLE",
        name="Sample Asset",
        asset_type="stock",
        sector="technology",
        thesis=["Test thesis"],
        max_position_pct=15,
    )


def test_blocks_position_overweight_and_emotional_add() -> None:
    decision = Decision(
        symbol="SAMPLE",
        action=Action.ADD,
        amount=10000,
        position_before_pct=10,
        position_after_pct=18,
        reason="Price has fallen and I want to reduce my average cost.",
        evidence=[],
        emotion=Emotion.ANXIOUS,
    )

    result = evaluate_decision(make_profile(), make_card(), decision)

    assert result.status == AuditStatus.BLOCKED
    assert {item.type for item in result.violations} == {
        "Position Overweight",
        "Emotional Averaging Down",
    }


def test_warns_when_evidence_missing_but_position_is_ok() -> None:
    decision = Decision(
        symbol="SAMPLE",
        action=Action.BUY,
        amount=3000,
        position_before_pct=0,
        position_after_pct=5,
        reason="Initial position",
        evidence=[],
        emotion=Emotion.CALM,
    )

    result = evaluate_decision(make_profile(), make_card(), decision)

    assert result.status == AuditStatus.EVIDENCE_REQUIRED
    assert [item.type for item in result.warnings] == ["No Evidence Trade"]


def test_passes_clear_decision_with_evidence() -> None:
    decision = Decision(
        symbol="SAMPLE",
        action=Action.BUY,
        amount=3000,
        position_before_pct=0,
        position_after_pct=5,
        reason="Initial position under discipline card.",
        evidence=["Revenue and margin trend match the card thesis."],
        emotion=Emotion.CALM,
    )

    result = evaluate_decision(make_profile(), make_card(), decision)

    assert result.status == AuditStatus.PASS


def test_detects_revenge_thesis_style_and_valuation_violations() -> None:
    decision = Decision(
        symbol="SAMPLE",
        action=Action.BUY,
        amount=3000,
        position_before_pct=0,
        position_after_pct=5,
        reason=(
            "This is overvalued and outside valuation range, but I will hold "
            "forever because it is value now."
        ),
        evidence=["Some evidence"],
        emotion=Emotion.REVENGE,
        thesis_changed=True,
    )

    result = evaluate_decision(make_profile(), make_card(), decision)
    all_types = {item.type for item in result.violations + result.warnings}

    assert "Revenge Trade" in all_types
    assert "Thesis Drift" in all_types
    assert "Style Drift" in all_types
    assert "Valuation Violation" in all_types
    assert all((item.remediation and item.category) for item in result.violations + result.warnings)


def test_card_rules_parameterize_position_limit() -> None:
    card = make_card()
    card.max_position_pct = 30
    card.card_rules = [
        {
            "rule_code": "position.max_single",
            "enabled": True,
            "severity": "HARD_BLOCK",
            "params": {"max_position_pct": 12},
        }
    ]
    decision = Decision(
        symbol="SAMPLE",
        action=Action.BUY,
        amount=3000,
        position_before_pct=0,
        position_after_pct=13,
        reason="Initial position with evidence.",
        evidence=["New evidence"],
        emotion=Emotion.CALM,
    )

    result = evaluate_decision(make_profile(), card, decision)

    assert result.status == AuditStatus.BLOCKED
    assert result.violations[0].rule_id == "position.max_single"


def test_review_required_is_distinct_status() -> None:
    decision = Decision(
        symbol="SAMPLE",
        action=Action.REDUCE,
        amount=3000,
        position_before_pct=10,
        position_after_pct=8,
        reason="Reduce after thesis changed.",
        evidence=["Updated evidence"],
        emotion=Emotion.CALM,
        thesis_changed=True,
    )

    result = evaluate_decision(make_profile(), make_card(), decision)

    assert result.status == AuditStatus.REVIEW_REQUIRED
    assert {item.rule_id for item in result.warnings} >= {
        "thesis.review_required",
        "review.after_material_action",
    }
