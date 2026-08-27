"""Tests for Fitness exercise-image lightbox helpers."""

from __future__ import annotations

from PySide6.QtGui import QStandardItem, QStandardItemModel

from harrix_swiss_knife.apps.fitness.main import (
    _EXERCISE_TABLE_IMAGE_COLUMN,
    _EXERCISE_TABLE_NAME_COLUMN,
    exercise_names_from_name_column,
    exercise_table_focus_column,
    is_exercise_table_image_column,
)


def test_is_exercise_table_image_column() -> None:
    assert is_exercise_table_image_column(_EXERCISE_TABLE_IMAGE_COLUMN)
    assert not is_exercise_table_image_column(_EXERCISE_TABLE_NAME_COLUMN)


def test_exercise_table_focus_column_is_image() -> None:
    assert exercise_table_focus_column("exercises") == _EXERCISE_TABLE_IMAGE_COLUMN
    assert exercise_table_focus_column("types") == _EXERCISE_TABLE_IMAGE_COLUMN
    assert exercise_table_focus_column("process") == 0


def test_exercise_names_from_name_column_skips_empty_and_duplicates() -> None:
    model = QStandardItemModel(4, 2)
    rows = [("", "Squat"), ("x", "Bench"), ("x", "Squat"), ("x", "")]
    for row, (image, name) in enumerate(rows):
        model.setItem(row, 0, QStandardItem(image))
        model.setItem(row, 1, QStandardItem(name))
    assert exercise_names_from_name_column(model, 1) == ["Squat", "Bench"]
    assert exercise_names_from_name_column(None, 1) == []
