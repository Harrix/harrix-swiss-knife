"""Hunspell (spylls) engine: en_US + ru_RU + personal dictionary."""

from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.spellcheck import user_dict as user_dict_mod

if TYPE_CHECKING:
    from spylls.hunspell import Dictionary

log = logging.getLogger(__name__)

_ENGINE_LOCK = Lock()
_ENGINE: SpellEngine | None = None


class SpellEngine:
    """Lookup words against English, Russian, and the user dictionary (OR)."""

    def __init__(self, dictionaries_dir: Path | None = None, user_dict_path: Path | None = None) -> None:
        """Create an unloaded engine; call `ensure_loaded` before lookup."""
        self._dictionaries_dir = dictionaries_dir if dictionaries_dir is not None else bundled_dictionaries_dir()
        self._user_dict_path = user_dict_path
        self._dicts: list[Dictionary] = []
        self._user_words: set[str] = set()
        self._user_words_folded: set[str] = set()
        self._loaded = False
        self._load_error: str | None = None

    def add_to_user_dictionary(self, word: str) -> bool:
        """Persist `word` in the personal dictionary and refresh in-memory set.

        Returns:

        - `bool`: `True` when the word was added (or already present).

        """
        cleaned = word.strip()
        if not cleaned:
            return False
        self._set_user_words(user_dict_mod.add_user_word(cleaned, self._user_dict_path))
        return True

    def ensure_loaded(self) -> bool:
        """Load Hunspell dictionaries and the user word list once.

        Returns:

        - `bool`: `True` when at least one language dictionary is ready.

        """
        if self._loaded:
            return bool(self._dicts)
        self._loaded = True
        self._set_user_words(user_dict_mod.load_user_words(self._user_dict_path))
        try:
            dictionary_cls = _import_dictionary_class()
        except ImportError as exc:
            self._load_error = str(exc)
            log.warning("%s", self._load_error)
            return False
        for name in ("en_US", "ru_RU"):
            stem = self._dictionaries_dir / name
            if not stem.with_suffix(".dic").is_file() or not stem.with_suffix(".aff").is_file():
                log.warning("Spellcheck dictionary missing: %s", stem)
                continue
            try:
                self._dicts.append(dictionary_cls.from_files(str(stem)))
            except Exception:
                log.exception("Failed to load spellcheck dictionary %s", stem)
        if not self._dicts:
            self._load_error = self._load_error or f"No spellcheck dictionaries in {self._dictionaries_dir}"
            log.error("%s", self._load_error)
            return False
        return True

    @property
    def load_error(self) -> str | None:
        """Return a load failure message, or `None` when dictionaries loaded."""
        return self._load_error

    def lookup(self, word: str) -> bool:
        """Return `True` when `word` is in en, ru, or the personal dictionary."""
        if not word:
            return True
        if not self.ensure_loaded():
            return True
        if word in self._user_words or word.casefold() in self._user_words_folded:
            return True
        for dictionary in self._dicts:
            try:
                if dictionary.lookup(word):
                    return True
            except Exception:
                log.exception("Spellcheck lookup failed for %r", word)
        return False

    def reload_user_dictionary(self) -> None:
        """Reload personal words from disk (keeps Hunspell dictionaries)."""
        self._set_user_words(user_dict_mod.load_user_words(self._user_dict_path))

    def suggest(self, word: str, *, limit: int = 7) -> list[str]:
        """Return up to `limit` unique suggestions from en and ru dictionaries."""
        cleaned = word.strip()
        if not cleaned or not self.ensure_loaded() or limit <= 0:
            return []
        seen: set[str] = {cleaned, cleaned.casefold()}
        suggestions: list[str] = []
        for dictionary in self._dicts:
            try:
                for candidate in dictionary.suggest(cleaned):
                    if not candidate or candidate.casefold() in seen:
                        continue
                    seen.add(candidate.casefold())
                    suggestions.append(candidate)
                    if len(suggestions) >= limit:
                        return suggestions
            except Exception:
                log.exception("Spellcheck suggest failed for %r", cleaned)
        return suggestions

    @property
    def user_words(self) -> set[str]:
        """Return a copy of the in-memory personal dictionary."""
        return set(self._user_words)

    def _set_user_words(self, words: set[str]) -> None:
        self._user_words = words
        self._user_words_folded = {w.casefold() for w in words}


def bundled_dictionaries_dir() -> Path:
    """Return the directory that holds bundled `.aff` / `.dic` files."""
    base = Path(__file__).resolve().parent.parent / "assets" / "dictionaries"
    nested = base / "files"
    if (nested / "en_US.dic").is_file() and (nested / "en_US.aff").is_file():
        return nested
    return base


def get_spell_engine() -> SpellEngine:
    """Return the process-wide spellcheck engine (lazy singleton)."""
    global _ENGINE  # noqa: PLW0603
    with _ENGINE_LOCK:
        if _ENGINE is None:
            _ENGINE = SpellEngine()
        return _ENGINE


def reset_spell_engine_for_tests() -> None:
    """Clear the singleton (tests only)."""
    global _ENGINE  # noqa: PLW0603
    with _ENGINE_LOCK:
        _ENGINE = None


def _import_dictionary_class() -> type[Any]:
    """Import spylls `Dictionary` lazily so CLI imports do not require it."""
    try:
        from spylls.hunspell import Dictionary  # noqa: PLC0415
    except ImportError as exc:
        msg = "spylls is not installed; run `uv sync` or reinstall the hsk tool"
        raise ImportError(msg) from exc
    return Dictionary
