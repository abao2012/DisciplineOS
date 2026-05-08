from disciplineos.services import DisciplineService, seed_demo_data


def test_monthly_review_snapshot_persists(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    month = service.store.read("decisions.json", [])[0]["created_at"][:7]

    snapshot = service.save_review_snapshot(month)
    snapshots = service.list_review_snapshots(month=month)
    legacy = service.store.read("reviews.json", [])

    assert snapshot["period"] == month
    assert snapshot["review"]["month"] == month
    assert snapshot["decision_count"] == 1
    assert snapshot["discipline_score"] == snapshot["review"]["discipline_score"]
    assert snapshots[0]["id"] == snapshot["id"]
    assert snapshots[0]["status_summary"] == snapshot["status_summary"]
    assert legacy[0]["id"] == snapshot["id"]


def test_monthly_review_snapshot_freezes_audit_drilldown(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    evidence = service.save_evidence_dict(
        {
            "symbol": "SAMPLE",
            "evidence_type": "user_note",
            "title": "Thesis checkpoint",
            "content": "New evidence confirms the thesis.",
            "source": "manual",
            "source_date": "2026-05-01",
        }
    )
    service.check_decision_payload(
        {
            "symbol": "SAMPLE",
            "action": "add",
            "amount": 100,
            "reason": "New evidence confirms the thesis.",
            "evidence": [],
            "evidence_item_ids": [evidence["id"]],
            "emotion": "calm",
            "auto_position": True,
        }
    )
    month = service.store.read("decisions.json", [])[0]["created_at"][:7]

    snapshot = service.save_review_snapshot(month)
    drilldown = snapshot["review"]["drilldown"]

    assert drilldown["counts"]["decisions"] == 2
    assert drilldown["counts"]["audits"] == 2
    assert drilldown["counts"]["rule_results"] >= 2
    assert drilldown["counts"]["violations"] >= 1
    assert drilldown["evidence_items"][0]["id"] == evidence["id"]
    assert any(
        evidence["id"] in decision.get("referenced_evidence_ids", [])
        for decision in drilldown["decisions"]
    )


def test_review_snapshot_exports_markdown_report(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    month = service.store.read("decisions.json", [])[0]["created_at"][:7]
    snapshot = service.save_review_snapshot(month)

    report = service.export_review_snapshot(snapshot["id"])
    content = tmp_path.joinpath("reports").joinpath(
        f"review-{month}-{snapshot['id'][:8]}.md"
    ).read_text(encoding="utf-8")

    assert report["format"] == "markdown"
    assert report["bytes"] > 0
    assert "# DisciplineOS Monthly Review" in content
    assert "## Decision Drill-down" in content
    assert "#### Rule Results" in content
    assert "SAMPLE add" in content


def test_review_report_index_lists_exported_reports(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    month = service.store.read("decisions.json", [])[0]["created_at"][:7]
    snapshot = service.save_review_snapshot(month)
    report = service.export_review_snapshot(snapshot["id"])

    reports = service.list_review_reports()

    assert reports[0]["path"] == report["path"]
    assert reports[0]["snapshot_id"] == snapshot["id"]
    assert reports[0]["period"] == month
    assert reports[0]["bytes"] == report["bytes"]
    assert reports[0]["title"] == f"DisciplineOS Monthly Review {month}"


def test_review_snapshot_comparison_reports_deltas(tmp_path) -> None:
    service = DisciplineService(tmp_path)
    seed_demo_data(service)
    month = service.store.read("decisions.json", [])[0]["created_at"][:7]
    first = service.save_review_snapshot(month)
    evidence = service.save_evidence_dict(
        {
            "symbol": "SAMPLE",
            "evidence_type": "user_note",
            "title": "Fresh thesis evidence",
            "content": "New evidence confirms the thesis.",
        }
    )
    service.check_decision_payload(
        {
            "symbol": "SAMPLE",
            "action": "add",
            "amount": 100,
            "reason": "New evidence confirms the thesis.",
            "evidence_item_ids": [evidence["id"]],
            "emotion": "calm",
            "auto_position": True,
        }
    )
    second = service.save_review_snapshot(month)

    comparison = service.compare_review_snapshots(first["id"], second["id"])

    assert comparison["left"]["id"] == first["id"]
    assert comparison["right"]["id"] == second["id"]
    assert comparison["delta"]["decision_count"] == 1
    assert comparison["interpretation"] in {"improving", "deteriorating", "mixed"}
    assert any(item["symbol"] == "SAMPLE" for item in comparison["repeated_symbols"])
