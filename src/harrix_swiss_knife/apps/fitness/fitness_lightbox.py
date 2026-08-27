"""Fitness exercise lightbox: image chrome plus a Quick-style timer column."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QCloseEvent, QColor, QFont, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.apps_config import DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS
from harrix_swiss_knife.apps.common.widgets.exercise_avif_lightbox import ExerciseAvifLightboxDialog
from harrix_swiss_knife.apps.fitness.lightbox_logic import (
    ExerciseStopwatch,
    FitnessLightboxConfirm,
    FitnessLightboxDetails,
    StopwatchColor,
    StopwatchSnapshot,
    allocated_exercise_seconds,
    format_mm_ss,
)
from harrix_swiss_knife.apps.fitness.lightbox_sounds import play_fitness_timer_alert, stop_fitness_timer_alert

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.common.avif_manager import AvifManager
    from harrix_swiss_knife.apps.fitness.database_manager import WorkoutItemRow

_SIDEBAR_MIN_WIDTH = 260
_SIDEBAR_WIDTH = 300
_MIN_IMAGE_EDGE = 2
_TICK_MS = 100
_VALUE_MAXIMUM = 1_000_000

_COLOR_IDLE = "#111827"
_COLOR_COUNTDOWN = "#2563EB"
_COLOR_RUNNING = "#111827"
_COLOR_OVERTIME = "#DC2626"

_PANE_STYLE = """
QFrame#fitnessLightboxPane {
    background: #F8FAFC;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
}
"""

_VALUE_STYLE = """
QSpinBox#fitnessLightboxValueSpin {
    background: #FFFFFF;
    border: 2px solid #D1D5DB;
    border-radius: 16px;
    padding: 8px 16px;
    color: #111827;
}
QSpinBox#fitnessLightboxValueSpin:focus {
    border-color: #3B82F6;
}
"""

_TYPE_STYLE = """
QComboBox#fitnessLightboxTypeCombo {
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
    padding: 8px 32px 8px 12px;
    color: #111827;
    min-height: 28px;
}
QComboBox#fitnessLightboxTypeCombo:focus,
QComboBox#fitnessLightboxTypeCombo:on {
    border-color: #3B82F6;
}
QComboBox#fitnessLightboxTypeCombo::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    background: transparent;
}
QComboBox#fitnessLightboxTypeCombo::down-arrow {
    image: none;
    width: 0;
    height: 0;
}
QComboBox#fitnessLightboxTypeCombo QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    outline: none;
    selection-background-color: #DBEAFE;
    selection-color: #111827;
}
"""

_ADD_BUTTON_STYLE = """
QPushButton#fitnessLightboxAddButton {
    background: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    padding: 16px 32px;
}
QPushButton#fitnessLightboxAddButton:hover {
    background: #2563EB;
}
QPushButton#fitnessLightboxAddButton:pressed {
    background: #1D4ED8;
}
"""

_TIMER_BUTTON_STYLE = """
QPushButton#fitnessLightboxStartButton,
QPushButton#fitnessLightboxPauseButton,
QPushButton#fitnessLightboxRestartButton {
    background: #FFFFFF;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
    padding: 10px 12px;
}
QPushButton#fitnessLightboxStartButton:hover,
QPushButton#fitnessLightboxPauseButton:hover,
QPushButton#fitnessLightboxRestartButton:hover {
    background: #F1F5F9;
    border-color: #3B82F6;
}
"""

DetailsLoader = Callable[[str, int | None], FitnessLightboxDetails]
ConfirmHandler = Callable[[FitnessLightboxConfirm], bool]


class FitnessExerciseLightboxDialog(ExerciseAvifLightboxDialog):
    """Exercise AVIF lightbox with a Quick-style timer and log column."""

    def __init__(
        self,
        exercises: Sequence[str],
        *,
        avif_manager: AvifManager,
        details_loader: DetailsLoader,
        confirm_handler: ConfirmHandler,
        current_index: int = 0,
        parent: QWidget | None = None,
        countdown_seconds: int = DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS,
        workout_items: Sequence[WorkoutItemRow] | None = None,
        workout_duration_min: int | None = None,
    ) -> None:
        """Build the Fitness lightbox.

        Args:

        - `exercises` (`Sequence[str]`): Exercise names in navigation order.
        - `avif_manager` (`AvifManager`): Loader for static and animated AVIF files.
        - `details_loader` (`DetailsLoader`): Loads types, unit, and default value.
        - `confirm_handler` (`ConfirmHandler`): Persists a completed set.
        - `current_index` (`int`): Initial exercise index. Defaults to `0`.
        - `parent` (`QWidget | None`): Widget whose top-level window is covered.
        - `countdown_seconds` (`int`): Ready countdown before the stopwatch.
        - `workout_items` (`Sequence[WorkoutItemRow] | None`): Workout rows when
          opened from a saved workout. `None` is browse mode.
        - `workout_duration_min` (`int | None`): Planned workout length.

        """
        if workout_items is not None:
            workout_items = [item for item in workout_items if item.exercise_name]
            names = [item.exercise_name for item in workout_items]
        else:
            names = list(exercises)
        super().__init__(
            names,
            avif_manager=avif_manager,
            current_index=current_index,
            parent=parent,
            show_speed_slider=True,
            complete_setup=False,
        )
        self._details_loader = details_loader
        self._confirm_handler = confirm_handler
        self._workout_items = list(workout_items) if workout_items is not None else None
        self._open_sets_on_close = False
        item_count = len(self._workout_items) if self._workout_items is not None else 0
        duration = workout_duration_min if workout_duration_min is not None else 0
        self._limit_seconds = (
            allocated_exercise_seconds(duration, item_count) if self._workout_items is not None else None
        )
        self._image_host: QWidget | None = None
        self._splitter: QSplitter | None = None
        self._sidebar = FitnessLightboxSidebar(
            countdown_seconds=countdown_seconds,
            limit_seconds=self._limit_seconds,
            parent=self,
        )
        self._sidebar.confirm_requested.connect(self._on_confirm)
        self._install_sidebar()
        self.finish_setup()

    def chrome_rect(self) -> QRect:
        """Place overlay chrome over the image pane, not the timer column."""
        host = self._image_host
        if host is None:
            return super().chrome_rect()
        return QRect(host.mapTo(self, QPoint(0, 0)), host.size())

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop the timer alert when the overlay is closed."""
        self._sidebar.shutdown()
        super().closeEvent(event)

    def done(self, result: int) -> None:
        """Stop the timer alert when `exec` finishes."""
        self._sidebar.shutdown()
        super().done(result)

    @property
    def should_open_sets_tab(self) -> bool:
        """Whether confirm in browse mode asked to switch to Sets."""
        return self._open_sets_on_close

    def show_item(self, index: int) -> None:
        """Load the exercise image and bind the timer column."""
        self._position_controls()
        super().show_item(index)
        self._bind_sidebar(index)

    def _advance_after_confirm(self) -> None:
        if self._index + 1 < self._item_count:
            self._index += 1
            self._show_current()
            return
        self.accept()

    def _bind_sidebar(self, index: int) -> None:
        if not self._exercises:
            return
        name = self._exercises[index]
        item_id = None
        if self._workout_items is not None and 0 <= index < len(self._workout_items):
            item_id = self._workout_items[index].id
        self._sidebar.bind(name, self._details_loader(name, item_id))

    def _current_confirm(self) -> FitnessLightboxConfirm:
        item_id = None
        if self._workout_items is not None and 0 <= self._index < len(self._workout_items):
            item_id = self._workout_items[self._index].id
        name = self._exercises[self._index] if self._exercises else ""
        return FitnessLightboxConfirm(
            exercise_name=name,
            type_name=self._sidebar.selected_type(),
            value=str(self._sidebar.value()),
            workout_item_id=item_id,
        )

    def _install_sidebar(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setObjectName("fitnessLightboxSplitter")
        splitter.setChildrenCollapsible(False)
        image_host = QWidget(splitter)
        image_host.setObjectName("fitnessLightboxImageHost")
        self._label.setParent(image_host)
        splitter.addWidget(self._sidebar)
        splitter.addWidget(image_host)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([_SIDEBAR_WIDTH, max(self.width() - _SIDEBAR_WIDTH, _SIDEBAR_WIDTH)])
        splitter.splitterMoved.connect(self._on_splitter_moved)
        self._splitter = splitter
        self._image_host = image_host
        self.attach_content(splitter)

    def _on_confirm(self) -> None:
        if not self._confirm_handler(self._current_confirm()):
            return
        if self._workout_items is None:
            self._open_sets_on_close = True
            self.accept()
            return
        self._advance_after_confirm()

    def _on_splitter_moved(self, _pos: int, _index: int) -> None:
        self._position_controls()
        self._schedule_avif_reload()

    def _position_controls(self) -> None:
        super()._position_controls()
        host = self._image_host
        if host is None:
            return
        rect = host.rect()
        if rect.width() < _MIN_IMAGE_EDGE or rect.height() < _MIN_IMAGE_EDGE:
            rect = QRect(0, 0, max(self.width() - _SIDEBAR_WIDTH, 1), max(self.height(), 1))
        self._label.setGeometry(rect)
        self._schedule_avif_reload()


class FitnessLightboxSidebar(QFrame):
    """Quick-style column: stopwatch, exercise name, type, value, confirm."""

    confirm_requested = Signal()

    def __init__(
        self,
        *,
        countdown_seconds: int,
        limit_seconds: int | None,
        parent: QWidget | None = None,
    ) -> None:
        """Build the timer column."""
        super().__init__(parent)
        self.setObjectName("fitnessLightboxPane")
        self.setStyleSheet(_PANE_STYLE)
        self.setMinimumWidth(_SIDEBAR_MIN_WIDTH)
        self._countdown_seconds = max(0, countdown_seconds)
        self._limit_seconds = limit_seconds
        self._stopwatch = ExerciseStopwatch(
            countdown_seconds=self._countdown_seconds,
            limit_seconds=self._limit_seconds,
        )
        self._tick = QTimer(self)
        self._tick.setInterval(_TICK_MS)
        self._tick.timeout.connect(self._on_tick)
        self._build_ui()
        self._apply_snapshot(self._stopwatch.snapshot())

    def bind(self, exercise_name: str, details: FitnessLightboxDetails) -> None:
        """Show `exercise_name` and reset the stopwatch."""
        self._title.setText(exercise_name or "Exercise")
        self._unit_label.setText(details.unit)
        self._unit_label.setVisible(bool(details.unit))
        self._type_combo.blockSignals(True)  # noqa: FBT003
        self._type_combo.clear()
        self._type_combo.addItems(details.types)
        if details.selected_type:
            index = self._type_combo.findText(details.selected_type)
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
        self._type_combo.blockSignals(False)  # noqa: FBT003
        self._type_combo.setVisible(bool(details.types))
        self._value_spin.setValue(details.value)
        self.reset_timer()

    def reset_timer(self) -> None:
        """Stop the clock and return to idle."""
        self._tick.stop()
        stop_fitness_timer_alert()
        self._apply_snapshot(self._stopwatch.reset())

    def selected_type(self) -> str:
        """Return the chosen type, or an empty string."""
        return self._type_combo.currentText().strip()

    def shutdown(self) -> None:
        """Stop ticking and the overtime sound."""
        self._tick.stop()
        stop_fitness_timer_alert()

    def value(self) -> int:
        """Return the numeric set value."""
        return int(self._value_spin.value())

    def _apply_snapshot(self, snapshot: StopwatchSnapshot) -> None:
        self._time_label.setText(format_mm_ss(snapshot.display_seconds))
        color = {
            StopwatchColor.IDLE: _COLOR_IDLE,
            StopwatchColor.COUNTDOWN: _COLOR_COUNTDOWN,
            StopwatchColor.RUNNING: _COLOR_RUNNING,
            StopwatchColor.OVERTIME: _COLOR_OVERTIME,
        }[snapshot.color]
        self._time_label.setStyleSheet(f"color: {color}; background: transparent;")
        if snapshot.is_overtime and snapshot.is_running:
            play_fitness_timer_alert()
        else:
            stop_fitness_timer_alert()
        if self._limit_seconds:
            self._limit_label.setText(f"Slot {format_mm_ss(self._limit_seconds)}")
            self._limit_label.show()
        else:
            self._limit_label.hide()

    def _build_action_button(self) -> QPushButton:
        button = QPushButton("➕ Add")  # noqa: RUF001
        button.setObjectName("fitnessLightboxAddButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumSize(220, 56)
        button.setAutoDefault(False)
        button.setDefault(False)
        _apply_pixel_font(button, pixel_size=20, weight=QFont.Weight.Bold)
        button.clicked.connect(self.confirm_requested.emit)
        return button

    def _build_timer_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoDefault(False)
        button.setDefault(False)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        _apply_pixel_font(button, pixel_size=14, weight=QFont.Weight.DemiBold)
        return button

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)

        self._time_label = QLabel("0:00")
        self._time_label.setObjectName("fitnessLightboxTime")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _apply_pixel_font(self._time_label, pixel_size=56, weight=QFont.Weight.ExtraBold)

        self._limit_label = QLabel("")
        self._limit_label.setObjectName("fitnessLightboxLimit")
        self._limit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._limit_label.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(self._limit_label, pixel_size=14)
        self._limit_label.hide()

        start = self._build_timer_button("▶ Start", "fitnessLightboxStartButton")
        pause = self._build_timer_button("⏸ Pause", "fitnessLightboxPauseButton")
        restart = self._build_timer_button("↻ Restart", "fitnessLightboxRestartButton")
        start.clicked.connect(self._on_start)
        pause.clicked.connect(self._on_pause)
        restart.clicked.connect(self._on_restart)
        controls = QWidget()
        controls.setStyleSheet(_TIMER_BUTTON_STYLE)
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        controls_layout.addWidget(start)
        controls_layout.addWidget(pause)
        controls_layout.addWidget(restart)

        self._title = QLabel("Exercise")
        self._title.setObjectName("fitnessLightboxTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._title.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._title, pixel_size=22, weight=QFont.Weight.ExtraBold)

        self._type_combo = _LightboxTypeCombo()
        self._type_combo.setObjectName("fitnessLightboxTypeCombo")
        self._type_combo.setStyleSheet(_TYPE_STYLE)
        _apply_pixel_font(self._type_combo, pixel_size=16)
        self._type_combo.hide()

        self._value_spin = QSpinBox()
        self._value_spin.setObjectName("fitnessLightboxValueSpin")
        self._value_spin.setRange(0, _VALUE_MAXIMUM)
        self._value_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._value_spin.setMinimumSize(220, 72)
        self._value_spin.setStyleSheet(_VALUE_STYLE)
        _apply_pixel_font(self._value_spin, pixel_size=40, weight=QFont.Weight.ExtraBold)
        self._value_spin.lineEdit().returnPressed.connect(self.confirm_requested.emit)

        self._unit_label = QLabel("")
        self._unit_label.setObjectName("fitnessLightboxUnit")
        self._unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._unit_label.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(self._unit_label, pixel_size=16)
        self._unit_label.hide()

        add_wrap = QWidget()
        add_wrap.setStyleSheet(_ADD_BUTTON_STYLE)
        add_layout = QVBoxLayout(add_wrap)
        add_layout.setContentsMargins(0, 0, 0, 0)
        add_layout.addWidget(self._build_action_button(), 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(self._time_label)
        layout.addWidget(self._limit_label)
        layout.addWidget(controls)
        layout.addSpacing(8)
        layout.addWidget(self._title)
        layout.addStretch(2)
        layout.addWidget(self._type_combo)
        layout.addWidget(self._value_spin, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._unit_label)
        layout.addWidget(add_wrap, 0, Qt.AlignmentFlag.AlignHCenter)

    def _on_pause(self) -> None:
        self._tick.stop()
        self._apply_snapshot(self._stopwatch.pause())

    def _on_restart(self) -> None:
        self._tick.start()
        self._apply_snapshot(self._stopwatch.restart())

    def _on_start(self) -> None:
        self._tick.start()
        self._apply_snapshot(self._stopwatch.start())

    def _on_tick(self) -> None:
        self._apply_snapshot(self._stopwatch.advance(_TICK_MS))


class _LightboxTypeCombo(QComboBox):
    """QComboBox that paints a flat chevron instead of the native 3D arrow."""

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
