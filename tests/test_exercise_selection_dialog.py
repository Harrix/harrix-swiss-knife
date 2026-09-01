"""Tests for Select Exercise single and multi selection."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QAbstractItemView, QApplication

from harrix_swiss_knife.apps.common.dialogs.exercise_selection_dialog import ExerciseSelectionDialog


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _dialog(*, multi_select: bool = False) -> ExerciseSelectionDialog:
    return ExerciseSelectionDialog(
        None,
        exercises=["Push-ups", "Squats", "Plank"],
        pixmap_provider=lambda _name: QPixmap(),
        preview_size=QSize(64, 64),
        current_selection=None,
        multi_select=multi_select,
    )


def test_exercise_selection_dialog_single_click_replaces(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = _dialog()
    first = dialog.list_widget.item(0)
    second = dialog.list_widget.item(1)
    assert first is not None
    assert second is not None
    dialog._on_tile_clicked(first)
    dialog._on_tile_clicked(second)
    assert dialog.selected_exercise == "Squats"
    assert dialog.selected_exercises == ["Squats"]
    dialog.close()


def test_exercise_selection_dialog_multi_click_toggles(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = _dialog(multi_select=True)
    assert dialog.windowTitle() == "Select Exercises"
    assert dialog.list_widget.selectionMode() == QAbstractItemView.SelectionMode.MultiSelection
    assert dialog._selection_count_label.text() == "No exercises selected"
    assert dialog._add_button.text() == "Add exercise"
    assert not dialog._add_button.isEnabled()
    first = dialog.list_widget.item(0)
    second = dialog.list_widget.item(1)
    assert first is not None
    assert second is not None
    dialog._on_tile_clicked(first)
    dialog._on_tile_clicked(second)
    assert dialog.selected_exercises == ["Push-ups", "Squats"]
    assert dialog.selected_exercise == "Push-ups"
    assert dialog._selection_count_label.text() == "2 exercises selected"
    assert dialog._add_button.text() == "Add exercises (2)"
    assert dialog._add_button.isEnabled()
    dialog._on_tile_clicked(first)
    assert dialog.selected_exercises == ["Squats"]
    assert dialog._add_button.text() == "Add exercise"
    dialog.close()


def test_exercise_selection_dialog_selection_changed_does_not_use_item_set(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = _dialog(multi_select=True)
    first = dialog.list_widget.item(0)
    assert first is not None
    first.setSelected(True)
    dialog._on_selection_changed()
    assert dialog.selected_exercises == ["Push-ups"]
    dialog.close()


def test_exercise_selection_dialog_multi_shift_click_range(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = _dialog(multi_select=True)
    first = dialog.list_widget.item(0)
    third = dialog.list_widget.item(2)
    assert first is not None
    assert third is not None
    dialog._on_tile_clicked(first)
    dialog._on_tile_clicked(third, Qt.KeyboardModifier.ShiftModifier)
    assert dialog.selected_exercises == ["Push-ups", "Squats", "Plank"]
    dialog.close()
