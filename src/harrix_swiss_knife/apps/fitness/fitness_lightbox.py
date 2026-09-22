"""Fitness exercise lightbox: image chrome plus a Quick-style timer column."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import (
    QCloseEvent,
    QColor,
    QFont,
    QFontMetrics,
    QKeySequence,
    QPainter,
    QPaintEvent,
    QPen,
    QShortcut,
    QShowEvent,
)
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QStyle,
    QStyleOptionComboBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.apps_config import DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS
from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey
from harrix_swiss_knife.apps.common.delegates.name_local_list_delegate import (
    NAME_LOCAL_ROLE,
    NameLocalLayout,
    NameLocalListDelegate,
)
from harrix_swiss_knife.apps.common.widgets.exercise_avif_lightbox import ExerciseAvifLightboxDialog
from harrix_swiss_knife.apps.fitness.lightbox_logic import (
    ExerciseStopwatch,
    ExerciseStopwatchState,
    FitnessLightboxConfirm,
    FitnessLightboxDetails,
    LightboxOverlayKind,
    LightboxPlaybackView,
    StopwatchColor,
    StopwatchPhase,
    StopwatchSnapshot,
    allocated_exercise_seconds,
    format_mm_ss,
    is_seconds_exercise_unit,
    lightbox_playback_view,
    minutes_seconds_to_total,
    split_total_seconds,
    target_seconds_for_exercise,
)
from harrix_swiss_knife.apps.fitness.lightbox_sounds import (
    FitnessTimerCue,
    play_fitness_timer_cue,
    stop_fitness_timer_alert,
)
from harrix_swiss_knife.qt_compact_spin_box import CompactSpinBox as QSpinBox
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon
from harrix_swiss_knife.qt_toolbar_style import (
    TOOLBAR_BORDER_RADIUS,
    TOOLBAR_BUTTON_GAP,
    TOOLBAR_BUTTON_SIZE,
    TOOLBAR_ICON_SIZE,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.common.avif_manager import AvifManager
    from harrix_swiss_knife.apps.fitness.database_manager import WorkoutItemRow

_SIDEBAR_MIN_WIDTH = 260
_SIDEBAR_WIDTH = 300
_SPLITTER_PANE_COUNT = 2
_MIN_IMAGE_EDGE = 2
_TICK_MS = 100
_COUNTDOWN_VOICE_CUES: dict[int, FitnessTimerCue] = {3: "3", 2: "2", 1: "1"}
_VALUE_MAXIMUM = 1_000_000
_DURATION_SPIN_WIDTH = 118
_DURATION_SPIN_HEIGHT = 72
_TYPE_COMBO_SINGLE_HEIGHT = 40
_TYPE_COMBO_DOUBLE_HEIGHT = 56
_NAME_LOCAL_COLOR = QColor("#888888")

_COLOR_IDLE = "#111827"
_COLOR_COUNTDOWN = "#2563EB"
_COLOR_RUNNING = "#111827"
_COLOR_OVERTIME = "#DC2626"
_COLOR_FINISHED = "#16A34A"
_COLOR_IDLE_ON_DARK = "#F9FAFB"
_COLOR_RUNNING_ON_DARK = "#F9FAFB"
_COLOR_MUTED = "#6B7280"
_COLOR_MUTED_ON_DARK = "#9CA3AF"
_COLOR_TITLE = "#111827"
_COLOR_TITLE_ON_DARK = "#F9FAFB"
_SPLITTER_HOVER = "#9CA3AF"
_TIMER_BUTTON_ICON_ACTIVE = "#122A3A"
_TIMER_BUTTON_ICON_ON_FILLED = "#F9FAFB"
_TIMER_BUTTON_ICON_DISABLED = "#C4C4C8"
_TIMER_ROLE_START = "start"
_TIMER_ROLE_STOP = "stop"


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
        auto_start_prepare: bool = False,
        initial_timer_state: ExerciseStopwatchState | None = None,
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
        - `auto_start_prepare` (`bool`): Start the Prepare countdown when each
          exercise is shown. Defaults to `False`.
        - `initial_timer_state` (`ExerciseStopwatchState | None`): Resume the
          stopwatch for the first shown workout item instead of restarting.

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
        self._auto_start_prepare = auto_start_prepare
        self._pending_timer_state = initial_timer_state
        self._captured_timer_item_id: int | None = None
        self._captured_timer_state: ExerciseStopwatchState | None = None
        item_count = len(self._workout_items) if self._workout_items is not None else 0
        duration = workout_duration_min if workout_duration_min is not None else 0
        self._limit_seconds = (
            allocated_exercise_seconds(duration, item_count) if self._workout_items is not None else None
        )
        self._image_host: QWidget | None = None
        self._phase_overlay: LightboxPhaseOverlay | None = None
        self._splitter: QSplitter | None = None
        self._sidebar = FitnessLightboxSidebar(
            countdown_seconds=countdown_seconds,
            limit_seconds=self._limit_seconds,
            parent=self,
        )
        self._sidebar.confirm_requested.connect(self._on_confirm)
        self._sidebar.playback_changed.connect(self._apply_playback_view)
        self._last_playback_view: LightboxPlaybackView | None = None
        self._timer_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self._timer_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._timer_shortcut.activated.connect(self._sidebar.toggle_timer)
        self._install_sidebar()
        self._sync_fitness_chrome_backdrop()
        self.finish_setup()

    def captured_timer_state(self) -> tuple[int | None, ExerciseStopwatchState | None]:
        """Return the workout item ID and stopwatch state captured on close."""
        return self._captured_timer_item_id, self._captured_timer_state

    def chrome_rect(self) -> QRect:
        """Place overlay chrome over the image pane, not the timer column.

        Uses the dialog size and sidebar width so arrows and captions are
        not piled at the origin while the splitter is still laying out.

        """
        return self._image_pane_rect()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Capture the exercise timer, then stop alerts when the overlay closes."""
        self._capture_timer_before_close()
        self._sidebar.shutdown()
        super().closeEvent(event)

    def done(self, result: int) -> None:
        """Capture the exercise timer, then stop alerts when `exec` finishes."""
        self._capture_timer_before_close()
        self._sidebar.shutdown()
        super().done(result)

    def exercise_timer_config(self) -> tuple[int, int | None, bool]:
        """Return countdown, limit, and stop-at-limit used by the sidebar stopwatch."""
        return self._sidebar.exercise_timer_config()

    @property
    def should_open_sets_tab(self) -> bool:
        """Whether confirm in browse mode asked to switch to Sets."""
        return self._open_sets_on_close

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Reposition chrome after the overlay is shown and laid out."""
        super().showEvent(event)
        self._position_controls()
        self._schedule_avif_reload()

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

    def _apply_playback_view(self, view: LightboxPlaybackView) -> None:
        """Freeze or play the AVIF and show the Prepare / Finish veil."""
        previous = self._last_playback_view
        freeze = view.freeze_first_frame
        if freeze and (previous is None or not previous.freeze_first_frame):
            self._avif_manager.show_first_frame(AvifLabelKey.LIGHTBOX)
        animate = view.animate
        if previous is None or animate != previous.animate:
            if animate:
                self._avif_manager.resume_animation(AvifLabelKey.LIGHTBOX)
            else:
                self._avif_manager.pause_animation(AvifLabelKey.LIGHTBOX)
        self._last_playback_view = view
        overlay = self._phase_overlay
        if overlay is not None:
            overlay.apply(view)
            overlay.setGeometry(self._label.geometry())
            overlay.raise_()
        self._sync_speed_controls()

    def _bind_sidebar(self, index: int) -> None:
        if not self._exercises:
            return
        name = self._exercises[index]
        item_id = None
        if self._workout_items is not None and 0 <= index < len(self._workout_items):
            item_id = self._workout_items[index].id
        restore = self._pending_timer_state
        self._pending_timer_state = None
        self._sidebar.bind(name, self._details_loader(name, item_id), timer_state=restore)
        if restore is None and self._auto_start_prepare:
            self._sidebar.start_prepare()

    def _capture_timer_before_close(self) -> None:
        if self._captured_timer_state is not None:
            return
        item_id = None
        if self._workout_items is not None and 0 <= self._index < len(self._workout_items):
            item_id = self._workout_items[self._index].id
        self._captured_timer_item_id = item_id
        self._captured_timer_state = self._sidebar.capture_timer_state()

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

    def _image_pane_rect(self) -> QRect:
        width = max(self.width(), 1)
        height = max(self.height(), 1)
        handle = self._splitter.handleWidth() if self._splitter is not None else 0
        sidebar = _SIDEBAR_WIDTH
        if self._splitter is not None:
            sizes = self._splitter.sizes()
            if len(sizes) >= _SPLITTER_PANE_COUNT and sizes[0] >= _SIDEBAR_MIN_WIDTH and sizes[1] >= _MIN_IMAGE_EDGE:
                sidebar = sizes[0]
        image_width = max(width - sidebar - handle, 1)
        return QRect(sidebar + handle, 0, image_width, height)

    def _install_sidebar(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.setObjectName("fitnessLightboxSplitter")
        splitter.setChildrenCollapsible(False)
        image_host = QWidget(splitter)
        image_host.setObjectName("fitnessLightboxImageHost")
        self._label.setParent(image_host)
        overlay = LightboxPhaseOverlay(image_host)
        self._phase_overlay = overlay
        splitter.addWidget(self._sidebar)
        splitter.addWidget(image_host)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([_SIDEBAR_WIDTH, max(self.width() - _SIDEBAR_WIDTH, _SIDEBAR_WIDTH)])
        splitter.splitterMoved.connect(self._on_splitter_moved)
        self._splitter = splitter
        self._image_host = image_host
        self.attach_content(splitter)
        self._enable_backdrop_context_menu(self._sidebar)
        self._enable_backdrop_context_menu(image_host)
        self._enable_backdrop_context_menu(self._label)

    def _on_confirm(self) -> None:
        if not self._confirm_handler(self._current_confirm()):
            return
        play_fitness_timer_cue("paste")
        if self._workout_items is None:
            self._open_sets_on_close = True
            self.accept()
            return
        self._advance_after_confirm()

    def _on_splitter_moved(self, _pos: int, _index: int) -> None:
        self._position_controls()
        self._schedule_avif_reload()

    def _position_controls(self) -> None:
        if self._splitter is not None:
            self._splitter.setGeometry(self.rect())
            sizes = self._splitter.sizes()
            if len(sizes) < _SPLITTER_PANE_COUNT or sizes[1] < _MIN_IMAGE_EDGE:
                self._splitter.setSizes(
                    [_SIDEBAR_WIDTH, max(self.width() - _SIDEBAR_WIDTH, _SIDEBAR_WIDTH)],
                )
        super()._position_controls()
        host = self._image_host
        if host is None:
            return
        pane = self._image_pane_rect()
        self._label.setGeometry(0, 0, pane.width(), pane.height())
        overlay = self._phase_overlay
        if overlay is not None:
            overlay.setGeometry(self._label.geometry())
            overlay.raise_()
        self._schedule_avif_reload()

    def _reload_current(self) -> None:
        if not self._exercises:
            return
        name = self._exercises[self._index]
        self._cancel_speed_edit()
        view = self._sidebar.playback_view()
        self._avif_manager.load_exercise_avif(
            name,
            self._label,
            AvifLabelKey.LIGHTBOX,
            autoplay=view.animate,
        )
        self._loaded_size = self._label.size()
        self._last_playback_view = None
        self._apply_playback_view(view)
        self._sync_speed_controls()

    def _set_backdrop_color(self, color: str) -> None:
        super()._set_backdrop_color(color)
        self._sync_fitness_chrome_backdrop()

    def _sync_fitness_chrome_backdrop(self) -> None:
        fill = getattr(self, "_backdrop_color", "white")
        splitter = getattr(self, "_splitter", None)
        if splitter is not None:
            splitter.setStyleSheet(_fitness_splitter_style(fill))
        sidebar = getattr(self, "_sidebar", None)
        if sidebar is not None:
            sidebar.apply_backdrop(fill)


class FitnessLightboxSidebar(QFrame):
    """Quick-style column: stopwatch, exercise name, type, value, confirm."""

    confirm_requested = Signal()
    playback_changed = Signal(object)

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
        self._backdrop_dark = False
        self._countdown_seconds = max(0, countdown_seconds)
        self._slot_limit_seconds = limit_seconds if limit_seconds and limit_seconds > 0 else None
        self._limit_seconds = self._slot_limit_seconds
        self._stop_at_limit = False
        self._limit_label_kind = "slot" if self._slot_limit_seconds else ""
        self._bound_unit = ""
        self._seconds_value_mode = False
        self._planned_value = 0
        self._stopwatch = ExerciseStopwatch(
            countdown_seconds=self._countdown_seconds,
            limit_seconds=self._limit_seconds,
            stop_at_limit=self._stop_at_limit,
        )
        self._last_phase: StopwatchPhase | None = None
        self._last_synced_value_seconds: int | None = None
        self._overtime_announced = False
        self._ready_announced = False
        self._spoken_countdown: set[int] = set()
        self._tick = QTimer(self)
        self._tick.setInterval(_TICK_MS)
        self._tick.timeout.connect(self._on_tick)
        self._build_ui()
        self._apply_snapshot(self._stopwatch.snapshot())

    def apply_backdrop(self, color: str) -> None:
        """Match label colors to the lightbox backdrop (`white` or `black`)."""
        self._backdrop_dark = color == "black"
        title = _COLOR_TITLE_ON_DARK if self._backdrop_dark else _COLOR_TITLE
        muted = _COLOR_MUTED_ON_DARK if self._backdrop_dark else _COLOR_MUTED
        self._title.setStyleSheet(f"color: {title}; background: transparent;")
        self._limit_label.setStyleSheet(f"color: {muted};")
        self._unit_label.setStyleSheet(f"color: {muted};")
        self._apply_snapshot(self._stopwatch.snapshot())

    def bind(
        self,
        exercise_name: str,
        details: FitnessLightboxDetails,
        *,
        timer_state: ExerciseStopwatchState | None = None,
    ) -> None:
        """Show `exercise_name` and reset or resume the stopwatch."""
        self._title.setText(exercise_name or "Exercise")
        self._bound_unit = details.unit
        self._apply_value_input_mode(details.unit)
        self._unit_label.setText(details.unit)
        self._type_combo.blockSignals(True)  # noqa: FBT003
        self._type_combo.clear()
        for type_name in details.types:
            self._type_combo.addItem(type_name)
            local = details.type_locals.get(type_name, "").strip()
            if local:
                self._type_combo.setItemData(self._type_combo.count() - 1, local, NAME_LOCAL_ROLE)
        if details.selected_type:
            index = self._type_combo.findText(details.selected_type)
            if index >= 0:
                self._type_combo.setCurrentIndex(index)
        self._type_combo.blockSignals(False)  # noqa: FBT003
        self._type_combo.setVisible(bool(details.types))
        self._type_combo.set_two_line_mode(enabled=bool(details.type_locals))
        self._planned_value = max(0, int(details.value))
        self._set_value_total(self._planned_value)
        self._configure_limit_for_exercise(details.unit, self._planned_value)
        if timer_state is not None and timer_state.phase is not StopwatchPhase.IDLE:
            self.restore_timer_state(timer_state)
        else:
            self.reset_timer()

    def capture_timer_state(self) -> ExerciseStopwatchState:
        """Return the current stopwatch state for Continue resume."""
        return self._stopwatch.capture_state()

    def exercise_timer_config(self) -> tuple[int, int | None, bool]:
        """Return countdown, limit, and stop-at-limit used by the stopwatch."""
        return (
            self._countdown_seconds,
            self._limit_seconds,
            self._stop_at_limit,
        )

    def playback_view(self) -> LightboxPlaybackView:
        """Return overlay and animation flags for the current stopwatch."""
        return lightbox_playback_view(self._stopwatch.snapshot())

    def reset_timer(self) -> None:
        """Stop the clock and return to idle."""
        self._tick.stop()
        self._overtime_announced = False
        self._ready_announced = False
        self._spoken_countdown.clear()
        stop_fitness_timer_alert()
        self._apply_snapshot(self._stopwatch.reset())

    def restore_timer_state(self, state: ExerciseStopwatchState) -> None:
        """Resume a stopwatch captured when the lightbox was closed."""
        self._tick.stop()
        stop_fitness_timer_alert()
        snapshot = self._stopwatch.apply_state(state)
        self._overtime_announced = snapshot.is_overtime
        self._ready_announced = snapshot.phase is StopwatchPhase.COUNTDOWN
        self._spoken_countdown = set()
        if snapshot.phase is StopwatchPhase.COUNTDOWN:
            # Do not re-speak countdown values already passed while the overlay was closed.
            remaining = snapshot.display_seconds
            self._spoken_countdown = {n for n in (1, 2, 3) if n > remaining}
        self._last_phase = snapshot.phase
        self._apply_snapshot(snapshot)
        if snapshot.is_running:
            self._tick.start()

    def selected_type(self) -> str:
        """Return the chosen type, or an empty string."""
        return self._type_combo.currentText().strip()

    def shutdown(self) -> None:
        """Stop ticking and the overtime sound."""
        self._tick.stop()
        stop_fitness_timer_alert()

    def start_prepare(self) -> None:
        """Begin the ready countdown (Prepare!) from zero."""
        self._on_restart()

    def toggle_timer(self) -> None:
        """Start/resume a stopped timer, or pause a running timer."""
        if self._stopwatch.snapshot().is_running:
            self._on_pause()
        else:
            self._on_start()

    def value(self) -> int:
        """Return the numeric set value (seconds when the unit is timed)."""
        if self._seconds_value_mode:
            return minutes_seconds_to_total(
                self._value_minutes_spin.value(),
                self._value_seconds_spin.value(),
            )
        return int(self._value_spin.value())

    def _apply_snapshot(self, snapshot: StopwatchSnapshot) -> None:
        previous_phase = self._last_phase
        self._time_label.setText(format_mm_ss(snapshot.display_seconds))
        color = {
            StopwatchColor.IDLE: _COLOR_IDLE_ON_DARK if self._backdrop_dark else _COLOR_IDLE,
            StopwatchColor.COUNTDOWN: _COLOR_COUNTDOWN,
            StopwatchColor.RUNNING: (_COLOR_RUNNING_ON_DARK if self._backdrop_dark else _COLOR_RUNNING),
            StopwatchColor.OVERTIME: _COLOR_OVERTIME,
            StopwatchColor.FINISHED: _COLOR_FINISHED,
        }[snapshot.color]
        self._time_label.setStyleSheet(f"color: {color}; background: transparent;")
        self._prepare_label.hide()
        if snapshot.phase is StopwatchPhase.COUNTDOWN:
            if not self._ready_announced:
                self._ready_announced = True
                play_fitness_timer_cue("ready")
            remaining = snapshot.display_seconds
            cue = _COUNTDOWN_VOICE_CUES.get(remaining)
            if cue is not None and remaining not in self._spoken_countdown:
                self._spoken_countdown.add(remaining)
                play_fitness_timer_cue(cue)
        elif (
            previous_phase is StopwatchPhase.COUNTDOWN or previous_phase is StopwatchPhase.IDLE
        ) and snapshot.phase is StopwatchPhase.RUNNING:
            play_fitness_timer_cue("go")
        if snapshot.phase is StopwatchPhase.IDLE:
            self._ready_announced = False
            self._spoken_countdown.clear()
        if snapshot.is_overtime:
            if not self._overtime_announced:
                self._overtime_announced = True
                if self._stop_at_limit or snapshot.phase is StopwatchPhase.FINISHED:
                    play_fitness_timer_cue("time_over")
            if not snapshot.is_running:
                self._tick.stop()
        else:
            self._overtime_announced = False
            stop_fitness_timer_alert()
        self._sync_value_fields_with_timer(snapshot, previous_phase=previous_phase)
        self._sync_timer_buttons(snapshot)
        if self._limit_seconds:
            prefix = "Target" if self._limit_label_kind == "target" else "Slot"
            self._limit_label.setText(f"{prefix} {format_mm_ss(self._limit_seconds)}")
            self._limit_label.show()
        else:
            self._limit_label.hide()
        self._last_phase = snapshot.phase
        self.playback_changed.emit(lightbox_playback_view(snapshot))

    def _apply_value_input_mode(self, unit: str) -> None:
        self._seconds_value_mode = is_seconds_exercise_unit(unit)
        self._value_spin.setVisible(not self._seconds_value_mode)
        self._value_duration_wrap.setVisible(self._seconds_value_mode)
        self._unit_label.setVisible(bool(unit) and not self._seconds_value_mode)

    def _build_action_button(self) -> QPushButton:
        button = QPushButton("Add")
        apply_lucide_button_icon(button, "plus")
        button.setObjectName("fitnessLightboxAddButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumSize(220, 56)
        button.setAutoDefault(False)
        button.setDefault(False)
        _apply_pixel_font(button, pixel_size=20, weight=QFont.Weight.Bold)
        button.clicked.connect(self.confirm_requested.emit)
        return button

    def _build_duration_spin(self, object_name: str, *, maximum: int, suffix: str) -> QSpinBox:
        spin = QSpinBox()
        spin.setObjectName(object_name)
        spin.setRange(0, maximum)
        spin.setSuffix(suffix)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        spin.setFixedSize(_DURATION_SPIN_WIDTH, _DURATION_SPIN_HEIGHT)
        spin.setStyleSheet(_VALUE_STYLE)
        _apply_pixel_font(spin, pixel_size=28, weight=QFont.Weight.ExtraBold)
        spin.lineEdit().returnPressed.connect(self.confirm_requested.emit)
        spin.valueChanged.connect(self._on_value_changed)
        return spin

    def _build_timer_button(
        self,
        name: str,
        tooltip: str,
        object_name: str,
        *,
        style: str | None = None,
        role: str = "",
    ) -> QPushButton:
        button = QPushButton()
        button.setObjectName(object_name)
        button.setProperty("_fitness_timer_icon", name)
        if role:
            button.setProperty("_fitness_timer_role", role)
        apply_lucide_button_icon(
            button,
            name,
            icon_size=TOOLBAR_ICON_SIZE,
            color=_TIMER_BUTTON_ICON_ACTIVE,
        )
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoDefault(False)
        button.setDefault(False)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        button.setStyleSheet(style if style is not None else _TIMER_BUTTON_STYLE)
        self._refresh_timer_button_icon(button)
        return button

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(12)

        self._prepare_label = QLabel("Prepare!")
        self._prepare_label.setObjectName("fitnessLightboxPrepare")
        self._prepare_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._prepare_label.setStyleSheet(f"color: {_COLOR_COUNTDOWN}; background: transparent;")
        _apply_pixel_font(self._prepare_label, pixel_size=22, weight=QFont.Weight.ExtraBold)
        self._prepare_label.hide()

        self._time_label = QLabel("0:00")
        self._time_label.setObjectName("fitnessLightboxTime")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _apply_pixel_font(self._time_label, pixel_size=56, weight=QFont.Weight.ExtraBold)

        self._limit_label = QLabel("")
        self._limit_label.setObjectName("fitnessLightboxLimit")
        self._limit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._limit_label.setStyleSheet(f"color: {_COLOR_MUTED};")
        _apply_pixel_font(self._limit_label, pixel_size=14)
        self._limit_label.hide()

        self._start_button = self._build_timer_button(
            "play",
            "Start",
            "fitnessLightboxStartButton",
            style=_TIMER_BUTTON_START_STYLE,
            role=_TIMER_ROLE_START,
        )
        self._pause_button = self._build_timer_button("pause", "Pause", "fitnessLightboxPauseButton")
        self._stop_button = self._build_timer_button(
            "square",
            "Stop",
            "fitnessLightboxStopButton",
            style=_TIMER_BUTTON_STOP_STYLE,
            role=_TIMER_ROLE_STOP,
        )
        restart = self._build_timer_button("rotate-cw", "Restart", "fitnessLightboxRestartButton")
        self._start_button.clicked.connect(self._on_start)
        self._pause_button.clicked.connect(self._on_pause)
        self._stop_button.clicked.connect(self._on_stop)
        restart.clicked.connect(self._on_restart)
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(TOOLBAR_BUTTON_GAP)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self._start_button)
        controls_layout.addWidget(self._pause_button)
        controls_layout.addWidget(self._stop_button)
        controls_layout.addWidget(restart)
        controls_layout.addStretch(1)

        self._title = QLabel("Exercise")
        self._title.setObjectName("fitnessLightboxTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._title.setStyleSheet(f"color: {_COLOR_TITLE}; background: transparent;")
        _apply_pixel_font(self._title, pixel_size=22, weight=QFont.Weight.ExtraBold)

        self._type_combo = _LightboxTypeCombo()
        self._type_combo.setObjectName("fitnessLightboxTypeCombo")
        self._type_combo.setStyleSheet(_TYPE_STYLE)
        _apply_pixel_font(self._type_combo, pixel_size=16)
        self._type_combo.setItemDelegate(
            NameLocalListDelegate(self._type_combo, layout=NameLocalLayout.LIST),
        )
        self._type_combo.hide()

        self._value_spin = QSpinBox()
        self._value_spin.setObjectName("fitnessLightboxValueSpin")
        self._value_spin.setRange(0, _VALUE_MAXIMUM)
        self._value_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self._value_spin.setMinimumSize(220, _DURATION_SPIN_HEIGHT)
        self._value_spin.setStyleSheet(_VALUE_STYLE)
        _apply_pixel_font(self._value_spin, pixel_size=40, weight=QFont.Weight.ExtraBold)
        self._value_spin.lineEdit().returnPressed.connect(self.confirm_requested.emit)
        self._value_spin.valueChanged.connect(self._on_value_changed)

        self._value_duration_wrap = QWidget()
        self._value_duration_wrap.setObjectName("fitnessLightboxValueDuration")
        duration_layout = QHBoxLayout(self._value_duration_wrap)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        duration_layout.setSpacing(8)
        self._value_minutes_spin = self._build_duration_spin(
            "fitnessLightboxValueMinutesSpin",
            maximum=10_000,
            suffix=" min",
        )
        self._value_seconds_spin = self._build_duration_spin(
            "fitnessLightboxValueSecondsSpin",
            maximum=59,
            suffix=" sec",
        )
        duration_layout.addWidget(self._value_minutes_spin)
        duration_layout.addWidget(self._value_seconds_spin)
        self._value_duration_wrap.hide()

        self._unit_label = QLabel("")
        self._unit_label.setObjectName("fitnessLightboxUnit")
        self._unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._unit_label.setStyleSheet(f"color: {_COLOR_MUTED};")
        _apply_pixel_font(self._unit_label, pixel_size=16)
        self._unit_label.hide()

        add_wrap = QWidget()
        add_wrap.setStyleSheet(_ADD_BUTTON_STYLE)
        add_layout = QVBoxLayout(add_wrap)
        add_layout.setContentsMargins(0, 0, 0, 0)
        add_layout.addWidget(self._build_action_button(), 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(self._prepare_label)
        layout.addWidget(self._time_label)
        layout.addWidget(self._limit_label)
        layout.addWidget(controls)
        layout.addSpacing(8)
        layout.addWidget(self._title)
        layout.addStretch(2)
        layout.addWidget(self._type_combo)
        layout.addWidget(self._value_spin, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._value_duration_wrap, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._unit_label)
        layout.addWidget(add_wrap, 0, Qt.AlignmentFlag.AlignHCenter)

    def _configure_limit_for_exercise(self, unit: str, value: int) -> None:
        target = target_seconds_for_exercise(unit, value)
        if target is not None:
            self._limit_seconds = target
            self._stop_at_limit = True
            self._limit_label_kind = "target"
        elif self._slot_limit_seconds:
            self._limit_seconds = self._slot_limit_seconds
            self._stop_at_limit = False
            self._limit_label_kind = "slot"
        else:
            self._limit_seconds = None
            self._stop_at_limit = False
            self._limit_label_kind = ""
        previous = self._stopwatch.capture_state()
        self._stopwatch = ExerciseStopwatch(
            countdown_seconds=self._countdown_seconds,
            limit_seconds=self._limit_seconds,
            stop_at_limit=self._stop_at_limit,
        )
        if previous.phase is not StopwatchPhase.IDLE:
            self._stopwatch.apply_state(previous)

    def _on_pause(self) -> None:
        if not self._stopwatch.snapshot().is_running:
            return
        self._tick.stop()
        self._apply_snapshot(self._stopwatch.pause())
        play_fitness_timer_cue("pause")

    def _on_restart(self) -> None:
        self._ready_announced = False
        self._spoken_countdown.clear()
        self._overtime_announced = False
        self._configure_limit_for_exercise(self._bound_unit, self._planned_value)
        self._set_value_total(self._planned_value)
        self._tick.start()
        self._apply_snapshot(self._stopwatch.restart())

    def _on_start(self) -> None:
        snapshot = self._stopwatch.snapshot()
        fresh_start = snapshot.phase in {StopwatchPhase.IDLE, StopwatchPhase.FINISHED}
        resuming = not fresh_start and not snapshot.is_running
        if fresh_start:
            self._ready_announced = False
            self._spoken_countdown.clear()
            self._overtime_announced = False
        self._tick.start()
        self._apply_snapshot(self._stopwatch.start())
        if resuming:
            play_fitness_timer_cue("continue")

    def _on_stop(self) -> None:
        snapshot = self._stopwatch.snapshot()
        if snapshot.phase in {StopwatchPhase.IDLE, StopwatchPhase.FINISHED}:
            return
        self._tick.stop()
        if not self._overtime_announced:
            self._overtime_announced = True
            play_fitness_timer_cue("time_over")
        self._apply_snapshot(self._stopwatch.stop())

    def _on_tick(self) -> None:
        self._apply_snapshot(self._stopwatch.advance(_TICK_MS))

    def _on_value_changed(self, _value: int = 0) -> None:
        if self._stopwatch.snapshot().phase is not StopwatchPhase.IDLE:
            return
        self._planned_value = self.value()
        self._configure_limit_for_exercise(self._bound_unit, self._planned_value)
        self._apply_snapshot(self._stopwatch.snapshot())

    def _refresh_timer_button_icon(self, button: QPushButton) -> None:
        """Repaint the Lucide icon active or muted to match enabled state."""
        name = button.property("_fitness_timer_icon")
        if not isinstance(name, str) or not name:
            return
        role = button.property("_fitness_timer_role")
        if button.isEnabled() and role in {_TIMER_ROLE_START, _TIMER_ROLE_STOP}:
            color = _TIMER_BUTTON_ICON_ON_FILLED
        elif button.isEnabled():
            color = _TIMER_BUTTON_ICON_ACTIVE
        else:
            color = _TIMER_BUTTON_ICON_DISABLED
        apply_lucide_button_icon(button, name, icon_size=TOOLBAR_ICON_SIZE, color=color)
        button.setCursor(
            Qt.CursorShape.PointingHandCursor if button.isEnabled() else Qt.CursorShape.ArrowCursor,
        )

    def _set_value_total(self, total_seconds: int) -> None:
        total = max(0, int(total_seconds))
        if self._seconds_value_mode:
            minutes, seconds = split_total_seconds(total)
            self._value_minutes_spin.blockSignals(True)  # noqa: FBT003
            self._value_seconds_spin.blockSignals(True)  # noqa: FBT003
            self._value_minutes_spin.setValue(minutes)
            self._value_seconds_spin.setValue(seconds)
            self._value_minutes_spin.blockSignals(False)  # noqa: FBT003
            self._value_seconds_spin.blockSignals(False)  # noqa: FBT003
            return
        self._value_spin.blockSignals(True)  # noqa: FBT003
        self._value_spin.setValue(total)
        self._value_spin.blockSignals(False)  # noqa: FBT003

    def _sync_timer_buttons(self, snapshot: StopwatchSnapshot) -> None:
        """Enable timer actions that are valid for the current state."""
        self._start_button.setEnabled(not snapshot.is_running)
        self._pause_button.setEnabled(snapshot.is_running)
        self._stop_button.setEnabled(
            snapshot.phase not in {StopwatchPhase.IDLE, StopwatchPhase.FINISHED},
        )
        self._refresh_timer_button_icon(self._start_button)
        self._refresh_timer_button_icon(self._pause_button)
        self._refresh_timer_button_icon(self._stop_button)

    def _sync_value_fields_with_timer(
        self,
        snapshot: StopwatchSnapshot,
        *,
        previous_phase: StopwatchPhase | None,
    ) -> None:
        if not self._seconds_value_mode:
            return
        if snapshot.phase is StopwatchPhase.RUNNING:
            if self._last_synced_value_seconds != snapshot.display_seconds:
                self._last_synced_value_seconds = snapshot.display_seconds
                self._set_value_total(snapshot.display_seconds)
            return
        if snapshot.phase is StopwatchPhase.FINISHED and previous_phase in {
            StopwatchPhase.RUNNING,
            StopwatchPhase.FINISHED,
        }:
            self._last_synced_value_seconds = snapshot.display_seconds
            self._set_value_total(snapshot.display_seconds)
        elif snapshot.phase in {StopwatchPhase.IDLE, StopwatchPhase.COUNTDOWN}:
            self._last_synced_value_seconds = None


class LightboxPhaseOverlay(QWidget):
    """Dimmed first-frame overlay for Prepare countdown and Finish."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the centered Prepare / Finish labels."""
        super().__init__(parent)
        self.setObjectName("fitnessLightboxPhaseOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._title = QLabel("Prepare", self)
        self._title.setObjectName("fitnessLightboxOverlayTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("color: #FFFFFF; background: transparent;")
        _apply_pixel_font(self._title, pixel_size=48, weight=QFont.Weight.ExtraBold)
        self._number = QLabel("", self)
        self._number.setObjectName("fitnessLightboxOverlayNumber")
        self._number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._number.setStyleSheet("color: #FFFFFF; background: transparent;")
        _apply_pixel_font(self._number, pixel_size=96, weight=QFont.Weight.ExtraBold)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        layout.addStretch(1)
        layout.addWidget(self._title)
        layout.addWidget(self._number)
        layout.addStretch(1)
        self.hide()

    def apply(self, view: LightboxPlaybackView) -> None:
        """Show Prepare + countdown, Finish, or hide the overlay."""
        if view.overlay is LightboxOverlayKind.NONE:
            self.hide()
            return
        if view.overlay is LightboxOverlayKind.PREPARE:
            self._title.setText("Prepare")
            self._number.setText(str(view.countdown_seconds))
            self._number.show()
        else:
            self._title.setText("Finish")
            self._number.clear()
            self._number.hide()
        self.show()
        self.raise_()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Fill the image pane with a dark translucent veil."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))


class _LightboxTypeCombo(QComboBox):
    """QComboBox that paints a flat chevron and optional local-name second line."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the combo with single-line height by default."""
        super().__init__(parent)
        self._two_line_mode = False
        self.setMinimumHeight(_TYPE_COMBO_SINGLE_HEIGHT)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Draw the combo frame, two-line labels, and a simple down arrow."""
        del event
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        main_text = option.currentText
        local_text = str(self.currentData(NAME_LOCAL_ROLE) or "").strip()
        option.currentText = ""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        style = self.style()
        style.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option, painter, self)
        edit_rect = style.subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            option,
            QStyle.SubControl.SC_ComboBoxEditField,
            self,
        )
        if edit_rect.isValid() and main_text:
            self._paint_labels(painter, edit_rect, main_text, local_text)
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

    def set_two_line_mode(self, *, enabled: bool) -> None:
        """Grow the closed combo when type rows include a local name."""
        self._two_line_mode = enabled
        self.setMinimumHeight(_TYPE_COMBO_DOUBLE_HEIGHT if enabled else _TYPE_COMBO_SINGLE_HEIGHT)
        self.update()

    def _paint_labels(self, painter: QPainter, text_rect: QRect, main_text: str, local_text: str) -> None:
        font = self.font()
        metrics = QFontMetrics(font)
        painter.save()
        if not local_text or not self._two_line_mode:
            painter.setPen(QColor("#111827"))
            painter.setFont(font)
            painter.drawText(
                text_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextSingleLine),
                metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, text_rect.width()),
            )
            painter.restore()
            return

        local_font = QFont(font)
        pixel = font.pixelSize()
        if pixel > 0:
            local_font.setPixelSize(max(12, round(pixel * 0.85)))
        else:
            point = font.pointSizeF()
            if point <= 0:
                point = float(font.pointSize()) or 9.0
            local_font.setPointSizeF(max(7.0, point * 0.85))
        local_metrics = QFontMetrics(local_font)
        main_height = metrics.height()
        local_height = local_metrics.height()
        total_height = main_height + 1 + local_height
        top = text_rect.y() + max(0, (text_rect.height() - total_height) // 2)
        main_rect = QRect(text_rect.x(), top, text_rect.width(), main_height)
        local_rect = QRect(text_rect.x(), top + main_height + 1, text_rect.width(), local_height)
        left_flags = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextSingleLine)
        painter.setPen(QColor("#111827"))
        painter.setFont(font)
        painter.drawText(
            main_rect,
            left_flags,
            metrics.elidedText(main_text, Qt.TextElideMode.ElideRight, main_rect.width()),
        )
        painter.setPen(_NAME_LOCAL_COLOR)
        painter.setFont(local_font)
        painter.drawText(
            local_rect,
            left_flags,
            local_metrics.elidedText(local_text, Qt.TextElideMode.ElideRight, local_rect.width()),
        )
        painter.restore()


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


def _fitness_splitter_style(fill: str) -> str:
    return f"""
QSplitter#fitnessLightboxSplitter {{
    background: {fill};
    border: none;
}}
QSplitter#fitnessLightboxSplitter::handle {{
    background: {fill};
    width: 6px;
    margin: 0;
    padding: 0;
    border: none;
}}
QSplitter#fitnessLightboxSplitter::handle:hover {{
    background: {_SPLITTER_HOVER};
}}
QWidget#fitnessLightboxImageHost {{
    background: {fill};
    border: none;
}}
"""


def _timer_button_style(
    *,
    background: str,
    border: str,
    hover_background: str,
    hover_border: str,
    pressed_background: str,
    pressed_border: str,
    disabled_background: str = "#FBFBFC",
    disabled_border: str = "#F0F0F2",
) -> str:
    return f"""
