"""Tests for Select Exercise single and multi selection."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import cast

import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QAbstractItemView, QApplication

from harrix_swiss_knife.apps.common.dialogs.exercise_selection_dialog import ExerciseSelectionDialog
from harrix_swiss_knife.apps.fitness.main import MainWindow


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
    assert dialog.list_widget.selectionMode() == QAbstractItemView.SelectionMode.NoSelection
    assert dialog._selection_count_label.text() == "No exercises selected"
    assert dialog._add_button.text() == "Add exercise"
    assert not dialog._add_button.isEnabled()
    assert dialog._clear_button is not None
    assert not dialog._clear_button.isEnabled()
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


def test_exercise_selection_dialog_ignores_qt_item_selection(qapp: QApplication) -> None:
    """IconMode rubber-band must not become the selected-exercise source."""
    assert qapp is not None
    dialog = _dialog(multi_select=True)
    first = dialog.list_widget.item(0)
    assert first is not None
    first.setSelected(True)
    dialog._sync_selected_exercises()
    assert dialog.selected_exercises == []
    dialog.close()


def test_exercise_selection_dialog_multi_clear_selection(qapp: QApplication) -> None:
    assert qapp is not None
    dialog = _dialog(multi_select=True)
    first = dialog.list_widget.item(0)
    second = dialog.list_widget.item(1)
    assert first is not None
    assert second is not None
    assert dialog._clear_button is not None
    dialog._on_tile_clicked(first)
    dialog._on_tile_clicked(second)
    assert dialog.selected_exercises == ["Push-ups", "Squats"]
    assert dialog._clear_button.isEnabled()
    dialog._clear_button.click()
    assert dialog.selected_exercises == []
    assert dialog._selection_count_label.text() == "No exercises selected"
    assert not dialog._clear_button.isEnabled()
    first_tile = dialog._tile_for_item(first)
    second_tile = dialog._tile_for_item(second)
    assert first_tile is not None
    assert second_tile is not None
    assert not first_tile.is_selected
    assert not second_tile.is_selected
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


def test_open_select_exercise_dialog_shows_loading_toast(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert qapp is not None
    titles: list[str] = []

    @contextmanager
    def fake_scope(title: str) -> Iterator[None]:
        titles.append(title)
        yield None

    monkeypatch.setattr("harrix_swiss_knife.apps.fitness.main.app_loading_toast_scope", fake_scope)
    monkeypatch.setattr("harrix_swiss_knife.apps.fitness.main.message_box.information", lambda *_args, **_kwargs: None)

    class FakeWindow:
        def __init__(self) -> None:
            self.db_manager = SimpleNamespace(get_exercises_by_frequency=lambda _limit: [])

        def _validate_database_connection(self) -> bool:
            return True

    window = cast("MainWindow", FakeWindow())
    assert MainWindow._open_select_exercise_dialog(window) == []
    assert titles == ["Select Exercise"]
    assert MainWindow._open_select_exercise_dialog(window, multi_select=True) == []
    assert titles == ["Select Exercise", "Select Exercises"]
