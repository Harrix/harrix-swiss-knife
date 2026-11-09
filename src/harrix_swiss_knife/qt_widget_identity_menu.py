"""Copy object name / class name for any widget (Fluent gallery — style inspector).

Plain right-click shows the menu on widgets that do not already own a useful
context menu. Hold Ctrl and right-click to force the identity menu on tables,
command cards, editors, and other CustomContextMenu hosts.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QClipboard, QContextMenuEvent, QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLineEdit,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)

from harrix_swiss_knife.qt_lucide_icon import apply_leading_chrome_icons

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint

_PROP_FILTER = "_hskWidgetIdentityFilter"
_COPY_OBJECT_NAME_PREFIX = "📋 Copy object name ("
_COPY_CLASS_NAME_PREFIX = "📋 Copy class name ("

# Widgets whose DefaultContextMenu is useful; plain right-click keeps it.
_KEEP_DEFAULT_CONTEXT_MENU: tuple[type[QWidget], ...] = (
    QAbstractItemView,
    QAbstractSpinBox,
    QComboBox,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
)


class WidgetIdentityEventFilter(QObject):
    """Application filter that offers Copy object name / Copy class name."""

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Open the identity menu on ContextMenu when appropriate."""
        if event.type() != QEvent.Type.ContextMenu or not isinstance(event, QContextMenuEvent):
            return False
        widget = resolve_identity_widget(obj)
        if widget is None or not _should_handle_context_menu(widget, event):
            return False
        show_widget_identity_context_menu(widget, event.globalPos())
        return True


def add_widget_identity_actions(menu: QMenu, widget: QWidget) -> None:
    """Append Copy object name / Copy class name actions for `widget` to `menu`."""
    object_name = widget_object_name_for_copy(widget)
    class_name = widget_class_name_for_copy(widget)
    copy_name = menu.addAction(format_copy_object_name_menu_label(object_name))
    copy_name.triggered.connect(lambda *_args, text=object_name: _copy_text(text))
    copy_class = menu.addAction(format_copy_class_name_menu_label(class_name))
    copy_class.triggered.connect(lambda *_args, text=class_name: _copy_text(text))


def format_copy_class_name_menu_label(class_name: str) -> str:
    """Build the Copy class name menu label."""
    return f"{_COPY_CLASS_NAME_PREFIX}{class_name})"


def format_copy_object_name_menu_label(object_name: str) -> str:
    """Build the Copy object name menu label."""
    return f"{_COPY_OBJECT_NAME_PREFIX}{object_name})"


def install_widget_identity_context_menus(app: QApplication) -> None:
    """Install an app-wide filter for the widget identity context menu."""
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP_FILTER)
    if isinstance(existing, WidgetIdentityEventFilter):
        return
    event_filter = WidgetIdentityEventFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP_FILTER, event_filter)


def resolve_identity_widget(obj: QObject | None) -> QWidget | None:
    """Map a context-menu target (often a viewport) to the identity widget."""
    if not isinstance(obj, QWidget):
        return None
    widget: QWidget = obj
    parent = widget.parentWidget()
    if parent is not None:
        viewport = getattr(parent, "viewport", None)
        if callable(viewport) and viewport() is widget:
            return parent
    return widget


def show_widget_identity_context_menu(widget: QWidget, global_pos: QPoint) -> None:
    """Show Copy object name / Copy class name for `widget` at `global_pos`."""
    menu = QMenu(widget)
    add_widget_identity_actions(menu, widget)
    apply_leading_chrome_icons(menu)
    menu.exec(global_pos)


def widget_class_name_for_copy(widget: QWidget) -> str:
    """Return the class name shown and copied for `widget`."""
    return type(widget).__qualname__


def widget_object_name_for_copy(widget: QWidget) -> str:
    """Return the object name shown and copied for `widget`."""
    return widget.objectName().strip() or type(widget).__name__


def _copy_text(text: str) -> None:
    clipboard = QGuiApplication.clipboard()
    if clipboard is not None:
        clipboard.setText(text, QClipboard.Mode.Clipboard)


def _is_menu_chrome(widget: QWidget) -> bool:
    current: QWidget | None = widget
    while current is not None:
        if isinstance(current, (QMenu, QMenuBar)):
            return True
        current = current.parentWidget()
    return False


def _plain_right_click_shows_identity(widget: QWidget) -> bool:
    """Whether a normal right-click may open the identity menu on `widget`."""
    policy = widget.contextMenuPolicy()
    if policy in {
        Qt.ContextMenuPolicy.PreventContextMenu,
        Qt.ContextMenuPolicy.CustomContextMenu,
    }:
        return False
    # Cards and similar hosts emit their own context_menu_requested signal.
    if hasattr(widget, "context_menu_requested") and type(widget).contextMenuEvent is not QWidget.contextMenuEvent:
        return False
    return not isinstance(widget, _KEEP_DEFAULT_CONTEXT_MENU)


def _should_handle_context_menu(widget: QWidget, event: QContextMenuEvent) -> bool:
    if _is_menu_chrome(widget):
        return False
    modifiers = event.modifiers()
    if modifiers == Qt.KeyboardModifier.NoModifier:
        modifiers = QGuiApplication.keyboardModifiers()
    if bool(modifiers & Qt.KeyboardModifier.ControlModifier):
        return True
    return _plain_right_click_shows_identity(widget)
