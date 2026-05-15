from functools import lru_cache
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / "references"


SCORING_CONTEXT_WEIGHTS: dict[str, dict[str, float]] = {
    "SaaS feature page": {
        "brand_fit": 0.16,
        "audience_fit": 0.12,
        "clarity": 0.22,
        "human_sound": 0.14,
        "specificity": 0.18,
        "trust": 0.10,
        "distinctiveness": 0.08,
    },
    "Dental / healthcare page": {
        "brand_fit": 0.10,
        "audience_fit": 0.16,
        "clarity": 0.18,
        "human_sound": 0.12,
        "specificity": 0.14,
        "trust": 0.24,
        "distinctiveness": 0.06,
    },
    "Founder-led homepage": {
        "brand_fit": 0.20,
        "audience_fit": 0.10,
        "clarity": 0.17,
        "human_sound": 0.18,
        "specificity": 0.08,
        "trust": 0.12,
        "distinctiveness": 0.15,
    },
    "Blog / educational content": {
        "brand_fit": 0.10,
        "audience_fit": 0.12,
        "clarity": 0.22,
        "human_sound": 0.15,
        "specificity": 0.17,
        "trust": 0.18,
        "distinctiveness": 0.06,
    },
    "General brand copy": {
        "brand_fit": 0.16,
        "audience_fit": 0.13,
        "clarity": 0.19,
        "human_sound": 0.15,
        "specificity": 0.15,
        "trust": 0.14,
        "distinctiveness": 0.08,
    },
}


@lru_cache
def load_reference(name: str) -> str:
    return (REFERENCES / name).read_text(encoding="utf-8")


@lru_cache
def load_phrase_flags() -> dict[str, list[str]]:
    text = load_reference("phrase_flags.md")
    categories: dict[str, list[str]] = {}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = line.removeprefix("## ").strip()
            categories[current] = []
        elif current and line.startswith("- "):
            phrase = re.sub(r"`([^`]+)`", r"\1", line.removeprefix("- ").strip())
            if phrase:
                categories[current].append(phrase)

    return categories


@lru_cache
def load_rewrite_rules() -> str:
    return load_reference("rewrite_rules.md")


@lru_cache
def load_scoring_guide() -> str:
    return load_reference("scoring_guide.md")
