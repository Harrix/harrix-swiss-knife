"""Floating always-on-top shutter controls for region capture."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import QEventLoop, QSize, Qt, Signal
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout

from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.screenshot.window_visibility import mark_screenshot_ui

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

_BUTTON_SIZE = 56
_BUTTON_GAP = 8
_ARRANGE_EMOJI = "🪟"
_CAMERA_EMOJI = "📷"
_CLOSE_EMOJI = "❌"
_ICON_SIZE = 36

ShutterMode = Literal["selection", "arrange"]

_BUTTON_STYLE = """
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


class ShutterButton(QDialog):
    """Frameless stay-on-top camera + close controls on the left edge of the primary screen.

    Emits `triggered` on the mode button click and `cancelled` on close click or Escape.
    Stays modeless so it can sit above the region overlay and toggle capture /
    desktop-arrangement modes while the app stays hidden.

    """

    cancelled = Signal()
    triggered = Signal()

    def __init__(self) -> None:
        """Create the shutter control dialog."""
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.NonModal)
        total_height = _BUTTON_SIZE * 2 + _BUTTON_GAP
        self.setFixedSize(_BUTTON_SIZE, total_height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_BUTTON_GAP)

        self._mode_button = self._make_emoji_button(_ARRANGE_EMOJI, "Arrange desktop")
        self._mode_button.clicked.connect(self.triggered.emit)
        layout.addWidget(self._mode_button)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        layout.addWidget(close_button)

        self._mode: ShutterMode = "selection"
        self._position_on_primary_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel capture on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            return
        super().keyPressEvent(event)

    def raise_above(self) -> None:
        """Keep the controls visible above other screenshot UI."""
        self.show()
        self.raise_()

    def set_mode(self, mode: ShutterMode) -> None:
        """Update the mode button emoji for selection vs desktop-arrangement."""
        self._mode = mode
        if mode == "selection":
            # In region selection, click leaves capture to arrange other Windows.
            self._mode_button.setIcon(create_emoji_icon(_ARRANGE_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Arrange desktop")
        else:
            # In arrange mode, click returns to region capture.
            self._mode_button.setIcon(create_emoji_icon(_CAMERA_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Capture region")

    def wait_for_trigger_or_cancel(self) -> bool:
        """Block until the mode button is clicked (`True`) or cancel/Escape (`False`)."""
        loop = QEventLoop()
        accepted = {"value": False}

        def on_triggered() -> None:
            accepted["value"] = True
            loop.quit()

        def on_cancelled() -> None:
            accepted["value"] = False
            loop.quit()

        self.triggered.connect(on_triggered)
        self.cancelled.connect(on_cancelled)
        try:
            self.set_mode("arrange")
            self.raise_above()
            self.activateWindow()
            loop.exec()
        finally:
            self.triggered.disconnect(on_triggered)
            self.cancelled.disconnect(on_cancelled)
        return accepted["value"]

    def _make_emoji_button(self, emoji: str, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(_BUTTON_SIZE, _BUTTON_SIZE)
        button.setIcon(create_emoji_icon(emoji, _ICON_SIZE))
        button.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setStyleSheet(_BUTTON_STYLE)
        return button

    def _position_on_primary_screen(self) -> None:
        """Place the controls on the left edge, vertically centered."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + 12
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)
