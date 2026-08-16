"""Date edit with a quick preset / offset menu button."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QPoint, QSize, Qt
from PySide6.QtWidgets import QHBoxLayout, QMenu, QPushButton, QVBoxLayout

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDateEdit, QLayout, QWidget


def attach_date_edit_quick_controls(date_edit: QDateEdit, *, button_object_name: str | None = None) -> QPushButton:
    """Replace a bare `QDateEdit` with date field + dropdown quick button.

    Inserts a menu button after `date_edit` in its parent layout, wires the same
    Today / Yesterday / ±1 day actions into the button menu and into the date
    field context menu (keeping standard edit commands), and keeps the button
    caption in sync with the selected date.

    Args:

    - `date_edit` (`QDateEdit`): Existing date field from the UI.
    - `button_object_name` (`str | None`): Object name for the new button.
      Defaults to `{dateEditObjectName}_quick`.

    Returns:

    - `QPushButton`: The created quick-controls button.

    """
    button = QPushButton(date_edit.parentWidget())
    name = button_object_name or f"{date_edit.objectName()}_quick"
    button.setObjectName(name)
    button.setMinimumSize(QSize(61, 0))

    def set_today() -> None:
        date_edit.setDate(QDate.currentDate())

    def set_yesterday() -> None:
        date_edit.setDate(QDate.currentDate().addDays(-1))

    def add_one_day() -> None:
        date_edit.setDate(date_edit.date().addDays(1))

    def subtract_one_day() -> None:
        date_edit.setDate(date_edit.date().addDays(-1))

    def populate_date_actions(menu: QMenu) -> None:
        today_action = menu.addAction("📅 Today's date")
        today_action.triggered.connect(set_today)
        yesterday_action = menu.addAction("📅 Yesterday")
        yesterday_action.triggered.connect(set_yesterday)
        menu.addSeparator()
        plus_action = menu.addAction("➕ Add 1 day")  # noqa: RUF001
        plus_action.triggered.connect(add_one_day)
        minus_action = menu.addAction("➖ Subtract 1 day")  # noqa: RUF001
        minus_action.triggered.connect(subtract_one_day)

    def refresh_button_text() -> None:
        button.setText(date_quick_button_label(date_edit.date()))

    menu = QMenu(button)
    populate_date_actions(menu)
    button.setMenu(menu)

    def show_context_menu(position: QPoint) -> None:
        line_edit = date_edit.lineEdit()
        context_menu: QMenu = line_edit.createStandardContextMenu() if line_edit is not None else QMenu(date_edit)
        context_menu.addSeparator()
        populate_date_actions(context_menu)
        context_menu.exec_(date_edit.mapToGlobal(position))

    date_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    date_edit.customContextMenuRequested.connect(show_context_menu)
    date_edit.dateChanged.connect(lambda *_args: refresh_button_text())
    refresh_button_text()

    _insert_widget_after(date_edit, button)
    return button


def date_quick_button_label(selected: QDate, *, today: QDate | None = None) -> str:
    """Return the quick-button caption for `selected` relative to `today`.

    - Today → Today
    - Yesterday → Yesterday
    - Any other day → Add + 1

    """
    reference = today if today is not None else QDate.currentDate()
    if selected == reference:
        return "📅 Today"
    if selected == reference.addDays(-1):
        return "📅 Yesterday"
    return "➕ Add + 1"  # noqa: RUF001


def _find_layout_index(widget: QWidget) -> tuple[QLayout, int] | None:
    parent = widget.parentWidget()
    if parent is None:
        return None
    root = parent.layout()
    if root is None:
        return None

    def search(layout: QLayout) -> tuple[QLayout, int] | None:
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item is None:
                continue
            if item.widget() is widget:
                return layout, index
            child = item.layout()
            if child is not None:
                found = search(child)
                if found is not None:
                    return found
        return None

    return search(root)


def _insert_widget_after(anchor: QWidget, new_widget: QWidget) -> None:
    found = _find_layout_index(anchor)
    if found is None:
        parent = anchor.parentWidget()
        if parent is None:
            return
        layout = parent.layout()
        if isinstance(layout, (QHBoxLayout, QVBoxLayout)):
            layout.addWidget(new_widget)
        return
    layout, index = found
    layout.insertWidget(index + 1, new_widget)
