"""Fitness dashboard for quick set logging from an exercise list."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPaintEvent, QPen, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.delegates.name_local_list_delegate import (
    NAME_LOCAL_ROLE,
    NameLocalLayout,
    NameLocalListDelegate,
)
from harrix_swiss_knife.apps.fitness.exercise_favorites import format_favorite_exercise_label

if TYPE_CHECKING:
    from PySide6.QtCore import QPersistentModelIndex
    from PySide6.QtWidgets import QStyleOptionViewItem

_DASHBOARD_ICON_SIZE = 96
_DASHBOARD_LOCAL_FONT_SCALE = 0.9
_DASHBOARD_NAME_PIXEL_SIZE = 22
_DASHBOARD_SEPARATOR = QColor("#D1D5DB")
_VALUE_MAXIMUM = 1_000_000

_PANE_STYLE = """
QFrame#fitnessDashPane {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
}
"""

_LIST_STYLE = """
QListView#fitnessDashExerciseList {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 6px;
    outline: none;
}
QListView#fitnessDashExerciseList::item {
    border-radius: 12px;
    padding: 4px;
    min-height: 108px;
}
QListView#fitnessDashExerciseList::item:hover {
    background: #F1F5F9;
}
QListView#fitnessDashExerciseList::item:selected {
    background: #DBEAFE;
}
"""

_VALUE_STYLE = """
QSpinBox#fitnessDashValueSpin {
    background: #FFFFFF;
    border: 2px solid #D1D5DB;
    border-radius: 16px;
    padding: 8px 16px;
    color: #111827;
}
QSpinBox#fitnessDashValueSpin:focus {
    border-color: #3B82F6;
}
"""

_TYPE_STYLE = """
QComboBox#fitnessDashTypeCombo {
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
    padding: 8px 32px 8px 12px;
    color: #111827;
    min-height: 28px;
}
QComboBox#fitnessDashTypeCombo:focus,
QComboBox#fitnessDashTypeCombo:on {
    border-color: #3B82F6;
}
QComboBox#fitnessDashTypeCombo::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    background: transparent;
}
QComboBox#fitnessDashTypeCombo::down-arrow {
    image: none;
    width: 0;
    height: 0;
}
QComboBox#fitnessDashTypeCombo QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    outline: none;
    selection-background-color: #DBEAFE;
    selection-color: #111827;
}
"""

_ADD_BUTTON_STYLE = """
QPushButton#fitnessDashAddButton,
QPushButton#fitnessDashAddVoiceButton,
QPushButton#fitnessDashAddTextButton {
    background: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    padding: 16px 32px;
}
QPushButton#fitnessDashAddButton:hover,
QPushButton#fitnessDashAddVoiceButton:hover,
QPushButton#fitnessDashAddTextButton:hover {
    background: #2563EB;
}
QPushButton#fitnessDashAddButton:pressed,
QPushButton#fitnessDashAddVoiceButton:pressed,
QPushButton#fitnessDashAddTextButton:pressed {
    background: #1D4ED8;
}
"""


@dataclass(frozen=True)
class FitnessDashboardExercise:
    """One exercise row on the Fitness dashboard list."""

    name: str
    name_local: str = ""
    icon: QIcon | None = None
    is_favorite: bool = False
    is_dumbbell: bool = False


class FitnessDashboardWidget(QWidget):
    """Quick-add card: exercise list, large value field, and today's sets."""

    add_requested = Signal()
    add_text_requested = Signal()
    add_voice_requested = Signal()
    exercise_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("FitnessDashboardWidget { background: #FFFFFF; }")
        self._model = QStandardItemModel(self)
        self._build_ui()

    @property
    def exercise_list(self) -> QListView:
        """Return the dashboard exercise list view."""
        return self._list

    def focus_value(self) -> None:
        """Move keyboard focus to the value field and select its text."""
        self._value_spin.setFocus()
        self._value_spin.selectAll()

    @property
    def icon_size(self) -> int:
        """Return the list icon edge in pixels."""
        return _DASHBOARD_ICON_SIZE

    def selected_exercise(self) -> str:
        """Return the selected exercise name, or an empty string."""
        index = self._list.currentIndex()
        if not index.isValid():
            return ""
        name = index.data(Qt.ItemDataRole.UserRole)
        return str(name) if name else ""

    def selected_type(self) -> str:
        """Return the selected exercise type, or an empty string."""
        return self._type_combo.currentText().strip()

    def set_exercises(
        self,
        items: list[FitnessDashboardExercise],
        *,
        selected: str | None = None,
    ) -> None:
        """Replace the exercise list and optionally restore a selection.

        Args:

        - `items` (`list[FitnessDashboardExercise]`): Exercises to show.
        - `selected` (`str | None`): Exercise name to keep selected.

        """
        previous = selected if selected is not None else self.selected_exercise()
        self._list.blockSignals(True)  # noqa: FBT003
        self._model.clear()
        selected_row = 0
        name_font = self._list.font()
        for row, item in enumerate(items):
            row_item = QStandardItem(
                format_favorite_exercise_label(
                    item.name,
                    favorite=item.is_favorite,
                    dumbbell=item.is_dumbbell,
                )
            )
            if item.icon is not None and not item.icon.isNull():
                row_item.setIcon(item.icon)
            row_item.setFont(name_font)
            row_item.setEditable(False)
            row_item.setData(item.name, Qt.ItemDataRole.UserRole)
            if item.name_local.strip():
                row_item.setData(item.name_local.strip(), NAME_LOCAL_ROLE)
            row_item.setSizeHint(QSize(0, _DASHBOARD_ICON_SIZE + 16))
            self._model.appendRow(row_item)
            if previous and item.name == previous:
                selected_row = row
        if self._model.rowCount() > 0:
            self._list.setCurrentIndex(self._model.index(selected_row, 0))
        self._list.blockSignals(False)  # noqa: FBT003
        self._on_exercise_index_changed(self._list.currentIndex())

    def set_today_sets(self, count: int) -> None:
        """Update the large sets figure shown under the add controls.

        Args:

        - `count` (`int`): Number of process records logged today.

        """
        self._sets_value.setText(format_today_sets(count))

    def set_types(self, types: list[str], *, selected: str = "") -> None:
        """Fill the type combo and show it only when types exist.

        Args:

        - `types` (`list[str]`): Type names for the selected exercise.
        - `selected` (`str`): Type to preselect when present.

        """
        self._type_combo.blockSignals(True)  # noqa: FBT003
        self._type_combo.clear()
        self._type_combo.addItem("")
        self._type_combo.addItems(types)
        if selected:
            index = self._type_combo.findText(selected)
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
        self._type_combo.blockSignals(False)  # noqa: FBT003
        self._type_combo.setVisible(bool(types))

    def set_unit(self, unit: str) -> None:
        """Show the unit of the selected exercise under the value field.

        Args:

        - `unit` (`str`): Unit of measurement, or empty when nothing is selected.

        """
        text = unit.strip()
        self._unit_label.setText(text)
        self._unit_label.setVisible(bool(text))

    def set_value(self, value: int) -> None:
        """Set the numeric value used for the next set.

        Args:

        - `value` (`int`): Count, weight, or other exercise quantity.

        """
        self._value_spin.setValue(max(0, min(value, _VALUE_MAXIMUM)))

    def update_exercise_icon(self, name: str, icon: QIcon | None) -> None:
        """Replace the icon for one exercise already in the list.

        Args:

        - `name` (`str`): Exercise name stored in `UserRole`.
        - `icon` (`QIcon | None`): New icon, or `None` to clear it.

        """
        for row in range(self._model.rowCount()):
            row_item = self._model.item(row)
            if row_item is None or row_item.data(Qt.ItemDataRole.UserRole) != name:
                continue
            row_item.setIcon(icon if icon is not None else QIcon())
            return

    def value(self) -> int:
        """Return the numeric value entered for the next set."""
        return int(self._value_spin.value())

    def _build_action_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumSize(280, 56)
        _apply_pixel_font(button, pixel_size=20, weight=QFont.Weight.Bold)
        return button

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        pane = QFrame()
        pane.setObjectName("fitnessDashPane")
        pane.setStyleSheet(_PANE_STYLE)
        row = QHBoxLayout(pane)
        row.setContentsMargins(16, 16, 16, 16)
        row.setSpacing(24)

        self._list = QListView()
        self._list.setObjectName("fitnessDashExerciseList")
        self._list.setModel(self._model)
        self._list.setIconSize(QSize(_DASHBOARD_ICON_SIZE, _DASHBOARD_ICON_SIZE))
        self._list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self._list.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self._list.setUniformItemSizes(True)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.setMinimumWidth(320)
        self._list.setStyleSheet(_LIST_STYLE)
        _apply_pixel_font(self._list, pixel_size=_DASHBOARD_NAME_PIXEL_SIZE)
        self._list.setItemDelegate(
            _DashboardExerciseDelegate(
                self._list,
                layout=NameLocalLayout.LIST,
                local_font_scale=_DASHBOARD_LOCAL_FONT_SCALE,
            )
        )
        self._list.selectionModel().currentChanged.connect(self._on_exercise_index_changed)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(8, 8, 8, 8)
        center_layout.setSpacing(12)

        self._exercise_title = QLabel("Select an exercise")
        self._exercise_title.setObjectName("fitnessDashExerciseTitle")
        self._exercise_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._exercise_title.setWordWrap(True)
        self._exercise_title.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._exercise_title, pixel_size=24, weight=QFont.Weight.ExtraBold)

        self._value_spin = QSpinBox()
        self._value_spin.setObjectName("fitnessDashValueSpin")
        self._value_spin.setRange(0, _VALUE_MAXIMUM)
        self._value_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._value_spin.setMinimumSize(280, 88)
        self._value_spin.setStyleSheet(_VALUE_STYLE)
        _apply_pixel_font(self._value_spin, pixel_size=48, weight=QFont.Weight.ExtraBold)
        self._value_spin.lineEdit().returnPressed.connect(self.add_requested.emit)

        self._unit_label = QLabel("")
        self._unit_label.setObjectName("fitnessDashUnitLabel")
        self._unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._unit_label.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(self._unit_label, pixel_size=16)
        self._unit_label.hide()

        self._type_combo = _DashboardTypeCombo()
        self._type_combo.setObjectName("fitnessDashTypeCombo")
        self._type_combo.setMinimumWidth(280)
        self._type_combo.setStyleSheet(_TYPE_STYLE)
        _apply_pixel_font(self._type_combo, pixel_size=16)
        self._type_combo.hide()

        add_button = self._build_action_button("➕ Add", "fitnessDashAddButton")  # noqa: RUF001
        voice_button = self._build_action_button("🎙️ Speak", "fitnessDashAddVoiceButton")
        text_button = self._build_action_button("📝 Write text", "fitnessDashAddTextButton")
        add_button.clicked.connect(self.add_requested.emit)
        voice_button.clicked.connect(self.add_voice_requested.emit)
        text_button.clicked.connect(self.add_text_requested.emit)

        self._sets_value = QLabel("0")
        self._sets_value.setObjectName("fitnessDashSetsValue")
        self._sets_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sets_value.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._sets_value, pixel_size=64, weight=QFont.Weight.ExtraBold)

        sets_hint = QLabel("sets today")
        sets_hint.setObjectName("fitnessDashSetsHint")
        sets_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sets_hint.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(sets_hint, pixel_size=20, weight=QFont.Weight.DemiBold)

        center_layout.addStretch(1)
        center_layout.addWidget(self._exercise_title)
        center_layout.addWidget(self._value_spin, 0, Qt.AlignmentFlag.AlignHCenter)
        center_layout.addWidget(self._unit_label)
        center_layout.addWidget(self._type_combo, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons = QWidget()
        buttons.setStyleSheet(_ADD_BUTTON_STYLE)
        buttons_layout = QVBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)
        buttons_layout.addWidget(add_button, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons_layout.addWidget(voice_button, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons_layout.addWidget(text_button, 0, Qt.AlignmentFlag.AlignHCenter)
        center_layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignHCenter)
        center_layout.addStretch(1)
        center_layout.addWidget(self._sets_value)
        center_layout.addWidget(sets_hint)

        row.addWidget(self._list, 2)
        row.addWidget(center, 3)
        outer.addWidget(pane)

    def _on_exercise_index_changed(self, current: QModelIndex, _previous: QModelIndex | None = None) -> None:
        name = ""
        if current.isValid():
            value = current.data(Qt.ItemDataRole.UserRole)
            name = str(value) if value else ""
        self._exercise_title.setText(name or "Select an exercise")
        self.exercise_changed.emit(name)


class _DashboardExerciseDelegate(NameLocalListDelegate):
    """Exercise-list delegate that draws a gray line between rows."""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the row, then a gray divider under every item except the last."""
        super().paint(painter, option, index)
        model = index.model()
        if model is None or index.row() >= model.rowCount() - 1:
            return
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)  # noqa: FBT003
        painter.setPen(QPen(_DASHBOARD_SEPARATOR, 1))
        y = option.rect.bottom()
        painter.drawLine(option.rect.left() + 8, y, option.rect.right() - 8, y)
        painter.restore()


class _DashboardTypeCombo(QComboBox):
    """QComboBox that paints a flat chevron instead of the native 3D arrow button."""

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Draw the combo, then a simple down arrow on the right."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(
            QPen(
                QColor("#6B7280"),
                1.8,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        center_x = self.rect().right() - 16
        center_y = self.rect().center().y()
        painter.drawPolyline(
            [
                QPoint(center_x - 5, center_y - 2),
                QPoint(center_x, center_y + 3),
                QPoint(center_x + 5, center_y - 2),
            ]
        )


def format_today_sets(count: int) -> str:
    """Format today's set count for the large dashboard number.

    Args:

    - `count` (`int`): Number of process records logged today.

    Returns:

    - `str`: Compact integer text without a unit suffix.

    """
    return str(max(0, int(count)))


def _apply_pixel_font(
    widget: QWidget,
    *,
    pixel_size: int,
    weight: QFont.Weight = QFont.Weight.Normal,
) -> None:
    font = widget.font()
    font.setPixelSize(pixel_size)
    font.setWeight(weight)
    widget.setFont(font)
