"""Centered Food dashboard for quick photo, voice, and text logging."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

_DASH_BUTTON_STYLE = """
QPushButton#foodDashAddPhotoButton,
QPushButton#foodDashAddVoiceButton,
QPushButton#foodDashAddTextButton {
    background: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    padding: 16px 32px;
}
QPushButton#foodDashAddPhotoButton:hover,
QPushButton#foodDashAddVoiceButton:hover,
QPushButton#foodDashAddTextButton:hover {
    background: #2563EB;
}
QPushButton#foodDashAddPhotoButton:pressed,
QPushButton#foodDashAddVoiceButton:pressed,
QPushButton#foodDashAddTextButton:pressed {
    background: #1D4ED8;
}
"""


class FoodDashboardWidget(QWidget):
    """Habits-style call-to-action card for adding food and showing today's calories."""

    add_photo_requested = Signal()
    add_voice_requested = Signal()
    add_text_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("FoodDashboardWidget { background: #FFFFFF; }")
        self._build_ui()

    def set_today_calories(self, kcal: float) -> None:
        """Update the large calorie figure shown under the action buttons.

        Args:

        - `kcal` (`float`): Calories consumed today.

        """
        self._calories_value.setText(format_today_calories(kcal))

    def _build_action_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumSize(280, 64)
        _apply_pixel_font(button, pixel_size=20, weight=QFont.Weight.Bold)
        return button

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        pane = QFrame()
        pane.setObjectName("foodDashEmptyState")
        pane.setStyleSheet(
            """
            QFrame#foodDashEmptyState {
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
            }
            """
        )
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(16)

        title = QLabel("Add food")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #111827;")
        _apply_pixel_font(title, pixel_size=28, weight=QFont.Weight.ExtraBold)

        subtitle = QLabel("Log a meal with a photo, voice, or text.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(subtitle, pixel_size=16)

        photo_button = self._build_action_button("📷 Add photo", "foodDashAddPhotoButton")
        voice_button = self._build_action_button("🎙️ Speak", "foodDashAddVoiceButton")
        text_button = self._build_action_button("📝 Write text", "foodDashAddTextButton")
        photo_button.clicked.connect(self.add_photo_requested.emit)
        voice_button.clicked.connect(self.add_voice_requested.emit)
        text_button.clicked.connect(self.add_text_requested.emit)

        self._calories_value = QLabel("0")
        self._calories_value.setObjectName("foodDashCaloriesValue")
        self._calories_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._calories_value.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._calories_value, pixel_size=64, weight=QFont.Weight.ExtraBold)

        calories_hint = QLabel("kcal today")
        calories_hint.setObjectName("foodDashCaloriesHint")
        calories_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calories_hint.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(calories_hint, pixel_size=20, weight=QFont.Weight.DemiBold)

        buttons = QWidget()
        buttons.setStyleSheet(_DASH_BUTTON_STYLE)
        buttons_layout = QVBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 8)
        buttons_layout.setSpacing(12)
        buttons_layout.addWidget(photo_button, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons_layout.addWidget(voice_button, 0, Qt.AlignmentFlag.AlignHCenter)
        buttons_layout.addWidget(text_button, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(16)
        layout.addWidget(self._calories_value)
        layout.addWidget(calories_hint)
        layout.addStretch(1)

        outer.addWidget(pane)


def format_today_calories(kcal: float) -> str:
    """Format today's calories for the large dashboard number.

    Args:

    - `kcal` (`float`): Calories consumed today.

    Returns:

    - `str`: Compact calorie text without a unit suffix.

    """
    return str(round(kcal))


def _apply_pixel_font(
    widget: QWidget,
    *,
    pixel_size: int,
    weight: QFont.Weight = QFont.Weight.Normal,
) -> None:
    font = widget.font()
    font.setPixelSize(pixel_size)
    font.setWeight(weight)
    widget.setFont(font)
