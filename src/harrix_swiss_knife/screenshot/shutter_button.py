"""Floating always-on-top shutter button for starting a region capture."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout

from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.screenshot.window_visibility import mark_screenshot_ui

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

_SHUTTER_SIZE = 56
_CAMERA_EMOJI = "📷"


class ShutterButton(QDialog):
    """Frameless stay-on-top camera button on the left edge of the primary screen."""

    def __init__(self) -> None:
        """Create the shutter button dialog."""
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(_SHUTTER_SIZE, _SHUTTER_SIZE)

        button = QPushButton(self)
        button.setFixedSize(_SHUTTER_SIZE, _SHUTTER_SIZE)
        button.setIcon(create_emoji_icon(_CAMERA_EMOJI, 36))
        button.setIconSize(QSize(36, 36))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(40, 40, 40, 220);
                border: 2px solid rgba(255, 255, 255, 180);
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 240);
                border-color: rgba(255, 255, 255, 230);
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 240);
            }
            """
        )
        button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)

        self._position_on_primary_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel capture on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def _position_on_primary_screen(self) -> None:
        """Place the button on the left edge, vertically centered."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + 12
        y = geo.y() + (geo.height() - _SHUTTER_SIZE) // 2
        self.move(x, y)
