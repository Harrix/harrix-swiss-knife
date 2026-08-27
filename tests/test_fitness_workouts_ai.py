"""Tests for workout TSV parsing and catalog formatting."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.apps_config import (
    DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT,
    get_apps_fitness_workout_history_count,
)
from harrix_swiss_knife.apps.fitness.sets_ai import (
    ExerciseCatalogEntry,
    ExerciseTypeCatalog,
    ParsedSetRow,
    build_exercise_catalog,
)
from harrix_swiss_knife.apps.fitness.workouts_ai import (
    estimate_workout_duration_min,
    format_recent_sets,
    format_workout_exercise_catalog,
    parse_workout_tsv,
    recalculate_workout_duration,
    resolve_workout_item,
)


def test_get_apps_fitness_workout_history_count_defaults_to_100() -> None:
    assert get_apps_fitness_workout_history_count({}) == DEFAULT_FITNESS_WORKOUT_HISTORY_COUNT
    assert get_apps_fitness_workout_history_count({"apps": {}}) == 100
    assert get_apps_fitness_workout_history_count({"apps": {"fitness_workout_history_count": 25}}) == 25
    assert get_apps_fitness_workout_history_count({"apps": {"fitness_workout_history_count": 0}}) == 1
    assert get_apps_fitness_workout_history_count({"apps": {"fitness_workout_history_count": "nope"}}) == 100


def test_recalculate_workout_duration_scales_and_clamps() -> None:
    assert recalculate_workout_duration(45, remaining_count=8, previous_count=9) == 40
    assert recalculate_workout_duration(45, remaining_count=0, previous_count=9) == 45
    assert recalculate_workout_duration(10, remaining_count=1, previous_count=10) == 1
    assert recalculate_workout_duration(0, remaining_count=2, previous_count=4) == 1


def test_estimate_workout_duration_min_for_reps_and_time_units() -> None:
    assert estimate_workout_duration_min([("10", "times")]) == 1
    assert estimate_workout_duration_min([("20", "times")]) == 2
    assert estimate_workout_duration_min([("2", "min")]) == 2
    assert estimate_workout_duration_min([("90", "sec")]) == 2
    assert estimate_workout_duration_min([("10", "times"), ("2", "min")]) == 4


def test_parse_workout_tsv_reads_title_and_sets() -> None:
    text = "Title\tUpper body\nExercise\tType\tValue\nPull-up\t\t10\nSquat\t\t20\n"
    parsed = parse_workout_tsv(text)
    assert parsed.title == "Upper body"
    assert [(row.exercise, row.value) for row in parsed.rows] == [("Pull-up", "10"), ("Squat", "20")]


def test_format_workout_exercise_catalog_includes_unit_and_kcal() -> None:
    catalog = build_exercise_catalog(
        [[1, "Pull-up", "", 1, 0.5, "Подтягивания"]],
        [[10, "Pull-up", "Weighted", 1.2, "Блин 24"]],
    )
    text = format_workout_exercise_catalog(catalog)
    assert "Pull-up (Подтягивания)" in text
    assert "0.5 kcal/unit" in text
    assert "unit times" in text
    assert "Weighted (Блин 24) x1.2" in text


def test_format_recent_sets_empty() -> None:
    assert format_recent_sets([]) == "(none)"


def test_format_recent_sets_rows() -> None:
    text = format_recent_sets([[1, "Squat", "", "20", "", "2026-08-01"]])
    assert "Squat" in text
    assert "2026-08-01" in text


def test_resolve_workout_item_matches_catalog() -> None:
    catalog = [
        ExerciseCatalogEntry(
            name="Pull-up",
            type_required=True,
            types=[ExerciseTypeCatalog(name="Weighted")],
        )
    ]
    draft, error = resolve_workout_item(
        ParsedSetRow(exercise="Pull-up", type_name="Weighted", value="8"),
        catalog,
        {"Pull-up": 1},
        {("Pull-up", "Weighted"): 10},
    )
    assert error is None
    assert draft is not None
    assert draft.exercise_id == 1
    assert draft.type_id == 10
    assert draft.target_value == "8"
