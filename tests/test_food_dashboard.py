"""Tests for the Food dashboard tab and quick-add dialogs."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton

from harrix_swiss_knife.apps.common.dialogs.text_image_source_dialog import TextImageSourceDialog
from harrix_swiss_knife.apps.food.ai_source_dialog import (
    create_food_dashboard_photo_dialog,
    create_food_dashboard_text_dialog,
)
from harrix_swiss_knife.apps.food.food_dashboard import FoodDashboardWidget, format_today_calories
from harrix_swiss_knife.apps.food.window import Ui_MainWindow


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_format_today_calories_rounds_near_integers() -> None:
    """Whole and near-whole calorie totals render without a decimal."""
    assert format_today_calories(0) == "0"
    assert format_today_calories(1840.0) == "1840"
    assert format_today_calories(1840.4) == "1840"
    assert format_today_calories(1840.5) == "1840"


def test_food_dashboard_widget_shows_actions_and_calories() -> None:
    """Dashboard card has three centered actions and a large calorie total."""
    assert _qapp() is not None
    widget = FoodDashboardWidget()
    photo = widget.findChild(QPushButton, "foodDashAddPhotoButton")
    voice = widget.findChild(QPushButton, "foodDashAddVoiceButton")
    text = widget.findChild(QPushButton, "foodDashAddTextButton")
    assert photo is not None
    assert voice is not None
    assert text is not None
    assert "Add photo" in photo.text()
    assert "Speak" in voice.text()
    assert "Write text" in text.text()

    clicked: list[str] = []
    widget.add_photo_requested.connect(lambda: clicked.append("photo"))
    widget.add_voice_requested.connect(lambda: clicked.append("voice"))
    widget.add_text_requested.connect(lambda: clicked.append("text"))
    photo.click()
    voice.click()
    text.click()
    assert clicked == ["photo", "voice", "text"]

    widget.set_today_calories(1840.0)
    calories = widget.findChild(QLabel, "foodDashCaloriesValue")
    assert calories is not None
    assert calories.text() == "1840"


def test_food_window_inserts_dashboard_as_first_tab() -> None:
    """Dashboard is tab 0; Food and Statistics keep their object names."""
    assert _qapp() is not None

    class FoodUiWindow(QMainWindow, Ui_MainWindow):
        pass

    window = FoodUiWindow()
    window.setupUi(window)
    tabs = window.tabWidget
    assert tabs.count() == 3
    assert tabs.widget(0) is window.tab_food_dashboard
    assert tabs.widget(1) is window.tab_food
    assert tabs.widget(2) is window.tab_food_stats
    assert window.tab_food_dashboard.objectName() == "tab_food_dashboard"
    assert window.tab_food.objectName() == "tab_food"
    assert window.tab_food_stats.objectName() == "tab_food_stats"
    assert tabs.tabText(0) == "Dashboard"
    assert tabs.tabText(1) == "Food"
    assert tabs.tabText(2) == "Food Statistics"
    assert tabs.currentWidget() is window.tab_food_dashboard
    window.close()


def test_food_dashboard_photo_dialog_is_large_photo_only() -> None:
    """Photo dashboard form hides text and uses the large-type layout."""
    assert _qapp() is not None
    dialog = create_food_dashboard_photo_dialog()
    assert isinstance(dialog, TextImageSourceDialog)
    assert dialog.text_edit is None
    assert dialog.image_widget is not None
    assert dialog.minimumWidth() >= 800
    assert dialog.minimumHeight() >= 680
    dialog.close()


def test_food_dashboard_text_dialog_is_large_text_only() -> None:
    """Text dashboard form hides images and uses a large editor."""
    assert _qapp() is not None
    dialog = create_food_dashboard_text_dialog()
    assert dialog.image_widget is None
    assert dialog.text_edit is not None
    assert dialog.text_edit.minimumHeight() >= 260
    assert dialog.minimumWidth() >= 800
    dialog.close()
