"""Fluent panels: drawer, dock widget, splash screen, bottom sheet, watermark."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPoint, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPainter
from PySide6.QtWidgets import QDockWidget, QHBoxLayout, QVBoxLayout, QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface, with_alpha
from harrix_swiss_knife.fluent.style import lucide_qss_url
from harrix_swiss_knife.fluent.theme import bind_theme, css, enable_fluent_theme, fluent_font, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ANIMATION_SLOW,
    RADIUS_CONTROL,
    RADIUS_OVERLAY,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SPACE_XL,
    TYPE_CAPTION,
)
from harrix_swiss_knife.fluent.widgets.buttons import FluentIconButton
from harrix_swiss_knife.fluent.widgets.display import FluentProgressRing
from harrix_swiss_knife.fluent.widgets.enums import TextStyle
from harrix_swiss_knife.fluent.widgets.text import CaptionLabel
from harrix_swiss_knife.fluent.widgets.text_base import FluentText

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent, QPaintEvent, QShowEvent

_DRAWER_WIDTH = 320
_SHEET_HEIGHT = 280
_SPLASH_SIZE = (420, 260)
_WATERMARK_ANGLE = -24


class DrawerEdge(Enum):
    """Edge of the window a drawer slides from."""

    LEFT = "left"
    RIGHT = "right"


class FluentDockWidget(QDockWidget):
    """Dock widget with a Fluent title bar and layer surface."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Create a dock widget."""
        super().__init__(title, parent)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        palette = palette_for(self)
        close = lucide_qss_url("x", palette.text_secondary, 12)
        undock = lucide_qss_url("copy", palette.text_secondary, 12)
        self.setStyleSheet(f"""
QDockWidget {{
    color: {css(palette.text_primary)}; titlebar-close-icon: url("{close}"); titlebar-normal-icon: url("{undock}");
}}
QDockWidget::title {{
    background: {css(palette.layer_alt_bg)};
    border-bottom: 1px solid {css(palette.divider)};
    padding: 6px 8px;
    text-align: left;
}}
QDockWidget::close-button, QDockWidget::float-button {{
    border: none; background: transparent; border-radius: {RADIUS_CONTROL}px; padding: 2px;
}}
QDockWidget::close-button:hover, QDockWidget::float-button:hover {{ background: {css(palette.subtle_hover)}; }}
""")


class FluentDrawerArea(QWidget):
    """Side drawer that slides over a window from the left or right edge."""

    opened = Signal()
    closed = Signal()

    def __init__(
        self, host: QWidget, *, edge: DrawerEdge = DrawerEdge.RIGHT, title: str = "", width: int = _DRAWER_WIDTH
    ) -> None:
        """Create a drawer over `host`'s window; add widgets to `content_layout`."""
        window = host.window()
        self._overlay = _HostOverlay(window)
        super().__init__(window)
        self._window = window
        self._edge = edge
        self._open = False
        self.setFixedWidth(width)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        layout.setSpacing(SPACE_M)
        header = QHBoxLayout()
        header.addWidget(FluentText(title, self, style=TextStyle.SUBTITLE), 1)
        close = FluentIconButton("x", self, tooltip="Close")
        close.clicked.connect(self.close_drawer)
        header.addWidget(close)
        layout.addLayout(header)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACE_S)
        layout.addLayout(self.content_layout, 1)
        self._overlay.clicked_outside.connect(self.close_drawer)
        self._animation = QPropertyAnimation(self, b"pos", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.update)

    def close_drawer(self) -> None:
        """Slide out and hide."""
        if not self._open:
            return
        self._open = False
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self._hidden_pos())
        self._animation.finished.connect(self._after_close)
        self._animation.start()
        self._overlay.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Keep full height and the edge position on window resize."""
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self.setFixedHeight(self._window.height())
            self.move(self._shown_pos() if self._open else self._hidden_pos())
        return False

    def is_open(self) -> bool:
        """Return whether the drawer is shown."""
        return self._open

    def open_drawer(self) -> None:
        """Slide in over a smoke layer."""
        if self._open:
            return
        self._open = True
        self._overlay.setGeometry(self._window.rect())
        self._overlay.show()
        self._overlay.raise_()
        self.setFixedHeight(self._window.height())
        self.move(self._hidden_pos())
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(self._hidden_pos())
        self._animation.setEndValue(self._shown_pos())
        self._animation.start()
        self.opened.emit()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the drawer surface with a hairline on the inner edge."""
        palette = palette_for(self)
        painter = QPainter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        painter.fillRect(self.rect(), fill)
        x = self.width() - 1 if self._edge == DrawerEdge.LEFT else 0
        painter.fillRect(x, 0, 1, self.height(), palette.popup_stroke)
        painter.end()

    def toggle(self) -> None:
        """Open or close."""
        if self._open:
            self.close_drawer()
        else:
            self.open_drawer()

    def _after_close(self) -> None:
        self._animation.finished.disconnect(self._after_close)
        if not self._open:
            self.hide()
            self.closed.emit()

    def _hidden_pos(self) -> QPoint:
        if self._edge == DrawerEdge.LEFT:
            return QPoint(-self.width(), 0)
        return QPoint(self._window.width(), 0)

    def _shown_pos(self) -> QPoint:
        if self._edge == DrawerEdge.LEFT:
            return QPoint(0, 0)
        return QPoint(self._window.width() - self.width(), 0)


