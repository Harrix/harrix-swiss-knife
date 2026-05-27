"""Delegate for boolean habit cells in the process habits pivot table."""

from __future__ import annotations

from typing import Literal

from PySide6.QtCore import (
    QAbstractItemModel,
    QEvent,
    QLocale,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QRect,
    QSize,
    Qt,
)
from PySide6.QtGui import QMouseEvent, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionButton,
    QStyleOptionViewItem,
    QWidget,
)

ProcessHabitBoolState = Literal["absent", "checked", "unchecked"]
_DualPick = Literal["checked", "unchecked"]

_TRUTHY_VALUES = frozenset({"1", "true", "yes"})
_FALSY_VALUES = frozenset({"0", "false", "no"})
_DUAL_CHECKBOX_GAP = 6


class ProcessHabitBoolDelegate(QStyledItemDelegate):
    """Paint checkboxes; hover picker for empty cells, toggle for existing values."""

    def __init__(self, parent: QAbstractItemView | None = None) -> None:
        """Enable mouse tracking on the table view for hover picker UI."""
        super().__init__(parent)
        self._hover_index: QPersistentModelIndex | None = None
        if parent is not None:
            parent.setMouseTracking(True)
            parent.viewport().installEventFilter(self)

    def displayText(self, _value: object, _locale: QLocale | QLocale.Language) -> str:  # noqa: N802
        """Hide stored 0/1 text; checkbox is drawn in paint()."""
        return ""

    def editorEvent(  # noqa: N802
        self,
        event: QEvent,
        model: QAbstractItemModel,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Set value on click: dual-picker for absent cells, toggle otherwise."""
        if event.type() != QEvent.Type.MouseButtonRelease:
            return False
        mouse_event = event
        if not isinstance(mouse_event, QMouseEvent):
            return False
        if mouse_event.button() != Qt.MouseButton.LeftButton:
            return False

        state = cell_state_from_index(index)
        if state == "absent":
            if not _is_same_cell(index, self._hover_index):
                return False
            pick = _pick_dual_checkbox(option, index, mouse_event)
            if pick is None:
                return False
            new_value = "1" if pick == "checked" else "0"
            return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

        new_value = next_value_for_toggle(state)
        return model.setData(index, new_value, Qt.ItemDataRole.EditRole)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track hovered absent cell to show dual-checkbox picker."""
        view = self.parent()
        if not isinstance(view, QAbstractItemView) or watched is not view.viewport():
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.MouseMove:
            mouse_event = event
            if isinstance(mouse_event, QMouseEvent):
                idx = view.indexAt(mouse_event.position().toPoint())
                new_hover: QPersistentModelIndex | None = None
                if idx.isValid() and view.itemDelegate(idx) is self and cell_state_from_index(idx) == "absent":
                    new_hover = QPersistentModelIndex(idx)
                if not _persistent_index_equals(self._hover_index, new_hover):
                    self._hover_index = new_hover
                    view.viewport().update()
        elif event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
            if self._hover_index is not None:
                self._hover_index = None
                view.viewport().update()

        return super().eventFilter(watched, event)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw row background; draw checkbox(es) for stored or pending values."""
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget is not None else QApplication.style()

        # Fill cell background (row color from model)
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        state = cell_state_from_index(index)
        if state == "absent":
            if _is_same_cell(index, self._hover_index):
                _paint_dual_checkboxes(painter, option, style)
            return

        check_option = QStyleOptionButton()
        check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        if state == "checked":
            check_option.state |= QStyle.StateFlag.State_On
        else:
            check_option.state |= QStyle.StateFlag.State_Off

        indicator_rect = style.subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator,
            check_option,
            option.widget,
        )
        check_option.rect = _center_rect(option.rect, indicator_rect.size())
        style.drawControl(QStyle.ControlElement.CE_CheckBox, check_option, painter, option.widget)


def cell_state_from_index(index: QModelIndex | QPersistentModelIndex) -> ProcessHabitBoolState:
    """Return visual state for a boolean process-habit cell."""
    stored = index.data(Qt.ItemDataRole.UserRole)
    record_id = stored[0] if stored else None
    display = index.data(Qt.ItemDataRole.DisplayRole)
    return parse_process_habit_bool(display, record_id)


def next_value_for_toggle(current: ProcessHabitBoolState) -> str:
    """Return the model string value after a click on the cell."""
    if current == "absent":
        return "1"
    if current == "checked":
        return "0"
    return "1"


def parse_process_habit_bool(value: object, record_id: object) -> ProcessHabitBoolState:
    """Map model storage to absent / checked / unchecked.

    Args:

    - `value` (`object`): Display/edit value from the model.
    - `record_id` (`object`): First element of UserRole tuple, or None if no DB row.

    Returns:

    - `ProcessHabitBoolState`: Cell visual state.

    """
    text = str(value).strip().lower() if value is not None else ""
    if record_id is None:
        if not text:
            return "absent"
        if text in _TRUTHY_VALUES:
            return "checked"
        if text in _FALSY_VALUES:
            return "unchecked"
        return "absent"
    if text in _TRUTHY_VALUES:
        return "checked"
    return "unchecked"


def _center_rect(outer: QRect, size: QSize) -> QRect:
    """Center a rectangle of given size inside outer."""
    x = outer.x() + (outer.width() - size.width()) // 2
    y = outer.y() + (outer.height() - size.height()) // 2
    return QRect(x, y, size.width(), size.height())


def _checkbox_indicator_size(style: QStyle, widget: QWidget | None) -> QSize:
    check_option = QStyleOptionButton()
    check_option.state = QStyle.StateFlag.State_Enabled
    return style.subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, check_option, widget).size()


def _dual_checkbox_rects(outer: QRect, indicator_size: QSize) -> tuple[QRect, QRect]:
    """Return (unchecked_rect, checked_rect) centered in outer."""
    total_w = indicator_size.width() * 2 + _DUAL_CHECKBOX_GAP
    start_x = outer.x() + (outer.width() - total_w) // 2
    y = outer.y() + (outer.height() - indicator_size.height()) // 2
    unchecked = QRect(start_x, y, indicator_size.width(), indicator_size.height())
    checked = QRect(
        start_x + indicator_size.width() + _DUAL_CHECKBOX_GAP,
        y,
        indicator_size.width(),
        indicator_size.height(),
    )
    return unchecked, checked


def _is_same_cell(
    left: QModelIndex | QPersistentModelIndex | None,
    right: QModelIndex | QPersistentModelIndex | None,
) -> bool:
    if left is None or right is None:
        return False
    if not left.isValid() or not right.isValid():
        return False
    return left.row() == right.row() and left.column() == right.column() and left.model() is right.model()


def _paint_checkbox(
    painter: QPainter,
    rect: QRect,
    *,
    checked: bool,
    style: QStyle,
    widget: QWidget | None,
) -> None:
    check_option = QStyleOptionButton()
    check_option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
    if checked:
        check_option.state |= QStyle.StateFlag.State_On
    else:
        check_option.state |= QStyle.StateFlag.State_Off
    check_option.rect = rect
    style.drawControl(QStyle.ControlElement.CE_CheckBox, check_option, painter, widget)


def _paint_dual_checkboxes(painter: QPainter, option: QStyleOptionViewItem, style: QStyle) -> None:
    indicator_size = _checkbox_indicator_size(style, option.widget)
    unchecked_rect, checked_rect = _dual_checkbox_rects(option.rect, indicator_size)
    _paint_checkbox(painter, unchecked_rect, checked=False, style=style, widget=option.widget)
    _paint_checkbox(painter, checked_rect, checked=True, style=style, widget=option.widget)


def _persistent_index_equals(
    left: QPersistentModelIndex | None,
    right: QPersistentModelIndex | None,
) -> bool:
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return left == right


def _pick_dual_checkbox(
    option: QStyleOptionViewItem,
    index: QModelIndex | QPersistentModelIndex,
    mouse_event: QMouseEvent,
) -> _DualPick | None:
    view = option.widget
    if view is None:
        return None
    pos = mouse_event.position().toPoint()
    cell_rect = view.visualRect(index)
    if not cell_rect.contains(pos):
        return None

    local = pos - cell_rect.topLeft()
    local_rect = QRect(0, 0, cell_rect.width(), cell_rect.height())
    style = view.style() if view is not None else QApplication.style()
    indicator_size = _checkbox_indicator_size(style, view)
    unchecked_rect, checked_rect = _dual_checkbox_rects(local_rect, indicator_size)

    if checked_rect.contains(local):
        return "checked"
    if unchecked_rect.contains(local):
        return "unchecked"
    return None
