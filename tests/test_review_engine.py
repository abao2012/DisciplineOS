from disciplineos.review_engine import (
    build_review_attribution,
    build_rule_revision_suggestions,
)


def test_review_attribution_groups_issues_by_bucket() -> None:
    decisions = [
        {"id": "d1", "symbol": "AAA", "action": "add"},
        {"id": "d2", "symbol": "BBB", "action": "buy"},
    ]
    audits = [
        {
            "decision_id": "d1",
            "violations": [
                {"type": "Position Overweight", "category": "position"},
                {"type": "No Evidence Trade", "category": "evidence"},
            ],
            "warnings": [],
        },
        {
            "decision_id": "d2",
            "violations": [],
            "warnings": [{"type": "Thesis Drift", "category": "thesis"}],
        },
    ]

    attribution = build_review_attribution(decisions, audits)

    assert attribution["portfolio"]["issue_count"] == 1
    assert attribution["behavior"]["issue_count"] == 1
    assert attribution["security"]["issue_count"] == 1
    assert attribution["symbols"] == {"AAA": 1, "BBB": 1}


def test_rule_revision_suggestions_for_repeated_open_violations() -> None:
    suggestions = build_rule_revision_suggestions(
        [
            {
                "symbol": "AAA",
                "type": "No Evidence Trade",
                "status": "open",
            },
            {
                "symbol": "AAA",
                "type": "No Evidence Trade",
                "status": "open",
            },
            {
                "symbol": "AAA",
                "type": "Position Overweight",
                "status": "resolved",
            },
        ]
    )

    assert any(item["scope"] == "profile" for item in suggestions)
    assert any(item["scope"] == "card:AAA" for item in suggestions)

