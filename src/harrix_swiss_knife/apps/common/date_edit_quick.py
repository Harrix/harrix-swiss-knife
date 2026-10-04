"""Date edit with a quick preset / offset split menu button."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QPoint, QSize, Qt
from PySide6.QtWidgets import QDateEdit, QHBoxLayout, QLabel, QMenu, QVBoxLayout, QWidget

from harrix_swiss_knife.qt_date_calendar import apply_date_calendar_popup
from harrix_swiss_knife.qt_lucide_icon import add_lucide_action, apply_leading_chrome_button_icon
from harrix_swiss_knife.qt_split_menu_button import SplitMenuButton

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from PySide6.QtWidgets import QLayout

_MIN_CONTROL_HEIGHT = 24


def attach_date_edit_quick_controls(
    date_edit: QDateEdit,
    *,
    button_object_name: str | None = None,
) -> SplitMenuButton:
    """Replace a bare `QDateEdit` with date field + split quick button.

    Inserts a split menu button after `date_edit` in its parent layout. The main
    zone runs the caption action (Today / Yesterday / Add + 1); the arrow opens
    the full Today / Yesterday / ±1 day menu. The same actions are also added to
    the date field context menu. The date field height is matched to the button.

    Args:

    - `date_edit` (`QDateEdit`): Existing date field from the UI.
    - `button_object_name` (`str | None`): Object name for the new button.
      Defaults to `{dateEditObjectName}_quick`.

    Returns:

    - `SplitMenuButton`: The created quick-controls button.

    """
    button = SplitMenuButton(date_edit.parentWidget())
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
        today_action = add_lucide_action(menu, "Today's date", "calendar")
        today_action.triggered.connect(set_today)
        yesterday_action = add_lucide_action(menu, "Yesterday", "calendar")
        yesterday_action.triggered.connect(set_yesterday)
        menu.addSeparator()
        plus_action = add_lucide_action(menu, "Add 1 day", "plus")
        plus_action.triggered.connect(add_one_day)
        minus_action = add_lucide_action(menu, "Subtract 1 day", "minus")
        minus_action.triggered.connect(subtract_one_day)

    def primary_action() -> Callable[[], None]:
        return date_quick_primary_action(
            date_edit.date(),
            set_today=set_today,
            set_yesterday=set_yesterday,
            add_one_day=add_one_day,
        )

    def refresh_button_text() -> None:
        button.setText(date_quick_button_label(date_edit.date()))
        apply_leading_chrome_button_icon(button.main_button)
        match_control_heights(date_edit, button)

    menu = QMenu(button)
    populate_date_actions(menu)
    button.setMenu(menu)

    def on_primary_clicked() -> None:
        primary_action()()

    button.clicked.connect(on_primary_clicked)

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
    apply_date_calendar_popup(date_edit)

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


def date_quick_primary_action(
    selected: QDate,
    *,
    set_today: Callable[[], None],
    set_yesterday: Callable[[], None],
    add_one_day: Callable[[], None],
    today: QDate | None = None,
) -> Callable[[], None]:
    """Return the main-zone callback matching `date_quick_button_label`."""
    reference = today if today is not None else QDate.currentDate()
    if selected == reference:
        return set_today
    if selected == reference.addDays(-1):
        return set_yesterday
    return add_one_day


def match_control_heights(*widgets: QWidget | None) -> int:
    """Make every widget share the tallest size-hint height in the group.

    Labels are vertically centered so text sits on the same baseline row as
    buttons and date fields.

    Args:

    - `widgets` (`QWidget | None`): Controls in one toolbar/filter row.

    Returns:

    - `int`: Applied height, or `0` when no widgets were given.

    """
    visible = [widget for widget in widgets if widget is not None]
    if not visible:
        return 0
    height = max(
        _MIN_CONTROL_HEIGHT,
        *(max(widget.sizeHint().height(), widget.minimumHeight()) for widget in visible),
    )
    for widget in visible:
        widget.setMinimumHeight(height)
        widget.setMaximumHeight(height)
        if isinstance(widget, QLabel):
            widget.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    return height


def match_layout_control_heights(layout: QLayout | None) -> int:
    """Match heights of every widget inside a horizontal toolbar layout."""
    if layout is None:
        return 0
    widgets: list[QWidget] = []
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is None:
            continue
        widget = item.widget()
        if isinstance(widget, QWidget):
            widgets.append(widget)
    return match_control_heights(*widgets)


def match_layout_control_heights_many(layouts: Iterable[QLayout | None]) -> None:
    """Apply `match_layout_control_heights` to each layout."""
    for layout in layouts:
        match_layout_control_heights(layout)


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
