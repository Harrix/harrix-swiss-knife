"""Unicode word spans for spellcheck (skip URLs, emails, and path-like runs)."""

from __future__ import annotations

import re
from re import Pattern

# Skip whole URL / email / Windows or POSIX path runs before word tokenization.
_SKIP_RUN_RE: Pattern[str] = re.compile(
    r"https?://[^\s]+"
    r"|www\.[^\s]+"
    r"|[\w.+-]+@[\w.-]+\.\w+"
    r"|[A-Za-z]:\\[^\s]+"
    r"|/(?:[\w.-]+/)+\S*",
    re.UNICODE,
)

# Letters/digits with optional internal apostrophes or hyphens (no leading/trailing).
_WORD_RE: Pattern[str] = re.compile(
    r"[^\W_]+(?:['\u2019-][^\W_]+)*",
    re.UNICODE,
)

_DIGITS_ONLY_RE: Pattern[str] = re.compile(r"^\d+$")


def iter_skip_spans(text: str) -> list[tuple[int, int]]:
    """Return `[start, end)` spans that must not be spellchecked."""
    return [(m.start(), m.end()) for m in _SKIP_RUN_RE.finditer(text)]


def iter_word_spans(text: str) -> list[tuple[int, int, str]]:
    """Return `(start, end, word)` spans for spellcheckable tokens in `text`.

    Words may contain letters, digits, and internal `'` / `-`. Pure digit tokens,
    and tokens inside URL/email/path runs, are omitted.

    """
    skip_spans = iter_skip_spans(text)
    spans: list[tuple[int, int, str]] = []
    for match in _WORD_RE.finditer(text):
        start, end = match.start(), match.end()
        if _in_skip(start, skip_spans):
            continue
        word = match.group(0)
        if _DIGITS_ONLY_RE.fullmatch(word):
            continue
        spans.append((start, end, word))
    return spans


def word_at_index(text: str, index: int) -> tuple[int, int, str] | None:
    """Return the word span covering `index`, or `None` if there is none.

    When `index` sits on a boundary (typical caret after a word), the word to the
    left is preferred.

    """
    if index < 0 or index > len(text):
        return None
    spans = iter_word_spans(text)
    for start, end, word in spans:
        if start <= index < end:
            return start, end, word
    if index > 0:
        for start, end, word in spans:
            if start <= index - 1 < end:
                return start, end, word
    return None


def _in_skip(index: int, skip_spans: list[tuple[int, int]]) -> bool:
    return any(start <= index < end for start, end in skip_spans)
