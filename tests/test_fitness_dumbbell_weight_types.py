"""Tests for copying dumbbell weight types from the template exercise."""

from __future__ import annotations

from harrix_swiss_knife.apps.fitness.dumbbell_weight_types import (
    DUMBBELL_WEIGHT_TEMPLATE_EXERCISE,
    ExerciseWeightSnapshot,
    WeightTypeSpec,
    exercises_needing_weight_sync,
    is_template_exercise,
    missing_weight_types,
    shares_template_weight_types,
)

_TEMPLATE = (
    WeightTypeSpec("1 kg", 1.0, "1 кг"),
    WeightTypeSpec("6.5 kg", 1.0, "6,5 кг"),
    WeightTypeSpec("9 kg", 1.0, "9 кг"),
    WeightTypeSpec("11.5 kg", 1.0, "11,5 кг"),
    WeightTypeSpec("14 kg", 1.0, "14 кг"),
)


def test_missing_weight_types_skips_existing_and_duplicates() -> None:
    """Only new template weights are returned, matching names case-insensitively."""
    missing = missing_weight_types(["9 KG", "14 kg"], _TEMPLATE)
    assert [spec.name for spec in missing] == ["1 kg", "6.5 kg", "11.5 kg"]


def test_missing_weight_types_returns_all_when_empty() -> None:
    """An exercise without types receives the full template list."""
    missing = missing_weight_types([], _TEMPLATE)
    assert missing == list(_TEMPLATE)


def test_shares_template_weight_types_requires_overlap() -> None:
    """Exercises match the template only when they already share a weight name."""
    template_names = [spec.name for spec in _TEMPLATE]
    assert shares_template_weight_types(["9 kg", "Custom"], template_names)
    assert not shares_template_weight_types(["Band", "Bodyweight"], template_names)


def test_is_template_exercise_ignores_case_and_spaces() -> None:
    """The template exercise is recognized regardless of case or padding."""
    assert is_template_exercise(f"  {DUMBBELL_WEIGHT_TEMPLATE_EXERCISE.upper()}  ")
    assert not is_template_exercise("Dumbbell fly")


def test_exercises_needing_weight_sync_skips_template_and_unrelated() -> None:
    """Sync targets already use a template weight and are missing at least one."""
    curls = ExerciseWeightSnapshot(1, DUMBBELL_WEIGHT_TEMPLATE_EXERCISE, ("1 kg", "14 kg"))
    press = ExerciseWeightSnapshot(2, "Dumbbell shoulder press", ("9 kg",))
    plank = ExerciseWeightSnapshot(3, "Plank", ("Bodyweight",))
    complete = ExerciseWeightSnapshot(4, "Dumbbell row", tuple(spec.name for spec in _TEMPLATE))

    targets = exercises_needing_weight_sync((curls, press, plank, complete), _TEMPLATE)
    assert [exercise.name for exercise, _missing in targets] == ["Dumbbell shoulder press"]
    assert [spec.name for spec in targets[0][1]] == ["1 kg", "6.5 kg", "11.5 kg", "14 kg"]
