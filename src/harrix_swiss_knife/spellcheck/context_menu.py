"""Context menu: Add misspelled word under cursor to the personal dictionary."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeGuard

from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QLineEdit, QMenu, QPlainTextEdit, QTextEdit, QWidget

from harrix_swiss_knife.spellcheck.engine import SpellEngine, get_spell_engine
from harrix_swiss_knife.spellcheck.tokenize import word_at_index

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QPoint

TextEditor = QLineEdit | QPlainTextEdit | QTextEdit


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


def add_dictionary_action(
    menu: QMenu,
    widget: TextEditor,
    *,
    engine: SpellEngine | None = None,
    global_pos: QPoint | None = None,
    on_added: Callable[[str], None] | None = None,
) -> QAction | None:
    """Append **Add to dictionary** when a misspelled word is under the cursor.

    Returns the created action, or `None` when there is nothing to add.
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
    on_added: Callable[[str], None] | None = None,
    base_menu: QMenu | None = None,
) -> bool:
    """Show a context menu that includes Add to dictionary when applicable.

    When `base_menu` is given, the action is added to it and the menu is not
    executed here. Returns `True` when the Add action was available.
    """
    pos = global_pos if global_pos is not None else QCursor.pos()
    if base_menu is not None:
        return add_dictionary_action(base_menu, widget, engine=engine, global_pos=pos, on_added=on_added) is not None

    menu = QMenu(widget)
    if add_dictionary_action(menu, widget, engine=engine, global_pos=pos, on_added=on_added) is None:
        menu.deleteLater()
        return False
    menu.exec(pos)
    return True
