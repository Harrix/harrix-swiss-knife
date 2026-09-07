"""Context menu: suggestions and Add to dictionary for misspelled words."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeGuard

from PySide6.QtGui import QAction, QCursor, QTextCursor
from PySide6.QtWidgets import QLineEdit, QMenu, QPlainTextEdit, QTextEdit, QWidget

from harrix_swiss_knife.spellcheck.engine import SpellEngine, get_spell_engine
from harrix_swiss_knife.spellcheck.tokenize import word_at_index

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QPoint

TextEditor = QLineEdit | QPlainTextEdit | QTextEdit

_DEFAULT_SUGGEST_LIMIT = 7


def is_text_editor(widget: QWidget) -> TypeGuard[TextEditor]:
    """Return whether `widget` is a supported spellcheck editor type."""
    return isinstance(widget, (QLineEdit, QPlainTextEdit, QTextEdit))


def cursor_char_index(widget: TextEditor, global_pos: QPoint | None = None) -> int:
    """Return the character index under `global_pos` (or the caret if omitted)."""
    if isinstance(widget, QLineEdit):
        if global_pos is not None:
            local = widget.mapFromGlobal(global_pos)
            return widget.cursorPositionAt(local)
        return widget.cursorPosition()
    if global_pos is not None:
        local = widget.mapFromGlobal(global_pos)
        cursor = widget.cursorForPosition(local)
        return cursor.position()
    return widget.textCursor().position()


def editor_plain_text(widget: TextEditor) -> str:
    """Return the full plain text of a supported editor."""
    if isinstance(widget, QLineEdit):
        return widget.text()
    return widget.toPlainText()


def misspelled_word_at(
    widget: TextEditor,
    engine: SpellEngine | None = None,
    *,
    global_pos: QPoint | None = None,
) -> tuple[int, int, str] | None:
    """Return `(start, end, word)` when the token under the cursor is misspelled."""
    spell = engine if engine is not None else get_spell_engine()
    text = editor_plain_text(widget)
    index = cursor_char_index(widget, global_pos)
    span = word_at_index(text, index)
    if span is None:
        return None
    _start, _end, word = span
    if spell.lookup(word):
        return None
    return span


def replace_word_span(widget: TextEditor, start: int, end: int, replacement: str) -> None:
    """Replace characters `[start, end)` in `widget` with `replacement`."""
    if isinstance(widget, QLineEdit):
        text = widget.text()
        widget.setText(text[:start] + replacement + text[end:])
        widget.setCursorPosition(start + len(replacement))
        return
    cursor = widget.textCursor()
    cursor.beginEditBlock()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    cursor.insertText(replacement)
    cursor.endEditBlock()
    widget.setTextCursor(cursor)


def populate_spellcheck_menu(
    menu: QMenu,
    widget: TextEditor,
    *,
    engine: SpellEngine | None = None,
    global_pos: QPoint | None = None,
    on_changed: Callable[[], None] | None = None,
    suggest_limit: int = _DEFAULT_SUGGEST_LIMIT,
) -> int:
    """Insert suggestions and Add to dictionary at the top of `menu`.

    Returns the number of spellcheck actions added (0 when the word is fine).
    """
    spell = engine if engine is not None else get_spell_engine()
    span = misspelled_word_at(widget, spell, global_pos=global_pos)
    if span is None:
        return 0
    start, end, word = span
    suggestions = spell.suggest(word, limit=suggest_limit)
    insert_before = menu.actions()[0] if menu.actions() else None
    added = 0

    def _notify() -> None:
        if on_changed is not None:
            on_changed()

    for suggestion in suggestions:
        action = QAction(suggestion, menu)
        action.setObjectName("hskSpellcheckSuggestion")

        def _make_replacer(repl: str, s: int, e: int) -> Callable[[], None]:
            def _replace() -> None:
                replace_word_span(widget, s, e, repl)
                _notify()

            return _replace

        action.triggered.connect(_make_replacer(suggestion, start, end))
        if insert_before is not None:
            menu.insertAction(insert_before, action)
        else:
            menu.addAction(action)
        added += 1

    if suggestions:
        separator = menu.insertSeparator(insert_before) if insert_before is not None else menu.addSeparator()
        del separator
        added += 1

    add_action = QAction(f'Add "{word}" to dictionary', menu)
    add_action.setObjectName("hskSpellcheckAddToDictionary")

    def _add() -> None:
        if spell.add_to_user_dictionary(word):
            _notify()

    add_action.triggered.connect(_add)
    if insert_before is not None:
        menu.insertAction(insert_before, add_action)
        menu.insertSeparator(insert_before)
    else:
        menu.addAction(add_action)
        menu.addSeparator()
    added += 2
    return added


def add_dictionary_action(
    menu: QMenu,
    widget: TextEditor,
    *,
    engine: SpellEngine | None = None,
    global_pos: QPoint | None = None,
    on_added: Callable[[str], None] | None = None,
) -> QAction | None:
    """Append **Add to dictionary** when a misspelled word is under the cursor.

    Prefer `populate_spellcheck_menu` for the full context-menu UX.
    """
    spell = engine if engine is not None else get_spell_engine()
    span = misspelled_word_at(widget, spell, global_pos=global_pos)
    if span is None:
        return None
    _start, _end, word = span
    action = QAction(f'Add "{word}" to dictionary', menu)
    action.setObjectName("hskSpellcheckAddToDictionary")

    def _add() -> None:
        if spell.add_to_user_dictionary(word) and on_added is not None:
            on_added(word)

    action.triggered.connect(_add)
    menu.addAction(action)
    return action


def popup_spellcheck_menu(
    widget: TextEditor,
    global_pos: QPoint | None = None,
    *,
    engine: SpellEngine | None = None,
    on_changed: Callable[[], None] | None = None,
    base_menu: QMenu | None = None,
) -> bool:
    """Show a context menu with suggestions and Add to dictionary when applicable."""
    pos = global_pos if global_pos is not None else QCursor.pos()
    if base_menu is not None:
        return populate_spellcheck_menu(base_menu, widget, engine=engine, global_pos=pos, on_changed=on_changed) > 0

    menu = QMenu(widget)
    if populate_spellcheck_menu(menu, widget, engine=engine, global_pos=pos, on_changed=on_changed) == 0:
        menu.deleteLater()
        return False
    menu.exec(pos)
    return True
