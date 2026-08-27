"""Tests for the Fitness Workouts items table."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.fitness.database_manager import WorkoutItemRow
from harrix_swiss_knife.apps.fitness.workouts_widget import (
    _COL_EXERCISE,
    _COL_IMAGE,
    WorkoutsWidget,
)


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


def test_workouts_widget_has_duration_edit_and_remove_row() -> None:
    """Duration is editable and the items table has a remove-row action."""
    assert _qapp() is not None
    widget = WorkoutsWidget()
    assert widget.spin_duration.isEnabled() is False
    assert widget.spin_duration.suffix() == " min"
    assert widget.button_remove_item.text()
    widget.close()
