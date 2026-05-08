from disciplineos.models import AuditStatus, InvestorProfile, Position
from disciplineos.position_guard import (
    build_position_guard_report,
    project_position_percent,
)


def test_position_guard_flags_single_and_sector_exposure() -> None:
    profile = InvestorProfile(
        name="tester",
        style="value",
        max_single_position_pct=15,
        max_sector_position_pct=30,
    )
    positions = [
        Position(
            symbol="AAA",
            name="AAA",
            sector="technology",
            quantity=14,
            current_price=10,
        ),
        Position(
            symbol="BBB",
            name="BBB",
            sector="technology",
            quantity=86,
            current_price=10,
        ),
    ]

    report = build_position_guard_report(profile, positions)

    assert report.total_market_value == 1000
    assert report.positions[0].status == AuditStatus.WARN
    assert report.positions[1].status == AuditStatus.BLOCKED
    assert report.sectors[0].status == AuditStatus.BLOCKED


def test_project_position_percent_for_add_decision() -> None:
    positions = [
        Position(symbol="AAA", name="AAA", quantity=10, current_price=10),
        Position(symbol="BBB", name="BBB", quantity=90, current_price=10),
    ]

    before, after = project_position_percent(
        positions,
        symbol="AAA",
        action="add",
        amount=100,
    )

    assert before == 10
    assert after == 18.18
