"""Always-on-top floating screenshot button for Finance Add with AI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import (
    BUTTON_MIN_HEIGHT_PX,
    BUTTON_SECONDARY_BORDER,
    BUTTON_SECONDARY_FG,
    BUTTON_SECONDARY_HOVER,
    BUTTON_SECONDARY_PRESSED,
    PANEL_RADIUS,
    SURFACE,
)
from harrix_swiss_knife.fluent.tokens import ICON_SIZE_LARGE
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

if TYPE_CHECKING:
    from collections.abc import Callable

_FAB_SIZE = 48
_EDGE_MARGIN = 20
_SCREENSHOT_ICON = "camera"


class FinanceAiScreenshotFab(QWidget):
    """Circular stay-on-top camera control on the right edge of the screen.

    Unparented `Tool` window so it does not minimize with the Finance window or
    other apps. Finance shows and hides this while the tracker is open.

    """

    def __init__(self, on_click: Callable[[], None]) -> None:
        """Create the floating button; call `show_for_finance` when Finance opens."""
        super().__init__(None)
        self.setObjectName("financeAiScreenshotFab")
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setFixedSize(_FAB_SIZE, _FAB_SIZE)

        button = QPushButton(self)
        button.setObjectName("financeAiScreenshotFabButton")
        button.setFixedSize(_FAB_SIZE, _FAB_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolTip("Capture screen region for Add with AI")
        button.setStyleSheet(_fab_button_qss())
        apply_lucide_button_icon(button, _SCREENSHOT_ICON, icon_size=ICON_SIZE_LARGE)
        button.clicked.connect(on_click)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)

    def hide_for_finance(self) -> None:
        """Hide when Finance closes or is intentionally hidden."""
        self.hide()

    def place_on_screen(self) -> None:
        """Pin to the right edge, vertically centered on the current screen."""
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.right() - self.width() - _EDGE_MARGIN
        y = geo.center().y() - self.height() // 2
        self.move(x, y)

    def show_for_finance(self) -> None:
        """Show and re-place the floating control."""
        self.place_on_screen()
        self.show()
        self.raise_()


def _fab_button_qss() -> str:
    """Return QSS for a round secondary plate with the camera icon."""
    radius = max(PANEL_RADIUS, _FAB_SIZE // 2)
    return (
        f"QPushButton#financeAiScreenshotFabButton {{"
        f" background-color: {SURFACE};"
        f" border: 1px solid {BUTTON_SECONDARY_BORDER};"
        f" border-radius: {radius}px;"
        f" color: {BUTTON_SECONDARY_FG};"
        f" min-height: {BUTTON_MIN_HEIGHT_PX}px;"
        f" padding: 0px;"
        f"}}"
        f"QPushButton#financeAiScreenshotFabButton:hover {{"
        f" background-color: {BUTTON_SECONDARY_HOVER};"
        f"}}"
        f"QPushButton#financeAiScreenshotFabButton:pressed {{"
        f" background-color: {BUTTON_SECONDARY_PRESSED};"
        f"}}"
    )
