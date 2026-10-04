"""Date-edit helpers: field chrome, shared calendar popup, control heights."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDateEdit, QLabel, QLineEdit, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import SELECTION_BORDER
from harrix_swiss_knife.qt_date_calendar import apply_date_calendar_popup, show_date_calendar_popup
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon

if TYPE_CHECKING:
    from collections.abc import Iterable

    from PySide6.QtWidgets import QLayout

_MIN_CONTROL_HEIGHT = 24
_DATE_FIELD_MIN_HEIGHT = 28
_DATE_FIELD_ICON_SIZE = 16
_PROP_FIELD_CHROME = "hskDateEditFieldChrome"


def attach_date_edit_quick_controls(date_edit: QDateEdit) -> None:
    """Apply calendar popup, leading calendar icon, and toolbar field height.

    Quick presets (Yesterday, Today, ±1 day) live in the calendar footer, not
    next to the field. The date field itself gets a Lucide calendar glyph on
    the left and a height close to the former quick-button row.

    Args:

    - `date_edit` (`QDateEdit`): Existing date field from the UI.

    """
    apply_date_calendar_popup(date_edit)
    _apply_date_edit_field_chrome(date_edit)


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


def _apply_date_edit_field_chrome(date_edit: QDateEdit) -> None:
    if date_edit.property(_PROP_FIELD_CHROME) is True:
        return
    line_edit = date_edit.lineEdit()
    if line_edit is not None:
        action = QAction(line_edit)
        action.setObjectName("hskDateEditCalendarIcon")
        action.setIcon(create_lucide_icon("calendar", _DATE_FIELD_ICON_SIZE, color=SELECTION_BORDER))
        action.setToolTip("Open calendar")
        action.triggered.connect(lambda: show_date_calendar_popup(date_edit))
        line_edit.addAction(action, QLineEdit.ActionPosition.LeadingPosition)
    height = max(date_edit.sizeHint().height(), date_edit.minimumHeight(), _DATE_FIELD_MIN_HEIGHT)
    date_edit.setMinimumHeight(height)
    date_edit.setProperty(_PROP_FIELD_CHROME, True)  # noqa: FBT003
