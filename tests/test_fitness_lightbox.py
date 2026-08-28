"""Tests for the Fitness exercise lightbox timer, form, and overlay."""

from __future__ import annotations

from pathlib import Path

import pillow_avif  # noqa: F401
import pytest
from PIL import Image
from PySide6.QtWidgets import QApplication, QSplitter, QWidget

from harrix_swiss_knife.apps.common.apps_config import (
    DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS,
    get_apps_fitness_lightbox_countdown_seconds,
)
from harrix_swiss_knife.apps.common.avif_manager import AvifManager
from harrix_swiss_knife.apps.fitness.database_manager import WorkoutItemRow
from harrix_swiss_knife.apps.fitness.fitness_lightbox import FitnessExerciseLightboxDialog
from harrix_swiss_knife.apps.fitness.lightbox_logic import (
    ExerciseStopwatch,
    FitnessLightboxConfirm,
    FitnessLightboxDetails,
    StopwatchColor,
    StopwatchPhase,
    allocated_exercise_seconds,
    default_exercise_type,
    format_mm_ss,
    parse_exercise_value,
)
from harrix_swiss_knife.apps.fitness.lightbox_sounds import fitness_timer_cue_sound_name


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _write_test_avif(path: Path) -> None:
    Image.new("RGB", (64, 48), (120, 80, 40)).save(path, format="AVIF")


def _details(_name: str, _item_id: int | None) -> FitnessLightboxDetails:
    return FitnessLightboxDetails(unit="times", types=["Wide", "Narrow"], selected_type="Wide", value=10)


def _item(*, item_id: int, name: str, sort_order: int) -> WorkoutItemRow:
    return WorkoutItemRow(
        id=item_id,
        workout_id=1,
        exercise_id=item_id,
        type_id=3,
        exercise_name=name,
        type_name="Wide",
        target_value="12",
        sort_order=sort_order,
        is_done=False,
        process_id=None,
        unit="times",
        calories_per_unit=1.0,
        calories_modifier=1.0,
    )


def test_get_apps_fitness_lightbox_countdown_seconds_defaults_to_five() -> None:
    assert get_apps_fitness_lightbox_countdown_seconds({}) == DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS
    assert get_apps_fitness_lightbox_countdown_seconds({"apps": {}}) == 5
    assert get_apps_fitness_lightbox_countdown_seconds({"apps": {"fitness_lightbox_countdown_seconds": 8}}) == 8
    assert get_apps_fitness_lightbox_countdown_seconds({"apps": {"fitness_lightbox_countdown_seconds": 0}}) == 0
    assert get_apps_fitness_lightbox_countdown_seconds({"apps": {"fitness_lightbox_countdown_seconds": -3}}) == 0
    assert get_apps_fitness_lightbox_countdown_seconds({"apps": {"fitness_lightbox_countdown_seconds": "nope"}}) == 5


def test_allocated_exercise_seconds_splits_workout_evenly() -> None:
    assert allocated_exercise_seconds(45, 15) == 180
    assert allocated_exercise_seconds(0, 10) == 0
    assert allocated_exercise_seconds(30, 0) == 0
    assert allocated_exercise_seconds(10, 3) == 200


def test_default_exercise_type_prefers_plan_then_last_then_first() -> None:
    types = ["Wide", "Narrow"]
    assert default_exercise_type(types, preferred="Narrow", last_used="Wide") == "Narrow"
    assert default_exercise_type(types, preferred="", last_used="Wide") == "Wide"
    assert default_exercise_type(types, preferred="", last_used="") == "Wide"
    assert default_exercise_type([], preferred="Wide", last_used="Wide") == ""


def test_parse_exercise_value_and_format_mm_ss() -> None:
    assert parse_exercise_value("12") == 12
    assert parse_exercise_value("12.9") == 12
    assert parse_exercise_value("bad") == 0
    assert format_mm_ss(0) == "0:00"
    assert format_mm_ss(75) == "1:15"


def test_stopwatch_countdown_then_elapsed_then_overtime() -> None:
    watch = ExerciseStopwatch(countdown_seconds=2, limit_seconds=3)
    idle = watch.snapshot()
    assert idle.phase is StopwatchPhase.IDLE
    assert idle.color is StopwatchColor.IDLE
    started = watch.start()
    assert started.phase is StopwatchPhase.COUNTDOWN
    assert started.color is StopwatchColor.COUNTDOWN
    assert started.display_seconds == 2
    after_one = watch.advance(1000)
    assert after_one.phase is StopwatchPhase.COUNTDOWN
    assert after_one.display_seconds == 1
    running = watch.advance(1000)
    assert running.phase is StopwatchPhase.RUNNING
    assert running.color is StopwatchColor.RUNNING
    assert running.display_seconds == 0
    later = watch.advance(3000)
    assert later.is_overtime
    assert later.color is StopwatchColor.OVERTIME
    assert later.display_seconds == 3
    paused = watch.pause()
    assert not paused.is_running
    watch.advance(5000)
    assert watch.snapshot().display_seconds == 3
    restarted = watch.restart()
    assert restarted.phase is StopwatchPhase.COUNTDOWN
    assert not restarted.is_overtime


def test_stopwatch_skips_countdown_when_zero() -> None:
    watch = ExerciseStopwatch(countdown_seconds=0, limit_seconds=None)
    started = watch.start()
    assert started.phase is StopwatchPhase.RUNNING
    assert started.color is StopwatchColor.RUNNING
    assert not started.is_overtime


