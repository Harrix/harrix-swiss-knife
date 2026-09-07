"""Load, save, and append words in the personal spellcheck dictionary."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.paths import get_spellcheck_user_dict_path

if TYPE_CHECKING:
    from pathlib import Path


def load_user_words(path: Path | None = None) -> set[str]:
    """Load unique non-empty words from the user dictionary file."""
    dict_path = path if path is not None else get_spellcheck_user_dict_path()
    if not dict_path.is_file():
        return set()
    words: set[str] = set()
    text = dict_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        word = line.strip()
        if word and not word.startswith("#"):
            words.add(word)
    return words


def save_user_words(words: set[str], path: Path | None = None) -> None:
    """Write sorted unique words to the user dictionary file (UTF-8)."""
    dict_path = path if path is not None else get_spellcheck_user_dict_path()
    dict_path.parent.mkdir(parents=True, exist_ok=True)
    lines = sorted(words, key=lambda w: (w.casefold(), w))
    dict_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def add_user_word(word: str, path: Path | None = None) -> set[str]:
    """Add `word` to the user dictionary and return the updated set.

    Empty or whitespace-only words are ignored.
    """
    cleaned = word.strip()
    words = load_user_words(path)
    if not cleaned:
        return words
    if cleaned in words:
        return words
    words.add(cleaned)
    save_user_words(words, path)
    return words
