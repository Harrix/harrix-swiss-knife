---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fitness_lightbox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FitnessExerciseLightboxDialog`](#%EF%B8%8F-class-fitnessexerciselightboxdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `captured_timer_state`](#%EF%B8%8F-method-captured_timer_state)
  - [⚙️ Method `chrome_rect`](#%EF%B8%8F-method-chrome_rect)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `done`](#%EF%B8%8F-method-done)
  - [⚙️ Method `exercise_timer_config`](#%EF%B8%8F-method-exercise_timer_config)
  - [⚙️ Method `should_open_sets_tab (property)`](#%EF%B8%8F-method-should_open_sets_tab-property)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
  - [⚙️ Method `show_item`](#%EF%B8%8F-method-show_item)
- [🏛️ Class `FitnessLightboxSidebar`](#%EF%B8%8F-class-fitnesslightboxsidebar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `apply_backdrop`](#%EF%B8%8F-method-apply_backdrop)
  - [⚙️ Method `bind`](#%EF%B8%8F-method-bind)
  - [⚙️ Method `capture_timer_state`](#%EF%B8%8F-method-capture_timer_state)
  - [⚙️ Method `exercise_timer_config`](#%EF%B8%8F-method-exercise_timer_config-1)
  - [⚙️ Method `reset_timer`](#%EF%B8%8F-method-reset_timer)
  - [⚙️ Method `restore_timer_state`](#%EF%B8%8F-method-restore_timer_state)
  - [⚙️ Method `selected_type`](#%EF%B8%8F-method-selected_type)
  - [⚙️ Method `shutdown`](#%EF%B8%8F-method-shutdown)
  - [⚙️ Method `start_prepare`](#%EF%B8%8F-method-start_prepare)
  - [⚙️ Method `value`](#%EF%B8%8F-method-value)

</details>

## 🏛️ Class `FitnessExerciseLightboxDialog`

```python
class FitnessExerciseLightboxDialog(ExerciseAvifLightboxDialog)
```

Exercise AVIF lightbox with a Quick-style timer and log column.

<details>
<summary>Code:</summary>

```python
class FitnessExerciseLightboxDialog(ExerciseAvifLightboxDialog):

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
        self._splitter: QSplitter | None = None
        self._sidebar = FitnessLightboxSidebar(
            countdown_seconds=countdown_seconds,
            limit_seconds=self._limit_seconds,
            parent=self,
        )
        self._sidebar.confirm_requested.connect(self._on_confirm)
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
        self._schedule_avif_reload()

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
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, exercises: Sequence[str], *, avif_manager: AvifManager, details_loader: DetailsLoader, confirm_handler: ConfirmHandler, current_index: int = 0, parent: QWidget | None = None, countdown_seconds: int = DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS, workout_items: Sequence[WorkoutItemRow] | None = None, workout_duration_min: int | None = None, auto_start_prepare: bool = False, initial_timer_state: ExerciseStopwatchState | None = None) -> None
```

Build the Fitness lightbox.

Args:

- `exercises` (`Sequence[str]`): Exercise names in navigation order.
- `avif_manager` ([`AvifManager`](../common/avif_manager.g.md#%EF%B8%8F-class-avifmanager)): Loader for static and animated AVIF files.
- `details_loader` (`DetailsLoader`): Loads types, unit, and default value.
- `confirm_handler` (`ConfirmHandler`): Persists a completed set.
- [`current_index`](../common/widgets/app_window_lightbox.g.md#%EF%B8%8F-method-current_index-property) (`int`): Initial exercise index. Defaults to `0`.
- `parent` (`QWidget | None`): Widget whose top-level window is covered.
- `countdown_seconds` (`int`): Ready countdown before the stopwatch.
- `workout_items` (`Sequence[WorkoutItemRow] | None`): Workout rows when
  opened from a saved workout. `None` is browse mode.
- `workout_duration_min` (`int | None`): Planned workout length.
- `auto_start_prepare` (`bool`): Start the Prepare countdown when each
  exercise is shown. Defaults to `False`.
- `initial_timer_state` (`ExerciseStopwatchState | None`): Resume the
  stopwatch for the first shown workout item instead of restarting.

<details>
<summary>Code:</summary>

```python
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
        self._splitter: QSplitter | None = None
        self._sidebar = FitnessLightboxSidebar(
            countdown_seconds=countdown_seconds,
            limit_seconds=self._limit_seconds,
            parent=self,
        )
        self._sidebar.confirm_requested.connect(self._on_confirm)
        self._install_sidebar()
        self._sync_fitness_chrome_backdrop()
        self.finish_setup()
