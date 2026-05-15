from app.schemas import Scorecard
from app.services.scoring import ai_sludge_penalty, calculate_overall_score, verdict_for_score


def test_ai_sludge_penalty_bands() -> None:
    assert ai_sludge_penalty(20) == 0
    assert ai_sludge_penalty(40) == 4
    assert ai_sludge_penalty(60) == 9
    assert ai_sludge_penalty(80) == 16
    assert ai_sludge_penalty(100) == 25


def test_ai_sludge_caps_overall_score() -> None:
    scores = Scorecard(
        brand_fit=95,
        audience_fit=95,
        clarity=95,
        human_sound=95,
        specificity=95,
        trust=95,
        distinctiveness=95,
    )

    assert calculate_overall_score(scores, "General brand copy", 70) == 74
    assert calculate_overall_score(scores, "General brand copy", 85) == 59


def test_verdict_labels() -> None:
    assert verdict_for_score(91) == "Sharp and distinctive"
    assert verdict_for_score(80) == "Strong, with clear revision targets"
    assert verdict_for_score(65) == "Usable but generic or under-supported"
    assert verdict_for_score(45) == "Understandable but off-brand"
    assert verdict_for_score(20) == "Needs serious rewrite"
