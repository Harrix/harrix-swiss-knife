"""Tests for global spellcheck tokenize, engine, user dict, and exclusions."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QLineEdit,
    QPlainTextEdit,
    QTableWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.spellcheck.context_menu import replace_word_span
from harrix_swiss_knife.spellcheck.engine import (
    SpellEngine,
    bundled_dictionaries_dir,
    reset_spell_engine_for_tests,
)
from harrix_swiss_knife.spellcheck.install import should_attach_spellcheck, widget_is_inside_item_view
from harrix_swiss_knife.spellcheck.tokenize import iter_word_spans, word_at_index
from harrix_swiss_knife.spellcheck.user_dict import add_user_word, load_user_words, save_user_words


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.fixture
def dicts_dir() -> Path:
    return bundled_dictionaries_dir()


def test_tokenize_mixed_ru_en() -> None:
    text = "Hello мир and test"
    spans = iter_word_spans(text)
    words = [word for _s, _e, word in spans]
    assert "Hello" in words
    assert "мир" in words
    assert "and" in words
    assert "test" in words


def test_tokenize_skips_url_and_digits() -> None:
    text = "see https://example.com/path and 42 bottles"
    words = [word for _s, _e, word in iter_word_spans(text)]
    assert "https" not in words
    assert "example" not in words
    assert "42" not in words
    assert "see" in words
    assert "bottles" in words


def test_tokenize_internal_hyphen_and_apostrophe() -> None:
    text = "well-known don't"
    words = [word for _s, _e, word in iter_word_spans(text)]
    assert words == ["well-known", "don't"]


def test_word_at_index_prefers_left_boundary() -> None:
    text = "hello world"
    assert word_at_index(text, 5) == (0, 5, "hello")
    assert word_at_index(text, 0) == (0, 5, "hello")
    assert word_at_index(text, 6) == (6, 11, "world")


def test_user_dict_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "spellcheck_user_dict.txt"
    save_user_words({"Harrix", "spylls"}, path)
    assert load_user_words(path) == {"Harrix", "spylls"}
    add_user_word("NotepadPlusPlus", path)
    assert "NotepadPlusPlus" in load_user_words(path)


def test_engine_lookup_en_ru_and_user(dicts_dir: Path, tmp_path: Path) -> None:
    reset_spell_engine_for_tests()
    user_path = tmp_path / "user.txt"
    engine = SpellEngine(dictionaries_dir=dicts_dir, user_dict_path=user_path)
    assert engine.ensure_loaded()
    assert engine.lookup("hello")
    assert engine.lookup("привет")
    assert not engine.lookup("zzzznotawordzzz")
    assert engine.add_to_user_dictionary("zzzznotawordzzz")
    assert engine.lookup("zzzznotawordzzz")


def test_engine_suggest_russian_typo(dicts_dir: Path, tmp_path: Path) -> None:
    engine = SpellEngine(dictionaries_dir=dicts_dir, user_dict_path=tmp_path / "user.txt")
    assert engine.ensure_loaded()
    suggestions = engine.suggest("преехал", limit=5)
    assert "приехал" in suggestions


def test_replace_word_span_line_edit(qapp: QApplication) -> None:  # noqa: ARG001
    line = QLineEdit("foo bar baz")
    replace_word_span(line, 4, 7, "qux")
    assert line.text() == "foo qux baz"
    assert line.cursorPosition() == 7


def test_exclude_table_editor(qapp: QApplication) -> None:  # noqa: ARG001
    table = QTableWidget(1, 1)
    editor = QLineEdit(table)
    table.setCellWidget(0, 0, editor)
    assert widget_is_inside_item_view(editor)
    assert not should_attach_spellcheck(editor)


def test_exclude_spinbox_line_edit(qapp: QApplication) -> None:  # noqa: ARG001
    spin = QDoubleSpinBox()
    line = spin.lineEdit()
    assert line is not None
    assert not should_attach_spellcheck(line)


def test_exclude_readonly_and_password(qapp: QApplication) -> None:  # noqa: ARG001
    readonly = QPlainTextEdit()
    readonly.setReadOnly(True)
    assert not should_attach_spellcheck(readonly)

    password = QLineEdit()
    password.setEchoMode(QLineEdit.EchoMode.Password)
    assert not should_attach_spellcheck(password)

    browser = QTextBrowser()
    assert not should_attach_spellcheck(browser)


def test_attach_allowed_for_normal_line_edit(qapp: QApplication) -> None:  # noqa: ARG001
    host = QWidget()
    layout = QVBoxLayout(host)
    line = QLineEdit()
    layout.addWidget(line)
    assert should_attach_spellcheck(line)
