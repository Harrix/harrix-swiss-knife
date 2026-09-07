"""Application-wide spellcheck attach for QLineEdit / QPlainTextEdit / QTextEdit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QChildEvent, QEvent, QObject, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QLineEdit,
    QMenu,
    QPlainTextEdit,
    QTextBrowser,
    QTextEdit,
    QWidget,
)

from harrix_swiss_knife.spellcheck.context_menu import (
    TextEditor,
    is_text_editor,
    populate_spellcheck_menu,
)
from harrix_swiss_knife.spellcheck.engine import SpellEngine, get_spell_engine
from harrix_swiss_knife.spellcheck.highlighter import SpellHighlighter
from harrix_swiss_knife.spellcheck.line_edit import LineEditSpellController

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QContextMenuEvent

_PROP_ATTACHED = "_hskSpellcheck"
_PROP_CONTROLLER = "_hskSpellcheckController"
_PROP_HIGHLIGHTER = "_hskSpellcheckHighlighter"
_PROP_FILTER = "_hskSpellcheckFilter"
_DEBOUNCE_DOC_MS = 300


class SpellcheckEventFilter(QObject):
    """Attach spellcheck when text widgets appear or receive focus."""

    def __init__(self, app: QApplication, engine: SpellEngine | None = None) -> None:
        """Create the filter; `engine` defaults to the process-wide singleton."""
        super().__init__(app)
        self._engine = engine if engine is not None else get_spell_engine()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Attach on show/focus for eligible editors."""
        if event.type() == QEvent.Type.ChildAdded and isinstance(event, QChildEvent):
            child = event.child()
            if isinstance(child, QWidget) and is_text_editor(child):
                attach_to_widget(child, self._engine)
            return False
        if event.type() not in (QEvent.Type.Show, QEvent.Type.FocusIn):
            return False
        if isinstance(watched, QWidget) and is_text_editor(watched):
            attach_to_widget(watched, self._engine)
        return False


def attach_to_widget(widget: QWidget, engine: SpellEngine | None = None) -> bool:
    """Attach spellcheck UI to a supported editor. Returns `True` when attached."""
    if not should_attach_spellcheck(widget):
        return False
    spell = engine if engine is not None else get_spell_engine()
    spell.ensure_loaded()
    widget.setProperty(_PROP_ATTACHED, "1")

    if isinstance(widget, QLineEdit):
        controller = LineEditSpellController(widget, spell)
        widget.setProperty(_PROP_CONTROLLER, controller)

        def _on_changed() -> None:
            controller.refresh()

        _install_context_hook(widget, spell, _on_changed)
        return True

    if isinstance(widget, (QPlainTextEdit, QTextEdit)):
        highlighter = SpellHighlighter(widget.document(), spell)
        widget.setProperty(_PROP_HIGHLIGHTER, highlighter)
        debounce = QTimer(widget)
        debounce.setSingleShot(True)
        debounce.setInterval(_DEBOUNCE_DOC_MS)

        def _rehighlight() -> None:
            highlighter.rehighlight_all()

        def _schedule_rehighlight() -> None:
            debounce.start()

        debounce.timeout.connect(_rehighlight)
        widget.textChanged.connect(_schedule_rehighlight)

        def _on_changed() -> None:
            highlighter.rehighlight_all()

        _install_context_hook(widget, spell, _on_changed)
        return True

    return False


def install_spellcheck(app: QApplication, engine: SpellEngine | None = None) -> None:
    """Install an application-wide filter that attaches spellcheck to text editors."""
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP_FILTER)
    if isinstance(existing, SpellcheckEventFilter):
        return
    spell = engine if engine is not None else get_spell_engine()
    QTimer.singleShot(0, spell.ensure_loaded)
    event_filter = SpellcheckEventFilter(app, spell)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP_FILTER, event_filter)
    for widget in app.allWidgets():
        if is_text_editor(widget):
            attach_to_widget(widget, spell)


def scan_and_attach(root: QWidget | None = None, engine: SpellEngine | None = None) -> int:
    """Attach spellcheck under `root` (or all app widgets). Returns attach count."""
    spell = engine if engine is not None else get_spell_engine()
    count = 0
    if root is None:
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return 0
        widgets: list[QWidget] = list(app.allWidgets())
    else:
        widgets = [root, *root.findChildren(QWidget)]
    for widget in widgets:
        if is_text_editor(widget) and attach_to_widget(widget, spell):
            count += 1
    return count


def should_attach_spellcheck(widget: QWidget) -> bool:
    """Return whether global spellcheck should attach to `widget`."""
    if widget.property(_PROP_ATTACHED) == "1":
        return False
    if not is_text_editor(widget):
        return False
    if isinstance(widget, QTextBrowser):
        return False
    if widget_is_inside_item_view(widget):
        return False
    if isinstance(widget, QAbstractSpinBox):
        return False
    parent = widget.parent()
    if isinstance(parent, QAbstractSpinBox):
        return False
    if isinstance(widget, QLineEdit):
        echo = widget.echoMode()
        if echo in (QLineEdit.EchoMode.Password, QLineEdit.EchoMode.NoEcho):
            return False
        if widget.isReadOnly():
            return False
    elif isinstance(widget, (QPlainTextEdit, QTextEdit)) and widget.isReadOnly():
        return False
    return True


def widget_is_inside_item_view(widget: QObject | None) -> bool:
    """Return `True` when `widget` is under a `QAbstractItemView` (table/list editors)."""
    current: QObject | None = widget
    while current is not None:
        if isinstance(current, QAbstractItemView):
            return True
        current = current.parent()
    return False


def _install_context_hook(
    widget: TextEditor,
    engine: SpellEngine,
    on_changed: Callable[[], None],
) -> None:
    def context_menu_event(event: QContextMenuEvent) -> None:
        menu: QMenu | None = widget.createStandardContextMenu()
        if menu is None:
            event.ignore()
            return
        populate_spellcheck_menu(
            menu,
            widget,
            engine=engine,
            global_pos=event.globalPos(),
            on_changed=on_changed,
        )
        menu.exec_(event.globalPos())
        event.accept()

    widget.contextMenuEvent = context_menu_event  # ty: ignore[invalid-assignment]
