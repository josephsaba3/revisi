from app.schemas import Scorecard

from .spec_loader import SCORING_CONTEXT_WEIGHTS


def ai_sludge_penalty(risk: int) -> int:
    if risk <= 20:
        return 0
    if risk <= 40:
        return 4
    if risk <= 60:
        return 9
    if risk <= 80:
        return 16
    return 25


def verdict_for_score(score: int) -> str:
    if score >= 90:
        return "Sharp and distinctive"
    if score >= 75:
        return "Strong, with clear revision targets"
    if score >= 60:
        return "Usable but generic or under-supported"
    if score >= 40:
        return "Understandable but off-brand"
    return "Needs serious rewrite"


def calculate_overall_score(scores: Scorecard, scoring_context: str, ai_sludge_risk: int) -> int:
    weights = SCORING_CONTEXT_WEIGHTS.get(scoring_context, SCORING_CONTEXT_WEIGHTS["General brand copy"])
    score_values = scores.model_dump()
    weighted = sum(score_values[key] * weight for key, weight in weights.items())
    adjusted = round(weighted - ai_sludge_penalty(ai_sludge_risk))

    if ai_sludge_risk >= 85:
        adjusted = min(adjusted, 59)
    elif ai_sludge_risk >= 70:
        adjusted = min(adjusted, 74)

    return max(0, min(100, adjusted))
