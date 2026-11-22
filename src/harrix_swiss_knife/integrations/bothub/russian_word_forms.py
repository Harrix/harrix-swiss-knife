"""BotHub helper that expands a Russian lemma into spellcheck word forms."""

from __future__ import annotations

import re
from typing import Any

from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_KEY = "russian_word_forms"
PROMPT_MISSING_MSG = "Prompt russian_word_forms is not configured in config.json."

# Cyrillic letter ranges (U+0410-U+044F, Yo), with optional Latin for hybrids.
_CYRILLIC = "\u0410-\u044f\u0401\u0451"
_WORD_TOKEN = re.compile(rf"[A-Za-z{_CYRILLIC}][A-Za-z{_CYRILLIC}\-']*")
_HAS_CYRILLIC = re.compile(rf"[{_CYRILLIC}]")
_BULLET_PREFIX = re.compile(r"^[\s]*(?:[-*•]|\d+[.)])\s+")


def build_russian_word_forms_prompt(word: str, config: dict[str, Any]) -> str:
    """Build the word-forms prompt for `word`.

    Raises:

    - `ValueError`: If the prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        PROMPT_KEY,
        {"WORD": word.strip()},
        prompt_display_name=PROMPT_KEY,
    )


def get_russian_word_forms_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.russian_word_forms` template, or `None` if missing."""
    return get_prompt_template(config, PROMPT_KEY)


def parse_russian_word_forms(text: str, *, lemma: str = "") -> list[str]:
    """Return unique word forms from an AI response, preserving first-seen order.

    Lines may be bare words or bullet / numbered lists. The lemma is inserted
    first when it is non-empty and missing from the response. Tokens without
    Cyrillic letters are ignored, except the lemma itself.

    """
    forms: list[str] = []
    seen: set[str] = set()

    def add(candidate: str, *, allow_latin: bool = False) -> None:
        cleaned = candidate.strip().strip(".,;:!?\"'`«»()[]{}")
        if not cleaned or cleaned in seen:
            return
        if _WORD_TOKEN.fullmatch(cleaned) is None:
            return
        if not allow_latin and _HAS_CYRILLIC.search(cleaned) is None:
            return
        seen.add(cleaned)
        forms.append(cleaned)

    add(lemma, allow_latin=True)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    for raw in cleaned.splitlines():
        line = _BULLET_PREFIX.sub("", raw).strip()
        if not line or line.startswith("#"):
            continue
        for part in re.split(r"[,;/|]+", line):
            token = part.strip()
            if not token:
                continue
            match = _WORD_TOKEN.search(token)
            if match is not None:
                add(match.group(0))
    return forms
