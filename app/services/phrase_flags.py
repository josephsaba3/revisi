from dataclasses import dataclass
import re

from .spec_loader import load_phrase_flags


@dataclass(frozen=True)
class PhraseHit:
    category: str
    phrase: str
    count: int


def find_phrase_flags(text: str) -> list[PhraseHit]:
    hits: list[PhraseHit] = []
    lower_text = text.lower()

    for category, phrases in load_phrase_flags().items():
        for phrase in phrases:
            needle = phrase.lower()
            if not needle or needle.startswith("Repeated ") or needle.startswith("Three-item "):
                continue
            count = len(re.findall(rf"(?<!\w){re.escape(needle)}(?!\w)", lower_text))
            if count:
                hits.append(PhraseHit(category=category, phrase=phrase, count=count))

    return hits


def estimate_ai_sludge_risk(text: str) -> int:
    hits = find_phrase_flags(text)
    long_paragraphs = sum(1 for paragraph in text.split("\n") if len(paragraph.split()) > 45)
    em_dash_count = text.count("--") + text.count("—")
    risk = min(100, len(hits) * 8 + long_paragraphs * 7 + em_dash_count * 4)
    return risk