```

</details>

### ⚙️ Method `captured_timer_state`

```python
def captured_timer_state(self) -> tuple[int | None, ExerciseStopwatchState | None]
```

Return the workout item ID and stopwatch state captured on close.

<details>
<summary>Code:</summary>

```python
def captured_timer_state(self) -> tuple[int | None, ExerciseStopwatchState | None]:
        return self._captured_timer_item_id, self._captured_timer_state
```

</details>

### ⚙️ Method `chrome_rect`

```python
def chrome_rect(self) -> QRect
```

Place overlay chrome over the image pane, not the timer column.

Uses the dialog size and sidebar width so arrows and captions are
not piled at the origin while the splitter is still laying out.

<details>
<summary>Code:</summary>

```python
def chrome_rect(self) -> QRect:
        return self._image_pane_rect()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Capture the exercise timer, then stop alerts when the overlay closes.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._capture_timer_before_close()
        self._sidebar.shutdown()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `done`

```python
def done(self, result: int) -> None
```

Capture the exercise timer, then stop alerts when `exec` finishes.

<details>
<summary>Code:</summary>

```python
def done(self, result: int) -> None:
        self._capture_timer_before_close()
        self._sidebar.shutdown()
        super().done(result)
```

</details>

### ⚙️ Method `exercise_timer_config`

```python
def exercise_timer_config(self) -> tuple[int, int | None, bool]
```

Return countdown, limit, and stop-at-limit used by the sidebar stopwatch.

<details>
<summary>Code:</summary>

```python
def exercise_timer_config(self) -> tuple[int, int | None, bool]:
        return self._sidebar.exercise_timer_config()
```

</details>

### ⚙️ Method `should_open_sets_tab (property)`

```python
def should_open_sets_tab(self) -> bool
```

Whether confirm in browse mode asked to switch to Sets.

<details>
<summary>Code:</summary>

```python
def should_open_sets_tab(self) -> bool:
        return self._open_sets_on_close
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Reposition chrome after the overlay is shown and laid out.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._position_controls()
        self._schedule_avif_reload()
```

</details>

### ⚙️ Method `show_item`

```python
def show_item(self, index: int) -> None
```

Load the exercise image and bind the timer column.

<details>
<summary>Code:</summary>

```python
def show_item(self, index: int) -> None:
        self._position_controls()
        super().show_item(index)
        self._bind_sidebar(index)
```

</details>

## 🏛️ Class `FitnessLightboxSidebar`

```python
class FitnessLightboxSidebar(QFrame)
```

Quick-style column: stopwatch, exercise name, type, value, confirm.

<details>
<summary>Code:</summary>

