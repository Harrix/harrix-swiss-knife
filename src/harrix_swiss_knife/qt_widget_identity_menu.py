"""Copy object name / class name for any widget (Fluent gallery — style inspector).

Middle-click a widget to open the identity menu. Right-click keeps each control's
own context menu (editors, tables, command cards, etc.).

Widgets without an `objectName` get one automatically on polish/show (and again
when the identity menu opens). Existing names — Designer ids, Fluent QSS hooks
like `FluentListView` — are never overwritten.

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QClipboard, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QApplication, QMenu, QMenuBar, QWidget

from harrix_swiss_knife.fluent.widgets.menus import FluentMenu
from harrix_swiss_knife.qt_lucide_icon import apply_leading_chrome_icons

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint

_PROP_FILTER = "_hskWidgetIdentityFilter"
_COPY_OBJECT_NAME_PREFIX = "📋 Copy object name ("
_COPY_CLASS_NAME_PREFIX = "📋 Copy class name ("
_AUTO_NAME_COUNTS: dict[str, int] = {}
_SLUG_RE = re.compile(r"[^\w]+", re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+")


class WidgetIdentityEventFilter(QObject):
    """Application filter: auto object names + middle-click identity menu."""

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Assign missing object names; open the identity menu on middle-click."""
        if event.type() in {QEvent.Type.Polish, QEvent.Type.Show} and isinstance(obj, QWidget):
            ensure_widget_object_name(obj)
            return False
        if event.type() != QEvent.Type.MouseButtonPress or not isinstance(event, QMouseEvent):
            return False
        if event.button() != Qt.MouseButton.MiddleButton:
            return False
        widget = resolve_identity_widget(obj)
        if widget is None or _is_menu_chrome(widget):
            return False
        show_widget_identity_context_menu(widget, event.globalPosition().toPoint())
        return True


def add_widget_identity_actions(menu: QMenu, widget: QWidget) -> None:
    """Append Copy object name / Copy class name actions for `widget` to `menu`."""
    object_name = widget_object_name_for_copy(widget)
    class_name = widget_class_name_for_copy(widget)
    copy_name = menu.addAction(format_copy_object_name_menu_label(object_name))
    copy_name.triggered.connect(lambda *_args, text=object_name: _copy_text(text))
    copy_class = menu.addAction(format_copy_class_name_menu_label(class_name))
    copy_class.triggered.connect(lambda *_args, text=class_name: _copy_text(text))


def ensure_widget_object_name(widget: QWidget) -> str:
    """Set a stable object name when missing; return the name used for copy."""
    existing = widget.objectName().strip()
    if existing:
        return existing
    if _is_menu_chrome(widget):
        return type(widget).__name__
    name = _allocate_object_name(_compose_object_name_base(widget))
    widget.setObjectName(name)
    return name


def format_copy_class_name_menu_label(class_name: str) -> str:
    """Build the Copy class name menu label."""
    return f"{_COPY_CLASS_NAME_PREFIX}{class_name})"


def format_copy_object_name_menu_label(object_name: str) -> str:
    """Build the Copy object name menu label."""
    return f"{_COPY_OBJECT_NAME_PREFIX}{object_name})"


def install_widget_identity_context_menus(app: QApplication) -> None:
    """Install an app-wide filter for auto object names and the identity menu."""
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP_FILTER)
    if isinstance(existing, WidgetIdentityEventFilter):
        return
    event_filter = WidgetIdentityEventFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP_FILTER, event_filter)


def resolve_identity_widget(obj: QObject | None) -> QWidget | None:
    """Map a click target (often a viewport) to the identity widget."""
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
    menu = FluentMenu("", widget)
    add_widget_identity_actions(menu, widget)
    apply_leading_chrome_icons(menu)
    menu.refresh_theme()
    menu.exec(global_pos)


def widget_class_name_for_copy(widget: QWidget) -> str:
    """Return the class name shown and copied for `widget`."""
    return type(widget).__qualname__


def widget_object_name_for_copy(widget: QWidget) -> str:
    """Return the object name shown and copied for `widget`."""
    return ensure_widget_object_name(widget)


def _allocate_object_name(base: str) -> str:
    count = _AUTO_NAME_COUNTS.get(base, 0) + 1
    _AUTO_NAME_COUNTS[base] = count
    return base if count == 1 else f"{base}_{count}"


def _compose_object_name_base(widget: QWidget) -> str:
    class_name = type(widget).__name__
    slug = _slugify(_label_for_widget(widget))
    return f"{class_name}_{slug}" if slug else class_name


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


def _label_for_widget(widget: QWidget) -> str:
    for attr in ("text", "title", "windowTitle", "accessibleName"):
        getter = getattr(widget, attr, None)
        if not callable(getter):
            continue
        value = getter()
        if isinstance(value, str) and value.strip():
            return value.strip()
    tip = widget.toolTip().strip()
    if tip:
        return tip.splitlines()[0].strip()
    return ""


def _slugify(text: str) -> str:
    collapsed = _WHITESPACE_RE.sub("_", text.strip())
    slug = _SLUG_RE.sub("", collapsed)
    return slug[:48].strip("_")
