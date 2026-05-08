from disciplineos.card_generator import generate_card_from_answers, list_card_templates
from disciplineos.services import DisciplineService


def test_card_templates_include_whitepaper_asset_styles() -> None:
    templates = list_card_templates()

    assert {"value", "growth", "cyclical", "trend", "etf"} <= set(templates)
    assert templates["etf"]["asset_type"] == "ETF"
    assert templates["growth"]["thesis_options"]


def test_generate_card_from_six_question_answers() -> None:
    card = generate_card_from_answers(
        {
            "template": "growth",
            "symbol": "abc",
            "name": "ABC Corp",
            "sector": "AI",
            "max_position_pct": 12,
            "why_buy": ["Revenue growth is accelerating."],
            "no_buy": ["Valuation is too hot."],
            "add_when": ["New order evidence appears."],
            "reduce_when": ["Growth slows."],
            "raise_position": ["Revenue and profit quality both improve."],
            "lower_position": ["Margin evidence weakens."],
            "invalid_when": ["Guidance is cut."],
            "forbidden_behaviors": ["Do not chase FOMO."],
        }
    )

    assert card.symbol == "ABC"
    assert card.asset_type == "stock"
    assert card.thesis == ["Revenue growth is accelerating."]
    assert card.add_conditions == ["New order evidence appears."]
    assert card.raise_position_conditions == [
        "Revenue and profit quality both improve."
    ]
    assert card.lower_position_conditions == ["Margin evidence weakens."]
    assert any(rule["rule_code"] == "position.max_single" for rule in card.card_rules)


def test_service_generate_card_persists_card(tmp_path) -> None:
    service = DisciplineService(tmp_path)

    card = service.generate_card(
        {
            "template": "etf",
            "symbol": "ETF1",
            "name": "ETF One",
            "why_buy": ["Allocation plan."],
        }
    )

    assert card.asset_type == "ETF"
    assert "ETF1" in service.list_cards()