QPushButton {{
    background-color: {background};
    border: 1px solid {border};
    border-radius: {TOOLBAR_BORDER_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover:!disabled {{
    background-color: {hover_background};
    border-color: {hover_border};
}}
QPushButton:pressed:!disabled {{
    background-color: {pressed_background};
    border-color: {pressed_border};
}}
QPushButton:disabled {{
    background-color: {disabled_background};
    border: 1px solid {disabled_border};
}}
"""


_TIMER_BUTTON_STYLE = _timer_button_style(
    background="#F5F5F7",
    border="#E5E5E8",
    hover_background="#ECECEF",
    hover_border="#D8D8DC",
    pressed_background="#E2E2E6",
    pressed_border="#C8C8CC",
)
_TIMER_BUTTON_START_STYLE = _timer_button_style(
    background="#16A34A",
    border="#15803D",
    hover_background="#15803D",
    hover_border="#166534",
    pressed_background="#166534",
    pressed_border="#14532D",
    disabled_background="#E5E7EB",
    disabled_border="#D1D5DB",
)
_TIMER_BUTTON_STOP_STYLE = _timer_button_style(
    background="#DC2626",
    border="#B91C1C",
    hover_background="#B91C1C",
    hover_border="#991B1B",
    pressed_background="#991B1B",
    pressed_border="#7F1D1D",
    disabled_background="#FEE2E2",
    disabled_border="#FECACA",
)


_PANE_STYLE = """
QFrame#fitnessLightboxPane {
    background: transparent;
    border: none;
    border-radius: 0;
}
"""


_VALUE_STYLE = """
QSpinBox#fitnessLightboxValueSpin,
QSpinBox#fitnessLightboxValueMinutesSpin,
QSpinBox#fitnessLightboxValueSecondsSpin {
    background: #FFFFFF;
    border: 2px solid #D1D5DB;
    border-radius: 16px;
    padding: 8px 12px;
    color: #111827;
}
QSpinBox#fitnessLightboxValueSpin:focus,
QSpinBox#fitnessLightboxValueMinutesSpin:focus,
QSpinBox#fitnessLightboxValueSecondsSpin:focus {
    border-color: #3B82F6;
}
"""

_TYPE_STYLE = """
QComboBox#fitnessLightboxTypeCombo {
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
    padding: 6px 32px 6px 12px;
    color: #111827;
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

DetailsLoader = Callable[[str, int | None], FitnessLightboxDetails]
ConfirmHandler = Callable[[FitnessLightboxConfirm], bool]
