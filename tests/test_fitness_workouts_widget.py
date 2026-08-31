"""Tests for the Fitness Workouts items table."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox

from harrix_swiss_knife.apps.fitness.database_manager import WorkoutItemRow
from harrix_swiss_knife.apps.fitness.lightbox_logic import ExerciseStopwatchState, StopwatchPhase
from harrix_swiss_knife.apps.fitness.workouts_widget import (
    _COL_EXERCISE,
    _COL_IMAGE,
    _COL_KCAL,
    _COL_VALUE,
    _ROW_COLOR_CURRENT,
    WorkoutsWidget,
    estimate_workout_item_kcal,
)

if TYPE_CHECKING:
    import pytest

    from harrix_swiss_knife.apps.fitness.database_manager import DatabaseManager


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _sample_item() -> WorkoutItemRow:
    return WorkoutItemRow(
        id=1,
        workout_id=1,
        exercise_id=2,
        type_id=3,
        exercise_name="Pull-up",
        type_name="Bodyweight",
        target_value="10",
        sort_order=0,
        is_done=False,
        process_id=None,
        unit="times",
        calories_per_unit=1.0,
        calories_modifier=1.0,
    )


def test_workouts_table_has_image_column_like_other_tables() -> None:
    """Items table shows a thumbnail column and hover can resolve the exercise."""
    assert _qapp() is not None
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.red)
    icon = QIcon(pixmap)
    widget = WorkoutsWidget()
    widget.configure_exercise_images(icon_size=32, icon_getter=lambda _name: icon)
    widget._fill_items([_sample_item()])

    table = widget.table_items
    assert table.columnCount() == 7
    image_header = table.horizontalHeaderItem(_COL_IMAGE)
    name_header = table.horizontalHeaderItem(_COL_EXERCISE)
    assert image_header is not None
    assert name_header is not None
    assert image_header.text() == ""
    assert name_header.text() == "Exercise"
    image_item = table.item(0, _COL_IMAGE)
    name_item = table.item(0, _COL_EXERCISE)
    assert image_item is not None
    assert name_item is not None
    assert name_item.text() == "Pull-up"
    assert not image_item.icon().isNull()

    widget.resize(800, 400)
    widget.show()
    _qapp().processEvents()
    index = table.model().index(0, _COL_IMAGE)
    assert widget.exercise_at_image(table.visualRect(index).center()) == "Pull-up"

    widget.update_exercise_icon("Pull-up", QIcon())
    assert image_item.icon().isNull()
    widget.close()


def test_workouts_widget_shows_estimated_duration() -> None:
    """Duration is read-only and shows an approximate estimate."""
    assert _qapp() is not None
    widget = WorkoutsWidget()
    assert widget.label_duration.text() == ""
    widget._current_workout_id = 1
    widget._fill_items([_sample_item()])
    assert widget.label_duration.text() == "~1 min"
    assert not widget.table_items.verticalHeader().isVisible()
    widget.close()


def test_estimate_workout_item_kcal() -> None:
    """Kcal helper multiplies value by calorie factors."""
    assert estimate_workout_item_kcal("10", calories_per_unit=0.5, calories_modifier=2.0) == 10.0
    assert estimate_workout_item_kcal("bad", calories_per_unit=1.0, calories_modifier=1.0) == 0.0


def test_workouts_value_edit_recalculates_kcal() -> None:
    """Changing Value updates row kcal and estimated total."""
    assert _qapp() is not None
    item = _sample_item()
    item = WorkoutItemRow(
        id=item.id,
        workout_id=item.workout_id,
        exercise_id=item.exercise_id,
        type_id=item.type_id,
        exercise_name=item.exercise_name,
        type_name=item.type_name,
        target_value=item.target_value,
        sort_order=item.sort_order,
        is_done=item.is_done,
        process_id=item.process_id,
        unit=item.unit,
        calories_per_unit=0.5,
        calories_modifier=2.0,
    )
    widget = WorkoutsWidget()
    widget._current_workout_id = 1
    widget._fill_items([item])
    value_item = widget.table_items.item(0, _COL_VALUE)
    kcal_item = widget.table_items.item(0, _COL_KCAL)
    assert value_item is not None
    assert kcal_item is not None
    assert value_item.flags() & Qt.ItemFlag.ItemIsEditable
    assert kcal_item.text() == "10.0"
    assert widget.label_totals.text() == "Estimated: 10 kcal"
    assert widget.label_duration.text() == "~1 min"

    value_item.setText("20")
    widget._on_table_item_changed(value_item)
    assert kcal_item.text() == "20.0"
    assert widget.label_totals.text() == "Estimated: 20 kcal"
    assert widget.label_duration.text() == "~2 min"
    widget.close()


def test_workouts_done_item_value_is_read_only() -> None:
    """Completed rows keep Value read-only but Done can still be unchecked."""
    assert _qapp() is not None
    done_item = WorkoutItemRow(
        id=2,
        workout_id=1,
        exercise_id=2,
        type_id=3,
        exercise_name="Squat",
        type_name="Bodyweight",
        target_value="15",
        sort_order=1,
        is_done=True,
        process_id=99,
        unit="times",
        calories_per_unit=1.0,
        calories_modifier=1.0,
    )
    widget = WorkoutsWidget()
    received: list[tuple[int, bool]] = []
    widget.item_done_requested.connect(lambda item_id, checked: received.append((item_id, checked)))
    widget._fill_items([done_item])
    value_item = widget.table_items.item(0, _COL_VALUE)
    assert value_item is not None
    assert not (value_item.flags() & Qt.ItemFlag.ItemIsEditable)
    cell = widget.table_items.cellWidget(0, 0)
    assert cell is not None
    checkbox = cell.findChild(QCheckBox)
    assert checkbox is not None
    assert checkbox.isEnabled()
    assert checkbox.isChecked()
    checkbox.click()
    assert received == [(2, False)]
    widget.close()


def test_workouts_table_stretches_and_alternates_row_colors() -> None:
    """Items table fills width and paints alternating row backgrounds."""
    assert _qapp() is not None
    second = WorkoutItemRow(
        id=2,
        workout_id=1,
        exercise_id=3,
        type_id=3,
        exercise_name="Squat",
        type_name="Bodyweight",
        target_value="15",
        sort_order=1,
        is_done=False,
        process_id=None,
        unit="times",
        calories_per_unit=1.0,
        calories_modifier=1.0,
    )
    widget = WorkoutsWidget()
    widget._fill_items([_sample_item(), second])
    table = widget.table_items
    header = table.horizontalHeader()
    assert header.sectionResizeMode(_COL_EXERCISE) == header.ResizeMode.Stretch
    assert header.sectionResizeMode(_COL_KCAL) == header.ResizeMode.Interactive
    first_bg = table.item(0, _COL_EXERCISE).background().color()
    second_bg = table.item(1, _COL_EXERCISE).background().color()
    assert first_bg != second_bg
    widget.close()


def test_workout_session_shows_timer_bar_and_hides_start() -> None:
    """Starting a session shows the top stopwatch bar and hides Start."""
    assert _qapp() is not None
    widget = WorkoutsWidget()
    widget._current_workout_id = 1
    widget._session_active = True
    widget._session_workout_id = 1
    widget._session_elapsed.start()
    widget._session_bar.show()
    widget._update_start_button()
    widget._update_session_ui_locked()
    widget.show()
    _qapp().processEvents()

    assert widget.is_workout_session_active()
    assert widget._session_bar.isVisible()
    assert widget.button_continue.isVisible()
    assert not widget.button_start.isVisible()
    assert not widget.list_workouts.isEnabled()

    widget.stop_workout_session(completed=False)
    assert not widget.is_workout_session_active()
    assert not widget._session_bar.isVisible()
    assert widget.button_start.isVisible()
    widget.close()


def test_workout_session_continue_emits_current_incomplete(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _qapp() is not None
    widget = WorkoutsWidget()
    widget._session_active = True
    widget._session_workout_id = 1
    widget._current_workout_id = 1
    emitted: list[int] = []
    widget.workout_session_started.connect(emitted.append)
    monkeypatch.setattr(widget, "_first_incomplete_item_id", lambda: 42)
    widget._continue_workout_session()
    assert emitted == [42]
    widget.close()


def test_workout_session_highlights_current_incomplete_row(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _qapp() is not None
    widget = WorkoutsWidget()
    items = [
        _sample_item(),
        WorkoutItemRow(
            id=2,
            workout_id=1,
            exercise_id=3,
            type_id=3,
            exercise_name="Squat",
            type_name="Bodyweight",
            target_value="20",
            sort_order=1,
            is_done=False,
            process_id=None,
            unit="times",
            calories_per_unit=1.0,
            calories_modifier=1.0,
        ),
    ]
    widget._session_active = True
    monkeypatch.setattr(widget, "_first_incomplete_item_id", lambda: 1)
    widget._fill_items(items)
    assert widget.table_items.item(0, _COL_EXERCISE).background().color() == _ROW_COLOR_CURRENT
    assert widget.table_items.item(1, _COL_EXERCISE).background().color() != _ROW_COLOR_CURRENT
    widget.close()


def test_workout_session_saves_and_pops_exercise_timer_state() -> None:
    assert _qapp() is not None
    widget = WorkoutsWidget()
    state = ExerciseStopwatchState(phase=StopwatchPhase.RUNNING, elapsed_ms=1200, running=True)
    widget.save_exercise_timer_state(7, state)
    assert widget.pop_exercise_timer_state(99) is None
    restored = widget.pop_exercise_timer_state(7)
    assert restored == state
    assert widget.pop_exercise_timer_state(7) is None
    widget.close()


def test_workout_session_shows_running_exercise_timer() -> None:
    assert _qapp() is not None
    widget = WorkoutsWidget()
    widget.show()
    widget._session_bar.show()
    state = ExerciseStopwatchState(phase=StopwatchPhase.RUNNING, elapsed_ms=4500, running=True)
    widget.save_exercise_timer_state(3, state)
    assert not widget.label_exercise_timer.isHidden()
    assert widget.label_exercise_timer.text() == "0:04"
    widget._tick_exercise_timer()
    assert widget.label_exercise_timer.text() == "0:05"
    assert widget._exercise_timer_state is not None
    assert widget._exercise_timer_state.elapsed_ms == 5500
    paused = ExerciseStopwatchState(phase=StopwatchPhase.RUNNING, elapsed_ms=5500, running=False)
    widget.save_exercise_timer_state(3, paused)
    assert widget.label_exercise_timer.isHidden()
    widget.close()


def test_workout_session_timer_label_starts_at_zero() -> None:
    """The workout timer label uses M:SS formatting from zero."""
    assert _qapp() is not None
    widget = WorkoutsWidget()
    widget._update_session_timer_label()
    assert widget.label_session_timer.text() == "0:00"
    widget.close()


def test_workouts_empty_button_is_next_to_new() -> None:
    """Empty sits beside New and is locked during a session."""
    assert _qapp() is not None
    widget = WorkoutsWidget()
    emitted: list[bool] = []
    widget.empty_requested.connect(lambda: emitted.append(True))
    assert widget.button_new_empty is not None
    assert widget.button_new_empty.isEnabled()
    widget.button_new_empty.click()
    assert emitted == [True]

    widget._session_active = True
    widget._update_session_ui_locked()
    assert not widget.button_new_empty.isEnabled()
    assert not widget.button_new.isEnabled()
    widget.close()


def test_workouts_add_exercise_button_emits_workout_id() -> None:
    """Add exercise is off until a workout is selected, then emits that workout id."""
    assert _qapp() is not None
    widget = WorkoutsWidget()
    emitted: list[int] = []
    widget.add_exercise_requested.connect(emitted.append)
    assert widget.button_add_exercise is not None
    assert not widget.button_add_exercise.isEnabled()

    widget._db = cast("DatabaseManager", MagicMock())
    widget._current_workout_id = 7
    widget._update_add_exercise_button()
    assert widget.button_add_exercise.isEnabled()

    widget._request_add_exercise()
    assert emitted == [7]

    widget._session_active = True
    widget._update_add_exercise_button()
    assert not widget.button_add_exercise.isEnabled()
    widget.close()
