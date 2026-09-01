"""Tests for the Fitness exercise lightbox timer, form, and overlay."""

from __future__ import annotations

from pathlib import Path

import pillow_avif  # noqa: F401
import pytest
from PIL import Image
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QPushButton, QSplitter, QWidget

from harrix_swiss_knife import resources_rc  # noqa: F401
from harrix_swiss_knife.apps.common.apps_config import (
    DEFAULT_FITNESS_LIGHTBOX_COUNTDOWN_SECONDS,
    get_apps_fitness_lightbox_countdown_seconds,
)
from harrix_swiss_knife.apps.common.avif_manager import AvifManager
from harrix_swiss_knife.apps.fitness.database_manager import WorkoutItemRow
from harrix_swiss_knife.apps.fitness.fitness_lightbox import (
    FitnessExerciseLightboxDialog,
    LightboxPhaseOverlay,
)
from harrix_swiss_knife.apps.fitness.lightbox_logic import (
    ExerciseStopwatch,
    ExerciseStopwatchState,
    FitnessLightboxConfirm,
    FitnessLightboxDetails,
    LightboxOverlayKind,
    StopwatchColor,
    StopwatchPhase,
    allocated_exercise_seconds,
    default_exercise_type,
    format_mm_ss,
    is_seconds_exercise_unit,
    lightbox_playback_view,
    minutes_seconds_to_total,
    parse_exercise_value,
    split_total_seconds,
    target_seconds_for_exercise,
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


def _overlay(dialog: FitnessExerciseLightboxDialog) -> LightboxPhaseOverlay:
    overlay = dialog._phase_overlay
    assert overlay is not None
    return overlay


def _details(_name: str, _item_id: int | None) -> FitnessLightboxDetails:
    return FitnessLightboxDetails(unit="times", types=["Wide", "Narrow"], selected_type="Wide", value=10)


def _plank_details(_name: str, _item_id: int | None) -> FitnessLightboxDetails:
    return FitnessLightboxDetails(unit="sec.", types=[], selected_type="", value=5)


def _item(
    *,
    item_id: int,
    name: str,
    sort_order: int,
    target: str = "12",
    unit: str = "times",
) -> WorkoutItemRow:
    return WorkoutItemRow(
        id=item_id,
        workout_id=1,
        exercise_id=item_id,
        type_id=3,
        exercise_name=name,
        type_name="Wide",
        target_value=target,
        sort_order=sort_order,
        is_done=False,
        process_id=None,
        unit=unit,
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
    assert default_exercise_type(types, preferred="", last_used="") == ""
    assert default_exercise_type(types, preferred="", last_used="", type_required=True) == "Wide"
    assert default_exercise_type(types, preferred="", last_used="Narrow", type_required=True) == "Narrow"
    assert default_exercise_type([], preferred="Wide", last_used="Wide", type_required=True) == ""


def test_seconds_exercise_unit_and_minute_second_split() -> None:
    assert is_seconds_exercise_unit("sec.")
    assert is_seconds_exercise_unit("seconds")
    assert not is_seconds_exercise_unit("min")
    assert not is_seconds_exercise_unit("times")
    assert split_total_seconds(90) == (1, 30)
    assert split_total_seconds(5) == (0, 5)
    assert split_total_seconds(0) == (0, 0)
    assert minutes_seconds_to_total(1, 30) == 90
    assert minutes_seconds_to_total(0, 45) == 45


def test_parse_exercise_value_and_format_mm_ss() -> None:
    assert parse_exercise_value("12") == 12
    assert parse_exercise_value("12.9") == 12
    assert parse_exercise_value("bad") == 0
    assert format_mm_ss(0) == "0:00"
    assert format_mm_ss(75) == "1:15"


def test_target_seconds_for_timed_exercise_units() -> None:
    assert target_seconds_for_exercise("sec.", 5) == 5
    assert target_seconds_for_exercise("seconds", 12) == 12
    assert target_seconds_for_exercise("min", 2) == 120
    assert target_seconds_for_exercise("times", 5) is None
    assert target_seconds_for_exercise("sec.", 0) is None


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
    assert later.is_running
    paused = watch.pause()
    assert not paused.is_running
    watch.advance(5000)
    assert watch.snapshot().display_seconds == 3
    restarted = watch.restart()
    assert restarted.phase is StopwatchPhase.COUNTDOWN
    assert not restarted.is_overtime


def test_stopwatch_stops_at_timed_exercise_limit() -> None:
    watch = ExerciseStopwatch(countdown_seconds=0, limit_seconds=5, stop_at_limit=True)
    watch.start()
    snapshot = watch.advance(5000)
    assert snapshot.phase is StopwatchPhase.FINISHED
    assert snapshot.is_overtime
    assert snapshot.display_seconds == 5
    assert not snapshot.is_running
    watch.advance(2000)
    assert watch.snapshot().display_seconds == 5
    assert watch.snapshot().phase is StopwatchPhase.FINISHED
    assert not watch.snapshot().is_running


def test_stopwatch_stop_marks_finished() -> None:
    watch = ExerciseStopwatch(countdown_seconds=2, limit_seconds=10)
    watch.start()
    watch.advance(500)
    stopped = watch.stop()
    assert stopped.phase is StopwatchPhase.FINISHED
    assert not stopped.is_running
    assert stopped.is_overtime
    watch.advance(2000)
    assert watch.snapshot().phase is StopwatchPhase.FINISHED
    started = watch.start()
    assert started.phase is StopwatchPhase.COUNTDOWN
    assert started.is_running


def test_lightbox_playback_view_prepare_run_and_finish() -> None:
    countdown = ExerciseStopwatch(countdown_seconds=3, limit_seconds=None).start()
    assert lightbox_playback_view(countdown).overlay is LightboxOverlayKind.PREPARE
    assert lightbox_playback_view(countdown).countdown_seconds == 3
    assert not lightbox_playback_view(countdown).animate
    running = ExerciseStopwatch(countdown_seconds=0, limit_seconds=None).start()
    view = lightbox_playback_view(running)
    assert view.overlay is LightboxOverlayKind.NONE
    assert view.animate
    finished = ExerciseStopwatch(countdown_seconds=0, limit_seconds=5, stop_at_limit=True)
    finished.start()
    finish_view = lightbox_playback_view(finished.advance(5000))
    assert finish_view.overlay is LightboxOverlayKind.FINISH
    assert not finish_view.animate
    assert finish_view.freeze_first_frame


def test_stopwatch_capture_and_restore_resumes_elapsed() -> None:
    watch = ExerciseStopwatch(countdown_seconds=0, limit_seconds=10)
    watch.start()
    watch.advance(2500)
    state = watch.capture_state()
    assert state.phase is StopwatchPhase.RUNNING
    assert state.elapsed_ms == 2500
    assert state.running
    restored = ExerciseStopwatch(countdown_seconds=0, limit_seconds=10)
    snapshot = restored.apply_state(state)
    assert snapshot.phase is StopwatchPhase.RUNNING
    assert snapshot.display_seconds == 2
    assert snapshot.is_running
    restored.advance(800)
    assert restored.snapshot().display_seconds == 3


def test_stopwatch_skips_countdown_when_zero() -> None:
    watch = ExerciseStopwatch(countdown_seconds=0, limit_seconds=None)
    started = watch.start()
    assert started.phase is StopwatchPhase.RUNNING
    assert started.color is StopwatchColor.RUNNING
    assert not started.is_overtime


def test_fitness_timer_cue_sound_names() -> None:
    assert fitness_timer_cue_sound_name("ready") == "fitness_ready.wav"
    assert fitness_timer_cue_sound_name("go") == "fitness_go.wav"
    assert fitness_timer_cue_sound_name("time_over") == "fitness_time_over.wav"
    assert fitness_timer_cue_sound_name("paste") == "fitness_paste.wav"
    assert fitness_timer_cue_sound_name("pause") == "fitness_pause.wav"
    assert fitness_timer_cue_sound_name("continue") == "fitness_continue.wav"
    assert fitness_timer_cue_sound_name("success") == "fitness_success.wav"
    assert fitness_timer_cue_sound_name("applause") == "fitness_applause.wav"
    assert fitness_timer_cue_sound_name("congratulations") == "fitness_congratulations.wav"


def test_fitness_applause_sound_is_embedded(qapp: QApplication) -> None:  # noqa: ARG001
    """Record-congratulations WAV is compiled into Qt resources."""
    assert QFile.exists(":/assets/sounds/fitness_applause.wav")


def test_fitness_lightbox_flashes_start_and_finish(
    tmp_path: Path,
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Push-ups.avif")
    manager = AvifManager(img_dir)
    cues: list[str] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_cue",
        cues.append,
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
    assert dialog._sidebar._prepare_label.isHidden()
    overlay = _overlay(dialog)
    assert not overlay.isHidden()
    assert overlay._title.text() == "Prepare"
    assert overlay._number.text() == "1"
    assert cues == ["ready", "1"]
    dialog._sidebar._apply_snapshot(dialog._sidebar._stopwatch.advance(1000))
    assert cues == ["ready", "1", "go"]
    assert overlay.isHidden()
    assert dialog._sidebar._prepare_label.isHidden()
    dialog._sidebar._apply_snapshot(dialog._sidebar._stopwatch.advance(60_000))
    assert cues == ["ready", "1", "go"]
    assert not overlay.isHidden()
    assert overlay._title.text() == "Finish"
    assert overlay._number.isHidden()
    assert dialog._sidebar._prepare_label.isHidden()
    dialog.close()


def test_fitness_lightbox_stops_on_timed_exercise_target(
    tmp_path: Path,
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Plank.avif")
    manager = AvifManager(img_dir)
    cues: list[str] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_cue",
        cues.append,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.stop_fitness_timer_alert",
        lambda: None,
    )
    dialog = FitnessExerciseLightboxDialog(
        ["Plank"],
        avif_manager=manager,
        details_loader=_plank_details,
        confirm_handler=lambda _payload: True,
        countdown_seconds=0,
        workout_duration_min=10,
        workout_items=[_item(item_id=1, name="Plank", sort_order=0, target="5")],
    )
    assert dialog._sidebar._limit_seconds == 5
    assert dialog._sidebar._limit_label.text() == "Target 0:05"
    dialog._sidebar._on_start()
    dialog._sidebar._apply_snapshot(dialog._sidebar._stopwatch.advance(5000))
    assert cues == ["go", "time_over"]
    assert dialog._sidebar._prepare_label.isHidden()
    overlay = _overlay(dialog)
    assert not overlay.isHidden()
    assert overlay._title.text() == "Finish"
    assert dialog._sidebar._time_label.text() == "0:05"
    assert not dialog._sidebar._stopwatch.snapshot().is_running
    assert dialog._sidebar._stopwatch.snapshot().phase is StopwatchPhase.FINISHED
    dialog.close()


def test_fitness_lightbox_pause_and_continue_cues(
    tmp_path: Path,
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Plank.avif")
    manager = AvifManager(img_dir)
    cues: list[str] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_cue",
        cues.append,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.stop_fitness_timer_alert",
        lambda: None,
    )
    dialog = FitnessExerciseLightboxDialog(
        ["Plank"],
        avif_manager=manager,
        details_loader=_plank_details,
        confirm_handler=lambda _payload: True,
        countdown_seconds=0,
        workout_duration_min=10,
        workout_items=[_item(item_id=1, name="Plank", sort_order=0, target="30")],
    )
    dialog._sidebar._on_start()
    assert cues == ["go"]
    dialog._sidebar._on_pause()
    assert cues == ["go", "pause"]
    dialog._sidebar._on_start()
    assert cues == ["go", "pause", "continue"]
    dialog.close()


def test_fitness_lightbox_restores_timer_state_without_prepare(
    tmp_path: Path,
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Push-ups.avif")
    manager = AvifManager(img_dir)
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_cue",
        lambda _cue: None,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.stop_fitness_timer_alert",
        lambda: None,
    )
    state = ExerciseStopwatchState(phase=StopwatchPhase.RUNNING, elapsed_ms=4500, running=True)
    dialog = FitnessExerciseLightboxDialog(
        ["Push-ups"],
        avif_manager=manager,
        details_loader=_details,
        confirm_handler=lambda _payload: True,
        countdown_seconds=5,
        workout_duration_min=1,
        workout_items=[_item(item_id=1, name="Push-ups", sort_order=0)],
        auto_start_prepare=True,
        initial_timer_state=state,
    )
    assert dialog._sidebar._prepare_label.isHidden()
    assert _overlay(dialog).isHidden()
    assert dialog._sidebar._time_label.text() == "0:04"
    assert dialog._sidebar._tick.isActive()
    dialog.close()
    item_id, captured = dialog.captured_timer_state()
    assert item_id == 1
    assert captured is not None
    assert captured.phase is StopwatchPhase.RUNNING
    assert captured.elapsed_ms >= 4500


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
    assert dialog._sidebar._prepare_label.isHidden()
    overlay = _overlay(dialog)
    assert not overlay.isHidden()
    assert overlay._title.text() == "Prepare"
    assert overlay._number.text() == "5"
    stop = dialog.findChild(QPushButton, "fitnessLightboxStopButton")
    assert stop is not None
    assert stop.text() == "⏹ Stop"
    assert "background: transparent" in dialog._sidebar.styleSheet()
    assert "border: none" in dialog._sidebar.styleSheet()
    assert "border-radius: 0" in dialog._sidebar.styleSheet()
    assert dialog._splitter is not None
    assert "::handle:hover" in dialog._splitter.styleSheet()
    assert "#9CA3AF" in dialog._splitter.styleSheet()
    dialog._toggle_backdrop_color()
    assert dialog._backdrop_color == "black"
    assert "background: black" in dialog._splitter.styleSheet()
    dialog._sidebar.reset_timer()
    assert dialog._sidebar._prepare_label.isHidden()
    assert overlay.isHidden()
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
    overlay = _overlay(dialog)
    assert dialog._sidebar._prepare_label.isHidden()
    assert not overlay.isHidden()
    assert overlay._title.text() == "Prepare"
    dialog.show_next()
    assert dialog.current_index == 1
    assert dialog._sidebar._title.text() == "Squats"
    assert not overlay.isHidden()
    assert overlay._title.text() == "Prepare"
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


def test_fitness_lightbox_stop_button_shows_finish_overlay(
    tmp_path: Path,
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    img_dir = tmp_path / "fitness_img"
    img_dir.mkdir()
    _write_test_avif(img_dir / "Plank.avif")
    manager = AvifManager(img_dir)
    cues: list[str] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.play_fitness_timer_cue",
        cues.append,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.fitness.fitness_lightbox.stop_fitness_timer_alert",
        lambda: None,
    )
    dialog = FitnessExerciseLightboxDialog(
        ["Plank"],
        avif_manager=manager,
        details_loader=_plank_details,
        confirm_handler=lambda _payload: True,
        countdown_seconds=0,
        workout_duration_min=10,
        workout_items=[_item(item_id=1, name="Plank", sort_order=0, target="30")],
    )
    dialog._sidebar._on_start()
    assert _overlay(dialog).isHidden()
    dialog._sidebar._on_stop()
    overlay = _overlay(dialog)
    assert not overlay.isHidden()
    assert overlay._title.text() == "Finish"
    assert dialog._sidebar._prepare_label.isHidden()
    assert dialog._sidebar._stopwatch.snapshot().phase is StopwatchPhase.FINISHED
    assert cues == ["go", "time_over"]
    dialog.close()
