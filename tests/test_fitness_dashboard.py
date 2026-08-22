"""Tests for the Fitness dashboard tab and circular exercise list."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QListView, QMainWindow, QPushButton, QSpinBox

from harrix_swiss_knife.apps.fitness.fitness_dashboard import (
    FitnessDashboardExercise,
    FitnessDashboardWidget,
    format_today_sets,
    make_circular_icon,
)
from harrix_swiss_knife.apps.fitness.window import Ui_MainWindow


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_format_today_sets_is_non_negative_integer_text() -> None:
    """Set totals render as compact integers."""
    assert format_today_sets(0) == "0"
    assert format_today_sets(12) == "12"
    assert format_today_sets(-3) == "0"


def test_make_circular_icon_clips_corners() -> None:
    """Circular icons keep a transparent corner outside the image circle."""
    assert _qapp() is not None
    source = QPixmap(64, 64)
    source.fill(QColor("#EF4444"))
    icon = make_circular_icon(source, 64)
    image = icon.pixmap(64, 64).toImage()
    assert not image.isNull()
    assert image.pixelColor(0, 0).alpha() == 0
    assert image.pixelColor(32, 32).alpha() == 255


def test_fitness_dashboard_widget_lists_exercises_and_adds_value() -> None:
    """Dashboard has a list, large value field, add button, and today's sets."""
    assert _qapp() is not None
    widget = FitnessDashboardWidget()
    exercise_list = widget.findChild(QListView, "fitnessDashExerciseList")
    value_spin = widget.findChild(QSpinBox, "fitnessDashValueSpin")
    add_button = widget.findChild(QPushButton, "fitnessDashAddButton")
    type_combo = widget.findChild(QComboBox, "fitnessDashTypeCombo")
    assert exercise_list is not None
    assert value_spin is not None
    assert add_button is not None
    assert type_combo is not None
    assert "Add" in add_button.text()

    clicked: list[str] = []
    widget.add_requested.connect(lambda: clicked.append("add"))
    add_button.click()
    assert clicked == ["add"]

    widget.set_exercises(
        [
            FitnessDashboardExercise(name="Pull-up", name_local="Подтягивания"),
            FitnessDashboardExercise(name="Squat"),
        ],
        selected="Squat",
    )
    assert widget.selected_exercise() == "Squat"
    widget.set_value(15)
    widget.set_unit("reps")
    widget.set_types(["Bodyweight", "Weighted"], selected="Weighted")
    widget.set_today_sets(7)
    assert widget.value() == 15
    assert widget.selected_type() == "Weighted"
    assert not type_combo.isHidden()
    unit = widget.findChild(QLabel, "fitnessDashUnitLabel")
    sets = widget.findChild(QLabel, "fitnessDashSetsValue")
    assert unit is not None
    assert sets is not None
    assert unit.text() == "reps"
    assert sets.text() == "7"


def test_fitness_window_inserts_dashboard_as_first_tab() -> None:
    """Dashboard is tab 0; later tabs keep their object names."""
    assert _qapp() is not None

    class FitnessUiWindow(QMainWindow, Ui_MainWindow):
        pass

    window = FitnessUiWindow()
    window.setupUi(window)
    tabs = window.tabWidget
    assert tabs.widget(0) is window.tab_fitness_dashboard
    assert tabs.widget(1) is window.tab
    assert window.tab_fitness_dashboard.objectName() == "tab_fitness_dashboard"
    assert window.tab.objectName() == "tab"
    assert window.tab_charts.objectName() == "tab_charts"
    assert window.tab_5.objectName() == "tab_5"
    assert window.tab_4.objectName() == "tab_4"
    assert tabs.tabText(0) == "Dashboard"
    assert tabs.tabText(1) == "Sets"
    assert tabs.currentWidget() is window.tab_fitness_dashboard
    window.close()


def test_fitness_dashboard_placeholder_icon_uses_letter() -> None:
    """Missing images still get a circular letter badge."""
    assert _qapp() is not None
    icon = make_circular_icon(None, 48, letter="bench")
    image = icon.pixmap(48, 48).toImage()
    assert not image.isNull()
    assert image.pixelColor(0, 0).alpha() == 0
    assert image.pixelColor(24, 24).alpha() == 255