class FluentSheetPanel(QWidget):
    """Bottom sheet that slides up over a window with a grab handle."""

    closed = Signal()

    def __init__(self, host: QWidget, *, height: int = _SHEET_HEIGHT) -> None:
        """Create a bottom sheet over `host`'s window; add widgets to `content_layout`."""
        window = host.window()
        self._overlay = _HostOverlay(window)
        super().__init__(window)
        self._window = window
        self._open = False
        self.setFixedHeight(height)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_L)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout, 1)
        self._overlay.clicked_outside.connect(self.close_sheet)
        self._animation = QPropertyAnimation(self, b"pos", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.update)

    def close_sheet(self) -> None:
        """Slide down and hide."""
        if not self._open:
            return
        self._open = False
        self._overlay.hide()
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(QPoint(0, self._window.height()))
        self._animation.start()
        self.closed.emit()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Follow window resizes."""
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self.setFixedWidth(self._window.width())
            self.move(0, self._window.height() - (self.height() if self._open else 0))
        return False

    def open_sheet(self) -> None:
        """Slide up."""
        self._open = True
        self._overlay.setGeometry(self._window.rect())
        self._overlay.show()
        self._overlay.raise_()
        self.setFixedWidth(self._window.width())
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(QPoint(0, self._window.height()))
        self._animation.setEndValue(QPoint(0, self._window.height() - self.height()))
        self._animation.start()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the sheet with rounded top corners and a grab handle."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(
            painter, self.rect().adjusted(0, 0, 0, RADIUS_OVERLAY * 2), fill, palette.popup_stroke, RADIUS_OVERLAY * 2
        )
        handle = QRect((self.width() - 36) // 2, SPACE_S, 36, 4)
        paint_surface(painter, handle, palette.control_strong_stroke, None, 2)
        painter.end()


class FluentSplashScreen(QWidget):
    """Frameless startup window: app icon, title, status text, and a busy ring."""

    def __init__(self, title: str, *, icon: QIcon | None = None, subtitle: str = "") -> None:
        """Create a splash screen (`show()` centers it on the primary screen)."""
        super().__init__(
            None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        enable_fluent_theme(self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setFixedSize(*_SPLASH_SIZE)
        self._icon = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL * 2 + 48, SPACE_XL, SPACE_XL)
        layout.setSpacing(SPACE_S)
        heading = FluentText(title, self, style=TextStyle.TITLE)
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)
        if subtitle:
            caption = CaptionLabel(subtitle, self)
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(caption)
        layout.addStretch(1)
        self._status = CaptionLabel("", self)
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ring = FluentProgressRing(self, size=28)
        self.ring.set_busy(busy=True)
        layout.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._status)

    def finish(self, window: QWidget | None = None) -> None:
        """Close the splash (after `window` is shown, if given)."""
        self.ring.set_busy(busy=False)
        if window is not None:
            window.show()
        self.close()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the rounded surface and icon."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.window_bg, palette.popup_stroke, RADIUS_OVERLAY)
        if self._icon is not None and not self._icon.isNull():
            self._icon.paint(painter, QRect((self.width() - 48) // 2, SPACE_XL * 2 - SPACE_S, 48, 48))
        painter.end()

    def set_status(self, text: str) -> None:
        """Show a status line under the ring."""
        self._status.setText(text)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Center on the primary screen."""
        screen = self.screen()
        if screen is not None:
            self.move(screen.availableGeometry().center() - self.rect().center())
        super().showEvent(event)


class FluentWatermark(QWidget):
    """Transparent overlay that tiles a rotated text watermark over its parent."""

    def __init__(self, text: str, parent: QWidget, *, opacity: int = 22, gap: int = 120) -> None:
        """Create a watermark over `parent` (mouse events pass through)."""
        super().__init__(parent)
        self._text = text
        self._opacity = opacity
        self._gap = gap
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())
        self.raise_()
        bind_theme(self, self.update)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Cover the parent after it resizes."""
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            parent = self.parentWidget()
            if parent is not None:
                self.setGeometry(parent.rect())
                self.raise_()
        return False

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the tiled rotated text."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_CAPTION * 1.2, weight=QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(with_alpha(palette.text_primary, self._opacity))
        width = painter.fontMetrics().horizontalAdvance(self._text) + self._gap
        height = self._gap
        painter.rotate(_WATERMARK_ANGLE)
        span = max(self.width(), self.height()) * 2
        for y in range(-span, span, height):
            for x in range(-span, span, width):
                painter.drawText(x, y, self._text)
        painter.end()

    def set_text(self, text: str) -> None:
        """Change the watermark text."""
        self._text = text
        self.update()


class _HostOverlay(QWidget):
    """Full-window smoke layer that closes its panel on an outside click."""

    clicked_outside = Signal()

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window = window
        self.hide()
        window.installEventFilter(self)
        bind_theme(self, self.update)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self.setGeometry(self._window.rect())
        return False

    def mouseReleaseEvent(self, _event: QMouseEvent) -> None:  # noqa: N802
        self.clicked_outside.emit()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), palette_for(self).smoke)
        painter.end()
