"""Tests for shared text result dialog helpers."""

from __future__ import annotations

from harrix_swiss_knife.actions.common.text_result_dialog import (
    collapse_text_to_single_line,
    is_multiline_text,
)


def test_is_multiline_text() -> None:
    assert not is_multiline_text("")
    assert not is_multiline_text("one line")
    assert not is_multiline_text("one line\n")
    assert not is_multiline_text("one line\n\n")
    assert not is_multiline_text("  one line  \n")
    assert is_multiline_text("line one\nline two")
    assert is_multiline_text("a\n\nb")


def test_collapse_text_to_single_line() -> None:
    assert collapse_text_to_single_line("a\n\nb  c") == "a b c"
    assert not is_multiline_text(collapse_text_to_single_line("a\nb\nc"))
