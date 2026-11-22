"""Load, save, and append words in the personal spellcheck dictionary."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_swiss_knife.paths import get_spellcheck_user_dict_path

if TYPE_CHECKING:
    from pathlib import Path


def add_user_word(word: str, path: Path | None = None) -> set[str]:
    """Add `word` to the user dictionary and return the updated set.

    Empty or whitespace-only words are ignored.

    """
    return add_user_words([word], path)


def add_user_words(words_to_add: list[str] | set[str] | tuple[str, ...], path: Path | None = None) -> set[str]:
    """Add many words to the user dictionary in one write and return the set.

    Empty or whitespace-only entries are ignored. Existing words stay unchanged.

    """
    words = load_user_words(path)
    changed = False
    for word in words_to_add:
        cleaned = word.strip()
        if not cleaned or cleaned in words:
            continue
        words.add(cleaned)
        changed = True
    if changed:
        save_user_words(words, path)
    return words


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
