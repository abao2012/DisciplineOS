from disciplineos.services import DisciplineService


def _seed_profile_and_card(service: DisciplineService) -> None:
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


def test_manual_evidence_persists_in_evidence_pool(tmp_path) -> None:
    service = DisciplineService(tmp_path)

    item = service.save_evidence_dict(
        {
            "symbol": "aaa",
            "evidence_type": "financial_result",
            "title": "Q1 profit",
            "content": "Profit improved and cash flow stayed positive.",
            "source": "manual",
            "source_date": "2026Q1",
        }
    )

    assert item["symbol"] == "AAA"
    assert service.list_evidence("AAA")[0]["title"] == "Q1 profit"


def test_evidence_can_be_filtered_by_symbol_and_type(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    service.save_evidence_dict(
        {
            "symbol": "AAA",
            "evidence_type": "financial_result",
            "title": "Q1 profit",
            "content": "Profit improved.",
        }
    )
    service.save_evidence_dict(
        {
            "symbol": "AAA",
            "evidence_type": "user_note",
            "title": "Meeting note",
            "content": "Management tone stayed disciplined.",
        }
    )

    filtered = service.list_evidence("AAA", evidence_type="financial_result")

    assert len(filtered) == 1
    assert filtered[0]["title"] == "Q1 profit"


def test_financial_report_summary_creates_evidence_items(tmp_path) -> None:
    service = DisciplineService(tmp_path)

    summary = service.summarize_financial_report_text(
        {
            "symbol": "AAA",
            "period": "2026Q1",
            "text": "Revenue increased 10%. Net profit increased 8%. Cash flow positive.",
        }
    )

    evidence = service.list_evidence("AAA")
    assert summary["evidence_summary"]
    assert evidence
    assert evidence[0]["evidence_type"] == "financial_result"


def test_decision_gate_uses_existing_evidence_when_payload_has_none(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    _seed_profile_and_card(service)
    service.save_evidence_dict(
        {
            "symbol": "AAA",
            "evidence_type": "user_note",
            "title": "Channel check",
            "content": "New order visibility improved.",
        }
    )

    result = service.check_decision_dict(
        {
            "symbol": "AAA",
            "action": "add",
            "amount": 100,
            "position_before_pct": 10,
            "position_after_pct": 12,
            "reason": "Add after updated evidence.",
            "emotion": "calm",
        }
    )

    decision = service.store.read("decisions.json", [])[0]
    violation_types = [item.type for item in result.violations]
    assert "No Evidence Trade" not in violation_types
    assert decision["evidence"]


def test_decision_gate_returns_referenced_evidence_items(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    _seed_profile_and_card(service)
    evidence = service.save_evidence_dict(
        {
            "symbol": "AAA",
            "evidence_type": "user_note",
            "title": "Channel check",
            "content": "New order visibility improved.",
        }
    )

    result = service.check_decision_payload(
        {
            "symbol": "AAA",
            "action": "add",
            "amount": 100,
            "position_before_pct": 10,
            "position_after_pct": 12,
            "reason": "Add after updated evidence.",
            "emotion": "calm",
        }
    )

    decision = service.store.read("decisions.json", [])[0]
    assert result["referenced_evidence_items"][0]["id"] == evidence["id"]
    assert decision["referenced_evidence_ids"] == [evidence["id"]]


def test_decision_gate_uses_explicit_evidence_item_ids(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    _seed_profile_and_card(service)
    selected = service.save_evidence_dict(
        {
            "symbol": "AAA",
            "evidence_type": "financial_result",
            "title": "Selected evidence",
            "content": "Profit improved.",
        }
    )
    service.save_evidence_dict(
        {
            "symbol": "AAA",
            "evidence_type": "user_note",
            "title": "Unselected evidence",
            "content": "This should not be referenced.",
        }
    )

    result = service.check_decision_payload(
        {
            "symbol": "AAA",
            "action": "add",
            "amount": 100,
            "position_before_pct": 10,
            "position_after_pct": 12,
            "reason": "Add after selected evidence.",
            "emotion": "calm",
            "evidence_item_ids": [selected["id"]],
        }
    )

    assert [item["id"] for item in result["referenced_evidence_items"]] == [
        selected["id"]
    ]
    assert result["status"] == "REVIEW_REQUIRED"
