from disciplineos.scoring import calculate_discipline_score


def test_calculate_weighted_discipline_score() -> None:
    report = calculate_discipline_score(
        [
            {
                "violations": [
                    {
                        "type": "Position Overweight",
                        "category": "position",
                        "severity": "high",
                        "weight": 25,
                    }
                ],
                "warnings": [
                    {
                        "type": "No Evidence Trade",
                        "category": "evidence",
                        "severity": "medium",
                        "weight": 10,
                    }
                ],
            }
        ]
    )

    assert report["score"] == 69
    assert report["dimensions"]["position"]["score"] == 0
    assert report["dimensions"]["evidence"]["score"] == 4

