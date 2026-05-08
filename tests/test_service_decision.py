from disciplineos.services import DisciplineService


def test_service_auto_calculates_decision_position_percent(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    service.save_profile_dict(
        {
            "name": "tester",
            "style": "value",
            "max_single_position_pct": 30,
            "max_sector_position_pct": 40,
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
            "max_position_pct": 30,
        }
    )
    service.save_position_dict(
        {
            "symbol": "AAA",
            "name": "AAA",
            "quantity": 10,
            "current_price": 10,
        }
    )
    service.save_position_dict(
        {
            "symbol": "BBB",
            "name": "BBB",
            "quantity": 90,
            "current_price": 10,
        }
    )

    result = service.check_decision_dict(
        {
            "symbol": "AAA",
            "action": "add",
            "amount": 100,
            "reason": "Add with new evidence.",
            "evidence": ["New evidence"],
            "emotion": "calm",
            "auto_position": True,
        }
    )

    decision = service.store.read("decisions.json", [])[0]
    assert result.status == "REVIEW_REQUIRED"
    assert decision["position_before_pct"] == 10
    assert decision["position_after_pct"] == 18.18


def test_service_records_and_resolves_violation(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    service.save_card_dict(
        {
            "symbol": "AAA",
            "name": "AAA",
            "asset_type": "stock",
            "sector": "technology",
            "thesis": ["Test thesis"],
            "max_position_pct": 10,
        }
    )

    service.check_decision_dict(
        {
            "symbol": "AAA",
            "action": "add",
            "amount": 100,
            "position_before_pct": 9,
            "position_after_pct": 20,
            "reason": "Price has fallen.",
            "evidence": [],
            "emotion": "anxious",
        }
    )

    violation = service.store.read("violations.json", [])[0]
    assert violation["status"] == "open"
    assert violation["remediation"]
    assert violation["weight"] > 0

    resolved = service.resolve_violation(violation["id"], "Reduced planned size.")
    updated = service.store.read("violations.json", [])[0]

    assert resolved is True
    assert updated["status"] == "resolved"
    assert updated["resolution_note"] == "Reduced planned size."
