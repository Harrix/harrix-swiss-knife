"""Tests for Russian word-form parsing and bulk user-dictionary merges."""

from __future__ import annotations

from pathlib import Path

from harrix_swiss_knife.integrations.bothub.russian_word_forms import parse_russian_word_forms
from harrix_swiss_knife.spellcheck.user_dict import add_user_words, load_user_words

# Russian lemma "commit" and a few declined forms (Unicode escapes).
_LEMMA = "\u043a\u043e\u043c\u043c\u0438\u0442"
_GEN = "\u043a\u043e\u043c\u043c\u0438\u0442\u0430"
_DAT = "\u043a\u043e\u043c\u043c\u0438\u0442\u0443"
_PL = "\u043a\u043e\u043c\u043c\u0438\u0442\u044b"
_GEN_PL = "\u043a\u043e\u043c\u043c\u0438\u0442\u043e\u0432"


def test_add_user_words_merges_once(tmp_path: Path) -> None:
    path = tmp_path / "spellcheck_user_dict.txt"
    first = add_user_words([_LEMMA, _GEN, _LEMMA], path)
    assert first == {_LEMMA, _GEN}
    second = add_user_words([_DAT, _GEN], path)
    assert second == {_LEMMA, _GEN, _DAT}
    assert load_user_words(path) == second


def test_parse_russian_word_forms_ignores_noise() -> None:
    text = f"Forms:\n{_LEMMA}!\n# note\n123\n"
    assert parse_russian_word_forms(text, lemma=_LEMMA) == [_LEMMA]


def test_parse_russian_word_forms_strips_bullets_and_keeps_lemma() -> None:
    text = f"""
    ```text
    - {_LEMMA}
    1. {_GEN}
    {_DAT}, {_PL}
    {_GEN_PL}
    ```
    """
    forms = parse_russian_word_forms(text, lemma=_LEMMA)
    assert forms[0] == _LEMMA
    assert forms == [_LEMMA, _GEN, _DAT, _PL, _GEN_PL]
