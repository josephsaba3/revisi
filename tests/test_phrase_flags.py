from app.services.phrase_flags import estimate_ai_sludge_risk, find_phrase_flags


def test_find_phrase_flags_matches_known_phrases() -> None:
    hits = find_phrase_flags("Our all-in-one solution helps teams streamline operations with ease.")
    phrases = {hit.phrase for hit in hits}

    assert "all-in-one solution" in phrases
    assert "streamline operations" in phrases
    assert "with ease" in phrases


def test_estimate_ai_sludge_risk_increases_with_flags() -> None:
    clean = estimate_ai_sludge_risk("Send your page. Get a practical rewrite with clear proof gaps.")
    flagged = estimate_ai_sludge_risk("Unlock the power of a seamless experience like never before.")

    assert flagged > clean