```python
class FitnessLightboxSidebar(QFrame):

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
        self._backdrop_dark = False
        self._countdown_seconds = max(0, countdown_seconds)
        self._slot_limit_seconds = limit_seconds if limit_seconds and limit_seconds > 0 else None
        self._limit_seconds = self._slot_limit_seconds
        self._stop_at_limit = False
        self._limit_label_kind = "slot" if self._slot_limit_seconds else ""
        self._bound_unit = ""
        self._stopwatch = ExerciseStopwatch(
            countdown_seconds=self._countdown_seconds,
            limit_seconds=self._limit_seconds,
            stop_at_limit=self._stop_at_limit,
        )
        self._last_phase: StopwatchPhase | None = None
        self._overtime_announced = False
        self._ready_announced = False
        self._spoken_countdown: set[int] = set()
        self._tick = QTimer(self)
        self._tick.setInterval(_TICK_MS)
        self._tick.timeout.connect(self._on_tick)
        self._status_flash = QTimer(self)
        self._status_flash.setSingleShot(True)
        self._status_flash.timeout.connect(self._hide_status_flash)
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
        self._value_spin.blockSignals(True)  # noqa: FBT003
        self._value_spin.setValue(details.value)
        self._value_spin.blockSignals(False)  # noqa: FBT003
        self._configure_limit_for_exercise(details.unit, details.value)
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

    def reset_timer(self) -> None:
        """Stop the clock and return to idle."""
        self._tick.stop()
        self._status_flash.stop()
        self._overtime_announced = False
        self._ready_announced = False
        self._spoken_countdown.clear()
        stop_fitness_timer_alert()
        self._apply_snapshot(self._stopwatch.reset())

    def restore_timer_state(self, state: ExerciseStopwatchState) -> None:
        """Resume a stopwatch captured when the lightbox was closed."""
        self._tick.stop()
        self._status_flash.stop()
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
        self._status_flash.stop()
        stop_fitness_timer_alert()

    def start_prepare(self) -> None:
        """Begin the ready countdown (Prepare!) from zero."""
        self._on_restart()

    def value(self) -> int:
        """Return the numeric set value."""
        return int(self._value_spin.value())

    def _apply_snapshot(self, snapshot: StopwatchSnapshot) -> None:
        previous_phase = self._last_phase
        self._time_label.setText(format_mm_ss(snapshot.display_seconds))
        color = {
            StopwatchColor.IDLE: _COLOR_IDLE_ON_DARK if self._backdrop_dark else _COLOR_IDLE,
            StopwatchColor.COUNTDOWN: _COLOR_COUNTDOWN,
            StopwatchColor.RUNNING: (_COLOR_RUNNING_ON_DARK if self._backdrop_dark else _COLOR_RUNNING),
            StopwatchColor.OVERTIME: _COLOR_OVERTIME,
        }[snapshot.color]
        self._time_label.setStyleSheet(f"color: {color}; background: transparent;")
        if snapshot.phase is StopwatchPhase.COUNTDOWN:
            self._status_flash.stop()
            self._show_status_label("Prepare!", _COLOR_COUNTDOWN)
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
            start_color = _COLOR_RUNNING_ON_DARK if self._backdrop_dark else _COLOR_RUNNING
            self._flash_status("Start", start_color)
        elif snapshot.phase is StopwatchPhase.IDLE and not self._status_flash.isActive():
            self._prepare_label.hide()
        if snapshot.phase is StopwatchPhase.IDLE:
            self._ready_announced = False
            self._spoken_countdown.clear()
        if snapshot.is_overtime:
            if not self._overtime_announced:
                self._overtime_announced = True
                if self._stop_at_limit:
                    play_fitness_timer_cue("time_over")
                self._flash_status("Finish", _COLOR_OVERTIME)
            if not snapshot.is_running:
                self._tick.stop()
        else:
            self._overtime_announced = False
            stop_fitness_timer_alert()
        if self._limit_seconds:
            prefix = "Target" if self._limit_label_kind == "target" else "Slot"
            self._limit_label.setText(f"{prefix} {format_mm_ss(self._limit_seconds)}")
            self._limit_label.show()
        else:
            self._limit_label.hide()
        self._last_phase = snapshot.phase

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
        self._title.setStyleSheet(f"color: {_COLOR_TITLE}; background: transparent;")
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
        self._value_spin.valueChanged.connect(self._on_value_changed)

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

    def _flash_status(self, text: str, color: str) -> None:
        self._status_flash.stop()
        self._show_status_label(text, color)
        self._status_flash.start(_STATUS_FLASH_MS)

    def _hide_status_flash(self) -> None:
        if self._stopwatch.snapshot().phase is StopwatchPhase.COUNTDOWN:
            self._show_status_label("Prepare!", _COLOR_COUNTDOWN)
            return
        self._prepare_label.hide()

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
        self._configure_limit_for_exercise(self._bound_unit, self.value())
        self._tick.start()
        self._apply_snapshot(self._stopwatch.restart())

    def _on_start(self) -> None:
        snapshot = self._stopwatch.snapshot()
        resuming = snapshot.phase is not StopwatchPhase.IDLE and not snapshot.is_running
        if snapshot.phase is StopwatchPhase.IDLE:
            self._ready_announced = False
            self._spoken_countdown.clear()
            self._overtime_announced = False
        self._tick.start()
        self._apply_snapshot(self._stopwatch.start())
        if resuming:
            play_fitness_timer_cue("continue")

    def _on_tick(self) -> None:
        self._apply_snapshot(self._stopwatch.advance(_TICK_MS))

    def _on_value_changed(self, value: int) -> None:
        if self._stopwatch.snapshot().phase is not StopwatchPhase.IDLE:
            return
        self._configure_limit_for_exercise(self._bound_unit, value)
        self._apply_snapshot(self._stopwatch.snapshot())

    def _show_status_label(self, text: str, color: str) -> None:
        self._prepare_label.setText(text)
        self._prepare_label.setStyleSheet(f"color: {color}; background: transparent;")
        self._prepare_label.show()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, countdown_seconds: int, limit_seconds: int | None, parent: QWidget | None = None) -> None
```

Build the timer column.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        countdown_seconds: int,
        limit_seconds: int | None,
        parent: QWidget | None = None,
    ) -> None:
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
        self._stopwatch = ExerciseStopwatch(
            countdown_seconds=self._countdown_seconds,
            limit_seconds=self._limit_seconds,
            stop_at_limit=self._stop_at_limit,
        )
        self._last_phase: StopwatchPhase | None = None
        self._overtime_announced = False
        self._ready_announced = False
        self._spoken_countdown: set[int] = set()
        self._tick = QTimer(self)
        self._tick.setInterval(_TICK_MS)
        self._tick.timeout.connect(self._on_tick)
        self._status_flash = QTimer(self)
        self._status_flash.setSingleShot(True)
        self._status_flash.timeout.connect(self._hide_status_flash)
        self._build_ui()
        self._apply_snapshot(self._stopwatch.snapshot())