def test_fitness_timer_cue_sound_names() -> None:
    assert fitness_timer_cue_sound_name("start") == "fitness_timer_start.wav"
    assert fitness_timer_cue_sound_name("finish") == "fitness_timer_finish.wav"


def test_fitness_lightbox_flashes_start_and_finish(
    tmp_path: Path,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Push-ups.avif")
    manager = AvifManager(img_dir)
    cues: list[str] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_cue",
        lambda cue: cues.append(cue),
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_alert",
        lambda: None,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.stop_fitness_timer_alert",
        lambda: None,
    )
    dialog = FitnessExerciseLightboxDialog(
        ["Push-ups"],
        avif_manager=manager,
        details_loader=_details,
        confirm_handler=lambda _payload: True,
        countdown_seconds=1,
        workout_duration_min=1,
        workout_items=[_item(item_id=1, name="Push-ups", sort_order=0)],
    )
    dialog._sidebar._on_start()
    assert dialog._sidebar._prepare_label.text() == "Prepare!"
    assert not dialog._sidebar._prepare_label.isHidden()
    dialog._sidebar._apply_snapshot(dialog._sidebar._stopwatch.advance(1000))
    assert cues == ["start"]
    assert dialog._sidebar._prepare_label.text() == "Start"
    assert not dialog._sidebar._prepare_label.isHidden()
    dialog._sidebar._apply_snapshot(dialog._sidebar._stopwatch.advance(60_000))
    assert cues == ["start", "finish"]
    assert dialog._sidebar._prepare_label.text() == "Finish"
    assert not dialog._sidebar._prepare_label.isHidden()
    dialog.close()


def test_fitness_lightbox_has_splitter_sidebar_and_browse_confirm(
    tmp_path: Path,
    qapp: QApplication,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Push-ups.avif")
    _write_test_avif(img_dir / "Squats.avif")
    manager = AvifManager(img_dir)
    confirmed: list[FitnessLightboxConfirm] = []

    def _confirm(payload: FitnessLightboxConfirm) -> bool:
        confirmed.append(payload)
        return True

    owner = QWidget()
    owner.resize(900, 600)
    owner.show()
    qapp.processEvents()
    dialog = FitnessExerciseLightboxDialog(
        ["Push-ups", "Squats"],
        avif_manager=manager,
        details_loader=_details,
        confirm_handler=_confirm,
        parent=owner,
        countdown_seconds=5,
    )
    chrome = dialog.chrome_rect()
    assert chrome.x() >= 200
    assert chrome.width() > 400
    assert dialog._close_button.x() > dialog.width() // 2
    assert dialog._previous_button.x() >= chrome.x()
    dialog.show()
    qapp.processEvents()
    assert dialog._splitter is not None
    assert isinstance(dialog._splitter, QSplitter)
    assert dialog._splitter.count() == 2
    assert dialog._image_host is not None
    assert dialog._label.width() >= dialog._image_host.width() - 2
    assert dialog._label.height() >= dialog._image_host.height() - 2
    assert dialog._label.width() > 400
    assert dialog._sidebar._title.text() == "Push-ups"
    assert dialog._sidebar.value() == 10
    assert dialog._sidebar.selected_type() == "Wide"
    assert dialog._sidebar._prepare_label.isHidden()
    dialog._sidebar._on_start()
    assert dialog._sidebar._prepare_label.text() == "Prepare!"
    assert not dialog._sidebar._prepare_label.isHidden()
    dialog._sidebar.reset_timer()
    assert dialog._sidebar._prepare_label.isHidden()
    assert dialog.chrome_rect().x() > 0
    dialog._sidebar.confirm_requested.emit()
    qapp.processEvents()
    assert len(confirmed) == 1
    assert confirmed[0].exercise_name == "Push-ups"
    assert confirmed[0].workout_item_id is None
    assert dialog.should_open_sets_tab
    dialog.close()
    owner.close()


def test_fitness_lightbox_workout_arrows_skip_confirm_and_confirm_advances(
    tmp_path: Path,
    qapp: QApplication,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Push-ups.avif")
    _write_test_avif(img_dir / "Squats.avif")
    manager = AvifManager(img_dir)
    confirmed: list[FitnessLightboxConfirm] = []

    def _confirm(payload: FitnessLightboxConfirm) -> bool:
        confirmed.append(payload)
        return True

    items = [_item(item_id=11, name="Push-ups", sort_order=0), _item(item_id=12, name="Squats", sort_order=1)]
    dialog = FitnessExerciseLightboxDialog(
        ["Push-ups", "Squats"],
        avif_manager=manager,
        details_loader=_details,
        confirm_handler=_confirm,
        workout_items=items,
        workout_duration_min=10,
        countdown_seconds=5,
        auto_start_prepare=True,
    )
    assert dialog._limit_seconds == allocated_exercise_seconds(10, 2)
    assert not dialog._sidebar._limit_label.isHidden()
    assert dialog._sidebar._prepare_label.text() == "Prepare!"
    assert not dialog._sidebar._prepare_label.isHidden()
    dialog.show_next()
    assert dialog.current_index == 1
    assert dialog._sidebar._title.text() == "Squats"
    assert not dialog._sidebar._prepare_label.isHidden()
    assert confirmed == []
    dialog.show_previous()
    assert dialog.current_index == 0
    dialog._sidebar.confirm_requested.emit()
    qapp.processEvents()
    assert len(confirmed) == 1
    assert confirmed[0].workout_item_id == 11
    assert dialog.current_index == 1
    assert not dialog.should_open_sets_tab
    dialog.close()
