"""Tests for the Fitness dashboard tab and exercise list."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QStandardItemModel
from PySide6.QtWidgets import QApplication, QComboBox, QLabel, QListView, QMainWindow, QPushButton, QSpinBox

from harrix_swiss_knife.apps.common.delegates.name_local_list_delegate import NameLocalListDelegate
from harrix_swiss_knife.apps.fitness.fitness_dashboard import (
    FitnessDashboardExercise,
    FitnessDashboardWidget,
    _DashboardExerciseDelegate,
    format_today_sets,
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


def test_fitness_dashboard_widget_lists_exercises_and_adds_value() -> None:
    """Dashboard has a list, large value field, add button, and today's sets."""
    assert _qapp() is not None
    widget = FitnessDashboardWidget()
    exercise_list = widget.findChild(QListView, "fitnessDashExerciseList")
    value_spin = widget.findChild(QSpinBox, "fitnessDashValueSpin")
    add_button = widget.findChild(QPushButton, "fitnessDashAddButton")
    voice_button = widget.findChild(QPushButton, "fitnessDashAddVoiceButton")
    text_button = widget.findChild(QPushButton, "fitnessDashAddTextButton")
    type_combo = widget.findChild(QComboBox, "fitnessDashTypeCombo")
    assert exercise_list is not None
    assert value_spin is not None
    assert add_button is not None
    assert voice_button is not None
    assert text_button is not None
    assert type_combo is not None
    assert "Add" in add_button.text()
    assert "Speak" in voice_button.text()
    assert "Write text" in text_button.text()

    clicked: list[str] = []
    widget.add_requested.connect(lambda: clicked.append("add"))
    widget.add_voice_requested.connect(lambda: clicked.append("voice"))
    widget.add_text_requested.connect(lambda: clicked.append("text"))
    add_button.click()
    voice_button.click()
    text_button.click()
    assert clicked == ["add", "voice", "text"]

    widget.set_exercises(
        [
            FitnessDashboardExercise(name="Pull-up", name_local="Подтягивания", is_favorite=True),
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
    combo_style = type_combo.styleSheet()
    assert "::drop-down" in combo_style
    assert "image: none" in combo_style
    unit = widget.findChild(QLabel, "fitnessDashUnitLabel")
    sets = widget.findChild(QLabel, "fitnessDashSetsValue")
    assert unit is not None
    assert sets is not None
    assert unit.text() == "reps"
    assert sets.text() == "7"
    assert exercise_list.font().pixelSize() >= 22
    assert exercise_list.font().weight() == QFont.Weight.Normal
    assert exercise_list.iconSize().width() >= 96
    model = exercise_list.model()
    assert isinstance(model, QStandardItemModel)
    first = model.item(0)
    assert first is not None
    assert first.text() == "⭐ Pull-up"
    assert first.data(Qt.ItemDataRole.UserRole) == "Pull-up"
    assert first.font().pixelSize() >= 22
    assert first.font().weight() == QFont.Weight.Normal
    delegate = exercise_list.itemDelegate()
    assert isinstance(delegate, _DashboardExerciseDelegate)
    assert isinstance(delegate, NameLocalListDelegate)
    local_font = delegate._local_font(exercise_list.font())
    assert local_font.pixelSize() >= 18
    assert local_font.weight() == QFont.Weight.Normal


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
    assert tabs.tabText(0) == "Quick"
    assert tabs.tabText(1) == "Sets"
    assert tabs.currentWidget() is window.tab_fitness_dashboard
    window.close()