```

</details>

### ⚙️ Method `apply_backdrop`

```python
def apply_backdrop(self, color: str) -> None
```

Match label colors to the lightbox backdrop (`white` or `black`).

<details>
<summary>Code:</summary>

```python
def apply_backdrop(self, color: str) -> None:
        self._backdrop_dark = color == "black"
        title = _COLOR_TITLE_ON_DARK if self._backdrop_dark else _COLOR_TITLE
        muted = _COLOR_MUTED_ON_DARK if self._backdrop_dark else _COLOR_MUTED
        self._title.setStyleSheet(f"color: {title}; background: transparent;")
        self._limit_label.setStyleSheet(f"color: {muted};")
        self._unit_label.setStyleSheet(f"color: {muted};")
        self._apply_snapshot(self._stopwatch.snapshot())
```

</details>

### ⚙️ Method `bind`

```python
def bind(self, exercise_name: str, details: FitnessLightboxDetails, *, timer_state: ExerciseStopwatchState | None = None) -> None
```

Show `exercise_name` and reset or resume the stopwatch.

<details>
<summary>Code:</summary>

```python
def bind(
        self,
        exercise_name: str,
        details: FitnessLightboxDetails,
        *,
        timer_state: ExerciseStopwatchState | None = None,
    ) -> None:
        self._title.setText(exercise_name or "Exercise")
        self._bound_unit = details.unit
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
        self._value_spin.blockSignals(True)  # noqa: FBT003
        self._value_spin.setValue(details.value)
        self._value_spin.blockSignals(False)  # noqa: FBT003
        self._configure_limit_for_exercise(details.unit, details.value)
        if timer_state is not None and timer_state.phase is not StopwatchPhase.IDLE:
            self.restore_timer_state(timer_state)
        else:
            self.reset_timer()
```

</details>

### ⚙️ Method `capture_timer_state`

```python
def capture_timer_state(self) -> ExerciseStopwatchState
```

Return the current stopwatch state for Continue resume.

<details>
<summary>Code:</summary>

```python
def capture_timer_state(self) -> ExerciseStopwatchState:
        return self._stopwatch.capture_state()
```

</details>

### ⚙️ Method `exercise_timer_config`

```python
def exercise_timer_config(self) -> tuple[int, int | None, bool]
```

Return countdown, limit, and stop-at-limit used by the stopwatch.

<details>
<summary>Code:</summary>

```python
def exercise_timer_config(self) -> tuple[int, int | None, bool]:
        return (
            self._countdown_seconds,
            self._limit_seconds,
            self._stop_at_limit,
        )
```

</details>

### ⚙️ Method `reset_timer`

```python
def reset_timer(self) -> None
```

Stop the clock and return to idle.

<details>
<summary>Code:</summary>

```python
def reset_timer(self) -> None:
        self._tick.stop()
        self._status_flash.stop()
        self._overtime_announced = False
        self._ready_announced = False
        self._spoken_countdown.clear()
        stop_fitness_timer_alert()
        self._apply_snapshot(self._stopwatch.reset())
```

</details>

### ⚙️ Method `restore_timer_state`

```python
def restore_timer_state(self, state: ExerciseStopwatchState) -> None
```

Resume a stopwatch captured when the lightbox was closed.

<details>
<summary>Code:</summary>

```python
def restore_timer_state(self, state: ExerciseStopwatchState) -> None:
        self._tick.stop()
        self._status_flash.stop()
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
```

</details>

### ⚙️ Method `selected_type`

```python
def selected_type(self) -> str
```

Return the chosen type, or an empty string.

<details>
<summary>Code:</summary>

```python
def selected_type(self) -> str:
        return self._type_combo.currentText().strip()
```

</details>

### ⚙️ Method `shutdown`

```python
def shutdown(self) -> None
```

Stop ticking and the overtime sound.

<details>
<summary>Code:</summary>

```python
def shutdown(self) -> None:
        self._tick.stop()
        self._status_flash.stop()
        stop_fitness_timer_alert()
```

</details>

### ⚙️ Method `start_prepare`

```python
def start_prepare(self) -> None
```

Begin the ready countdown (Prepare!) from zero.

<details>
<summary>Code:</summary>

```python
def start_prepare(self) -> None:
        self._on_restart()
```

</details>

### ⚙️ Method `value`

```python
def value(self) -> int
```

Return the numeric set value.

<details>
<summary>Code:</summary>

```python
def value(self) -> int:
        return int(self._value_spin.value())
```

</details>
