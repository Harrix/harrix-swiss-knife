"""Always-on-top floating screenshot button for Finance Add with AI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtGui import QCursor, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QMenu, QPushButton, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import (
    BUTTON_MIN_HEIGHT_PX,
    BUTTON_SECONDARY_BORDER,
    BUTTON_SECONDARY_FG,
    BUTTON_SECONDARY_HOVER,
    BUTTON_SECONDARY_PRESSED,
    PANEL_RADIUS,
    SURFACE,
)
from harrix_swiss_knife.apps.finance.ai_screenshot_fab_settings import (
    clamp_fab_top_left,
    clear_fab_position,
    default_fab_top_left,
    load_fab_enabled,
    resolve_fab_top_left,
    save_fab_enabled,
    save_fab_position,
)
from harrix_swiss_knife.fluent.tokens import ICON_SIZE_LARGE
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QRect

_FAB_SIZE = 48
_EDGE_MARGIN = 20
_DRAG_THRESHOLD_PX = 5
_SCREENSHOT_ICON = "camera"


class FinanceAiScreenshotFab(QWidget):
    """Circular stay-on-top camera control, draggable, with show/hide prefs.

    Unparented `Tool` window so it does not minimize with the Finance window or
    other apps. Finance shows and hides this while the tracker is open.

    """

    def __init__(
        self,
        on_click: Callable[[], None],
        *,
        on_enabled_changed: Callable[..., None] | None = None,
    ) -> None:
        """Create the floating button; call `show_for_finance` when Finance opens."""
        super().__init__(None)
        self._on_click = on_click
        self._on_enabled_changed = on_enabled_changed
        self._drag_active = False
        self._drag_moved = False
        self._drag_offset = QPoint()
        self._press_global = QPoint()

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
        button.setToolTip("Capture screen region for Add with AI · drag to move")
        button.setStyleSheet(_fab_button_qss())
        button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        apply_lucide_button_icon(button, _SCREENSHOT_ICON, icon_size=ICON_SIZE_LARGE)
        button.customContextMenuRequested.connect(self._show_context_menu)
        button.installEventFilter(self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)
        self._button = button

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Drag the floating window; treat a short press as a click."""
        if watched is not self._button:
            return super().eventFilter(watched, event)
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
            if event.button() != Qt.MouseButton.LeftButton:
                return False
            self._drag_active = True
            self._drag_moved = False
            self._press_global = event.globalPosition().toPoint()
            self._drag_offset = self._press_global - self.frameGeometry().topLeft()
            return True
        if event_type == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
            if not self._drag_active or not (event.buttons() & Qt.MouseButton.LeftButton):
                return False
            global_pos = event.globalPosition().toPoint()
            if not self._drag_moved:
                delta = global_pos - self._press_global
                if abs(delta.x()) < _DRAG_THRESHOLD_PX and abs(delta.y()) < _DRAG_THRESHOLD_PX:
                    return True
                self._drag_moved = True
                self._button.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.move(global_pos - self._drag_offset)
            return True
        if event_type == QEvent.Type.MouseButtonRelease and isinstance(event, QMouseEvent):
            if event.button() != Qt.MouseButton.LeftButton or not self._drag_active:
                return False
            moved = self._drag_moved
            self._drag_active = False
            self._drag_moved = False
            self._button.setCursor(Qt.CursorShape.PointingHandCursor)
            if moved:
                self._finish_drag()
            else:
                self._on_click()
            return True
        return super().eventFilter(watched, event)

    def hide_for_finance(self) -> None:
        """Hide when Finance closes or the floating button is disabled."""
        self.hide()

    def place_on_screen(self, *, use_default: bool = False) -> None:
        """Place using the saved (clamped) position, or the right-edge default."""
        available = self._available_geometry()
        if available is None:
            return
        if use_default:
            point = default_fab_top_left(size=_FAB_SIZE, available=available, edge_margin=_EDGE_MARGIN)
        else:
            point = resolve_fab_top_left(size=_FAB_SIZE, available=available, edge_margin=_EDGE_MARGIN)
        self.move(point)

    def restore_default_position(self) -> None:
        """Clear the saved position and pin to the default right-edge spot."""
        clear_fab_position()
        self.place_on_screen(use_default=True)

    def show_for_finance(self) -> None:
        """Show and re-place the floating control when enabled."""
        if not load_fab_enabled():
            self.hide_for_finance()
            return
        self.place_on_screen()
        self.show()
        self.raise_()

    def _available_geometry(self) -> QRect | None:
        center = self.geometry().center() if self.isVisible() else QCursor.pos()
        screen = QGuiApplication.screenAt(center) or QGuiApplication.screenAt(QCursor.pos())
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        if screen is None:
            return None
        return screen.availableGeometry()

    def _finish_drag(self) -> None:
        available = self._available_geometry()
        if available is not None:
            point = clamp_fab_top_left(self.x(), self.y(), size=_FAB_SIZE, available=available)
            self.move(point)
        save_fab_position(self.x(), self.y())

    def _show_context_menu(self, pos: QPoint) -> None:
        menu = QMenu(self)
        show_action = menu.addAction("Show floating screenshot button")
        show_action.setCheckable(True)
        show_action.setChecked(load_fab_enabled())
        restore_action = menu.addAction("Restore default position")
        chosen = menu.exec(self._button.mapToGlobal(pos))
        if chosen is show_action:
            enabled = show_action.isChecked()
            save_fab_enabled(enabled=enabled)
            if self._on_enabled_changed is not None:
                self._on_enabled_changed(enabled=enabled)
            elif enabled:
                self.show_for_finance()
            else:
                self.hide_for_finance()
        elif chosen is restore_action:
            self.restore_default_position()


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
