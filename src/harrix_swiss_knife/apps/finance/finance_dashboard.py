"""Centered Finance dashboard for quick photo, voice, and text logging."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

_DASH_BUTTON_STYLE = """
QPushButton#financeDashAddPhotoButton,
QPushButton#financeDashAddVoiceButton,
QPushButton#financeDashAddTextButton {
    background: #3B82F6;
    color: #FFFFFF;
    border: none;
    border-radius: 14px;
    padding: 16px 32px;
}
QPushButton#financeDashAddPhotoButton:hover,
QPushButton#financeDashAddVoiceButton:hover,
QPushButton#financeDashAddTextButton:hover {
    background: #2563EB;
}
QPushButton#financeDashAddPhotoButton:pressed,
QPushButton#financeDashAddVoiceButton:pressed,
QPushButton#financeDashAddTextButton:pressed {
    background: #1D4ED8;
}
"""


class FinanceDashboardWidget(QWidget):
    """Food-style call-to-action card for adding purchases and showing today's spend."""

    add_photo_requested = Signal()
    add_voice_requested = Signal()
    add_text_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("FinanceDashboardWidget { background: #FFFFFF; }")
        self._build_ui()

    def set_today_expense(self, amount_text: str, extra_text: str = "") -> None:
        """Update the large spend figure shown under the action buttons.

        Args:

        - `amount_text` (`str`): Formatted amount for the default currency.
        - `extra_text` (`str`): Optional extra currencies on smaller lines.

        """
        self._expense_value.setText(amount_text)
        self._expense_extra.setText(extra_text)
        self._expense_extra.setVisible(bool(extra_text.strip()))

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
        pane.setObjectName("financeDashEmptyState")
        pane.setStyleSheet(
            """
            QFrame#financeDashEmptyState {
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
            }
            """
        )
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(16)

        title = QLabel("Add purchase")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #111827;")
        _apply_pixel_font(title, pixel_size=28, weight=QFont.Weight.ExtraBold)

        subtitle = QLabel("Log a purchase with a photo, voice, or text.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(subtitle, pixel_size=16)

        photo_button = self._build_action_button("📷 Add photo", "financeDashAddPhotoButton")
        voice_button = self._build_action_button("🎙️ Speak", "financeDashAddVoiceButton")
        text_button = self._build_action_button("📝 Write text", "financeDashAddTextButton")
        photo_button.clicked.connect(self.add_photo_requested.emit)
        voice_button.clicked.connect(self.add_voice_requested.emit)
        text_button.clicked.connect(self.add_text_requested.emit)

        self._expense_value = QLabel("0")
        self._expense_value.setObjectName("financeDashExpenseValue")
        self._expense_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._expense_value.setStyleSheet("color: #111827;")
        _apply_pixel_font(self._expense_value, pixel_size=64, weight=QFont.Weight.ExtraBold)

        expense_hint = QLabel("spent today")
        expense_hint.setObjectName("financeDashExpenseHint")
        expense_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        expense_hint.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(expense_hint, pixel_size=20, weight=QFont.Weight.DemiBold)

        self._expense_extra = QLabel("")
        self._expense_extra.setObjectName("financeDashExpenseExtra")
        self._expense_extra.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._expense_extra.setWordWrap(True)
        self._expense_extra.setStyleSheet("color: #6B7280;")
        _apply_pixel_font(self._expense_extra, pixel_size=16)
        self._expense_extra.hide()

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
        layout.addWidget(self._expense_value)
        layout.addWidget(expense_hint)
        layout.addWidget(self._expense_extra)
        layout.addStretch(1)

        outer.addWidget(pane)


def pick_today_expense_display(
    lines: list[str],
    *,
    default_code: str,
    zero_text: str,
) -> tuple[str, str]:
    """Choose the large amount and leftover currency lines for the dashboard.

    Args:

    - `lines` (`list[str]`): Per-currency expense lines (`CODE: amount`).
    - `default_code` (`str`): Preferred currency code for the large figure.
    - `zero_text` (`str`): Text to show when there are no expenses.

    Returns:

    - `tuple[str, str]`: Main amount text and optional extra currencies.

    """
    if not lines:
        return zero_text, ""
    prefix = f"{default_code}: "
    main = next((line for line in lines if line.startswith(prefix)), lines[0])
    amount_text = main.split(": ", 1)[-1]
    extra = "\n".join(line for line in lines if line != main)
    return amount_text, extra


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
