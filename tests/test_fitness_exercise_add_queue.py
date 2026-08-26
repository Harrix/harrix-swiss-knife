"""Tests for queued Add Exercise jobs and name conflicts."""

from __future__ import annotations

from harrix_swiss_knife.apps.fitness.exercise_add_queue import (
    PendingExerciseAdd,
    find_queued_exercise_conflict,
)


def _job(
    *,
    name: str = "Push-ups",
    unit: str = "times",
    is_type_required: bool = False,
    calories_per_unit: float = 0.4,
    name_local: str = "Отжимания",
    is_favorite: bool = False,
    media_path: str = "",
    with_dumbbells: bool = False,
    auto_fill: bool = False,
) -> PendingExerciseAdd:
    return PendingExerciseAdd(
        name=name,
        unit=unit,
        is_type_required=is_type_required,
        calories_per_unit=calories_per_unit,
        name_local=name_local,
        is_favorite=is_favorite,
        media_path=media_path,
        with_dumbbells=with_dumbbells,
        auto_fill=auto_fill,
    )


def test_from_dialog_result_strips_and_marks_auto_fill() -> None:
    job = PendingExerciseAdd.from_dialog_result(
        ("  ", "times", False, 0.0, "  Приседания  ", False, r"D:\img\squat.mp4", False),
    )
    assert job.name == ""
    assert job.name_local == "Приседания"
    assert job.media_path == r"D:\img\squat.mp4"
    assert job.auto_fill
    assert not job.is_type_required


def test_from_dialog_result_dumbbells_require_type() -> None:
    job = PendingExerciseAdd.from_dialog_result(
        ("Curl", "times", False, 1.0, "Сгибания", True, "", True),
    )
    assert job.with_dumbbells
    assert job.is_type_required
    assert not job.auto_fill


def test_find_queued_exercise_conflict_matches_name_or_local() -> None:
    jobs = [
        _job(name="Squat", name_local="Приседания"),
        _job(name="Push-ups", name_local="Отжимания"),
    ]
    by_name = find_queued_exercise_conflict(jobs, "squat", "")
    assert by_name is not None
    assert by_name.name == "Squat"
    by_local = find_queued_exercise_conflict(jobs, "", "отжимания")
    assert by_local is not None
    assert by_local.name_local == "Отжимания"
    assert find_queued_exercise_conflict(jobs, "Plank", "Планка") is None


def test_find_queued_exercise_conflict_ignores_blank_names() -> None:
    jobs = [_job(name="", name_local="Приседания")]
    assert find_queued_exercise_conflict(jobs, "", "") is None
    assert find_queued_exercise_conflict(jobs, "Squat", "") is None
    match = find_queued_exercise_conflict(jobs, "Squat", "Приседания")
    assert match is not None
    assert match.name_local == "Приседания"
