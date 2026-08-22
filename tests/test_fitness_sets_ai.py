"""Tests for Fitness set TSV parsing and catalog matching."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import TextImageSourceDialog
from harrix_swiss_knife.apps.fitness.ai_source_dialog import create_fitness_dashboard_text_dialog
from harrix_swiss_knife.apps.fitness.sets_ai import (
    ExerciseCatalogEntry,
    ExerciseTypeCatalog,
    build_exercise_catalog,
    format_exercise_catalog,
    match_exercise,
    match_type,
    parse_sets_tsv,
)


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_parse_sets_tsv_reads_three_and_two_column_rows() -> None:
    """Type may be empty; two-column lines are exercise plus value."""
    rows = parse_sets_tsv("```\nExercise\tType\tValue\nPull-up\t\t12\nBench Press\t80 kg\t8\nSquat\t20\nBad\n```")
    assert [(row.exercise, row.type_name, row.value) for row in rows] == [
        ("Pull-up", "", "12"),
        ("Bench Press", "80 kg", "8"),
        ("Squat", "", "20"),
    ]


def test_parse_sets_tsv_normalizes_decimal_values() -> None:
    """Comma decimals become a stored number string."""
    rows = parse_sets_tsv("Run\t\t5,5")
    assert rows == [parse_sets_tsv("Run\t\t5.5")[0]]
    assert rows[0].value == "5.5"


def test_match_exercise_and_type_use_local_names() -> None:
    """English and local labels resolve to catalog names."""
    catalog = [
        ExerciseCatalogEntry(
            name="Pull-up",
            name_local="Подтягивания",
            type_required=True,
            types=[ExerciseTypeCatalog(name="Weighted", name_local="Блин 24")],
        )
    ]
    entry = match_exercise("подтягивания", catalog)
    assert entry is not None
    assert entry.name == "Pull-up"
    assert match_type("блин 24", entry) == "Weighted"
    assert match_type("Missing", entry) is None
    assert match_type("", entry) == ""


def test_build_and_format_exercise_catalog() -> None:
    """Catalog text includes local names and type requirement."""
    catalog = build_exercise_catalog(
        [[1, "Pull-up", "times", 1, 0.5, "Подтягивания"]],
        [[10, "Pull-up", "Weighted", 1.0, "Блин 24"]],
    )
    text = format_exercise_catalog(catalog)
    assert "Pull-up (Подтягивания)" in text
    assert "type required" in text
    assert "Weighted (Блин 24)" in text


def test_fitness_dashboard_text_dialog_is_large_text_only() -> None:
    """Text dashboard form hides images and uses a large editor."""
    assert _qapp() is not None
    dialog = create_fitness_dashboard_text_dialog()
    assert isinstance(dialog, TextImageSourceDialog)
    assert dialog.image_widget is None
    assert dialog.text_edit is not None
    assert dialog.text_edit.minimumHeight() >= 260
    assert dialog.minimumWidth() >= 800
    dialog.close()
