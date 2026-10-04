"""Date-edit helpers: shared calendar popup and matching control heights."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDateEdit, QLabel, QWidget

from harrix_swiss_knife.qt_date_calendar import apply_date_calendar_popup

if TYPE_CHECKING:
    from collections.abc import Iterable

    from PySide6.QtWidgets import QLayout

_MIN_CONTROL_HEIGHT = 24


def attach_date_edit_quick_controls(date_edit: QDateEdit) -> None:
    """Apply the shared calendar popup to `date_edit`.

    Quick presets (Yesterday, Today, ±1 day) live in the calendar footer, not
    next to the field.

    Args:

    - `date_edit` (`QDateEdit`): Existing date field from the UI.

    """
    apply_date_calendar_popup(date_edit)


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
