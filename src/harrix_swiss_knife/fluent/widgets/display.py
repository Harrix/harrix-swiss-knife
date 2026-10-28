"""Fluent data display: badges, tags, avatars, stats, progress, steps, timeline, and more."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QDateTime, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPen, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLCDNumber, QSizePolicy, QVBoxLayout, QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface, rounded_path, with_alpha
from harrix_swiss_knife.fluent.qr import Ecc, encode_qr
from harrix_swiss_knife.fluent.style import themed_icon
from harrix_swiss_knife.fluent.theme import bind_theme, css, fluent_font, palette_for
from harrix_swiss_knife.fluent.tokens import (
    CONTROL_HEIGHT,
    ICON_SIZE_LARGE,
    RADIUS_CARD,
    RADIUS_CONTROL,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SPACE_XS,
    TYPE_CAPTION,
)
from harrix_swiss_knife.fluent.widgets.enums import TextRole, TextStyle
from harrix_swiss_knife.fluent.widgets.text import CaptionLabel
from harrix_swiss_knife.fluent.widgets.text_base import FluentText

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent

    from harrix_swiss_knife.fluent.tokens import FluentPalette
from harrix_swiss_knife.fluent.widgets.enums import Severity, SkeletonShape, Trend

_BUSY_INTERVAL_MS = 16
_SECONDS_PER_DAY = 86400
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_MINUTE = 60
_BADGE_MAX_VALUE = 99


class FluentCountdown(QWidget):
    """Days / hours / minutes / seconds countdown in card tiles."""

    finished = Signal()

    def __init__(self, parent: QWidget | None = None, *, seconds: int = 0) -> None:
        """Create a countdown (call `start` with seconds or a target time)."""
        super().__init__(parent)
        self._remaining = max(0, seconds)
        self._target: QDateTime | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACE_S)
        self._tiles: list[FluentText] = []
        for caption in ("Days", "Hours", "Minutes", "Seconds"):
            tile = _CountdownTile(caption, self)
            row.addWidget(tile)
            self._tiles.append(tile.value_label)
        row.addStretch(1)
        self._render()

    def is_running(self) -> bool:
        """Return whether the countdown is ticking."""
        return self._timer.isActive()

    def remaining(self) -> int:
        """Return remaining seconds."""
        return self._remaining

    def start(self, *, seconds: int | None = None, target: datetime | None = None) -> None:
        """Start counting down from `seconds` or until `target`."""
        if target is not None:
            self._target = QDateTime(target)
            self._remaining = max(0, QDateTime.currentDateTime().secsTo(self._target))
        elif seconds is not None:
            self._target = None
            self._remaining = max(0, seconds)
        self._render()
        self._timer.start()

    def stop(self) -> None:
        """Pause the countdown."""
        self._timer.stop()

    def _render(self) -> None:
        days, rest = divmod(self._remaining, _SECONDS_PER_DAY)
        hours, rest = divmod(rest, _SECONDS_PER_HOUR)
        minutes, seconds = divmod(rest, _SECONDS_PER_MINUTE)
        for label, value in zip(self._tiles, (days, hours, minutes, seconds), strict=True):
            label.setText(f"{value:02d}")

    def _tick(self) -> None:
        if self._target is not None:
            self._remaining = max(0, QDateTime.currentDateTime().secsTo(self._target))
        else:
            self._remaining = max(0, self._remaining - 1)
        self._render()
        if self._remaining == 0:
            self._timer.stop()
            self.finished.emit()


class FluentDivider(QWidget):
    """Horizontal or vertical hairline, optionally with text."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        text: str = "",
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignHCenter,
    ) -> None:
        """Create a divider.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `orientation` (`Qt.Orientation`): Line direction.
        - `text` (`str`): Optional label in the line (horizontal only).
        - `alignment` (`Qt.AlignmentFlag`): Label position: left, center, or right.

        """
        super().__init__(parent)
        self._orientation = orientation
        self._text = text
        self._alignment = alignment
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(20 if text else 1)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        else:
            self.setFixedWidth(1)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the line and label."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        painter.setRenderHint(painter.RenderHint.Antialiasing, on=False)
        if self._orientation == Qt.Orientation.Vertical:
            painter.fillRect(self.rect(), palette.divider)
            painter.end()
            return
        y = self.height() // 2
        if not self._text:
            painter.fillRect(0, y, self.width(), 1, palette.divider)
            painter.end()
            return
        text_width = self.fontMetrics().horizontalAdvance(self._text) + 2 * SPACE_S
        if self._alignment & Qt.AlignmentFlag.AlignLeft:
            start = SPACE_L
        elif self._alignment & Qt.AlignmentFlag.AlignRight:
            start = self.width() - SPACE_L - text_width
        else:
            start = (self.width() - text_width) // 2
        painter.fillRect(0, y, max(0, start), 1, palette.divider)
        painter.fillRect(start + text_width, y, max(0, self.width() - start - text_width), 1, palette.divider)
        painter.setPen(palette.text_secondary)
        painter.drawText(QRectF(start, 0, text_width, self.height()), int(Qt.AlignmentFlag.AlignCenter), self._text)
        painter.end()


class FluentInfoBadge(QWidget):
    """Small attention badge: a dot, a number, or an icon."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        value: int | None = None,
        icon: str = "",
        severity: Severity = Severity.CRITICAL,
    ) -> None:
        """Create a badge.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `value` (`int | None`): Number to show (`None` = dot or icon).
        - `icon` (`str`): Lucide icon ID shown when `value` is `None`.
        - `severity` (`Severity`): Badge color.

        """
        super().__init__(parent)
        self._value = value
        self._icon = icon
        self._severity = severity
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the pill, number, or icon."""
        palette = palette_for(self)
        foreground, _background = severity_colors(palette, self._severity)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        paint_surface(painter, rect, foreground, None, rect.height() / 2)
        if self._value is not None:
            painter.setPen(palette.text_on_accent if self._severity == Severity.ACCENT else QColor("#ffffff"))
            painter.setFont(fluent_font(self.font(), TYPE_CAPTION, weight=QFont.Weight.DemiBold))
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), self._text())
        elif self._icon:
            side = 10
            icon = themed_icon(self._icon, palette, QColor("#ffffff"), side)
            icon.paint(painter, int(rect.center().x() - side / 2), int(rect.center().y() - side / 2), side, side)
        painter.end()

    def set_severity(self, severity: Severity) -> None:
        """Change the badge color."""
        self._severity = severity
        self.update()

    def set_value(self, value: int | None) -> None:
        """Show a number (or a dot when `None`)."""
        self._value = value
        self.updateGeometry()
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return a dot, an icon disc, or a pill wide enough for the number."""
        if self._value is None:
            side = 16 if self._icon else 6
            return QSize(side, side)
        width = self.fontMetrics().horizontalAdvance(self._text()) + 10
        return QSize(max(16, width), 16)

    def value(self) -> int | None:
        """Return the number (or `None`)."""
        return self._value

    def _text(self) -> str:
        if self._value is None:
            return ""
        return f"{_BADGE_MAX_VALUE}+" if self._value > _BADGE_MAX_VALUE else str(self._value)


class FluentLCDNumber(QLCDNumber):
    """Seven-segment number display in the accent color."""

    def __init__(self, digits: int = 6, parent: QWidget | None = None) -> None:
        """Create an LCD display with `digits` positions."""
        super().__init__(digits, parent)
        self.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.setFrameShape(QLCDNumber.Shape.NoFrame)
        self.setMinimumHeight(48)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-color segments and background."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QLCDNumber {{ color: {css(palette.accent)}; background: {css(palette.card_bg)};"
            f" border: 1px solid {css(palette.card_stroke)}; border-radius: {RADIUS_CONTROL}px; }}",
        )


class FluentPersonPicture(QWidget):
    """Round avatar: a picture, initials, or the default person glyph."""

    def __init__(
        self, parent: QWidget | None = None, *, name: str = "", pixmap: QPixmap | None = None, size: int = 48
    ) -> None:
        """Create an avatar.

        Args:

        - `parent` (`QWidget | None`): Optional parent.
        - `name` (`str`): Display name used for initials.
        - `pixmap` (`QPixmap | None`): Picture (cropped to a circle).
        - `size` (`int`): Diameter in pixels. Defaults to `48`.

        """
        super().__init__(parent)
        self._name = name
        self._pixmap = pixmap
        self.setFixedSize(size, size)
        bind_theme(self, self.update)

    def initials(self) -> str:
        """Return up to two initials from the display name."""
        parts = [part for part in self._name.split() if part]
        return "".join(part[0] for part in parts[:2]).upper()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the circle with the picture, initials, or glyph."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        if self._pixmap is not None and not self._pixmap.isNull():
            painter.setClipPath(rounded_path(rect, rect.width() / 2))
            scaled = self._pixmap.scaled(
                self.size() * self.devicePixelRatioF(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            scaled.setDevicePixelRatio(self.devicePixelRatioF())
            painter.drawPixmap(0, 0, scaled)
            painter.end()
            return
        paint_surface(
            painter, rect, palette.control_strong_fill if not self._name else palette.accent, None, rect.width() / 2
        )
        initials = self.initials()
        if initials:
            painter.setPen(palette.text_on_accent)
            font = QFont(self.font())
            font.setPixelSize(max(8, int(rect.height() * 0.4)))
            font.setWeight(QFont.Weight.DemiBold)
            painter.setFont(font)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), initials)
        else:
            side = int(rect.width() * 0.5)
            icon = themed_icon("user", palette, palette.solid_quarternary_bg, side)
            icon.paint(painter, int((rect.width() - side) / 2), int((rect.height() - side) / 2), side, side)
        painter.end()

    def set_name(self, name: str) -> None:
        """Change the display name."""
        self._name = name
        self.update()

    def set_pixmap(self, pixmap: QPixmap | None) -> None:
        """Change the picture."""
        self._pixmap = pixmap
        self.update()


class FluentProgressBar(QWidget):
    """Thin progress bar with a determinate and an indeterminate (busy) mode."""

    def __init__(self, parent: QWidget | None = None, *, minimum: int = 0, maximum: int = 100) -> None:
        """Create a progress bar."""
        super().__init__(parent)
        self._minimum = minimum
        self._maximum = maximum
        self._value = minimum
        self._busy = False
        self._phase = 0.0
        self._paused = False
        self._error = False
        self._timer = QTimer(self)
        self._timer.setInterval(_BUSY_INTERVAL_MS)
        self._timer.timeout.connect(self._advance)
        self.setFixedHeight(SPACE_XS)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bind_theme(self, self.update)

    def is_busy(self) -> bool:
        """Return whether the indeterminate animation runs."""
        return self._busy

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the rail and the indicator."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        rail = QRectF(rect.left(), rect.center().y() - 0.5, rect.width(), 1)
        paint_surface(painter, rail, palette.control_strong_stroke, None, 0.5)
        color = palette.critical if self._error else palette.caution if self._paused else palette.accent
        height = 3.0
        top = rect.center().y() - height / 2
        if self._busy:
            span = rect.width() * 0.4
            start = (rect.width() + span) * self._phase - span
            bar = QRectF(max(0.0, start), top, min(span, rect.width() - max(0.0, start)), height)
        else:
            total = max(1, self._maximum - self._minimum)
            bar = QRectF(0, top, rect.width() * (self._value - self._minimum) / total, height)
        if bar.width() > 0:
            paint_surface(painter, bar, color, None, height / 2)
        painter.end()

    def set_busy(self, *, busy: bool) -> None:
        """Start or stop the indeterminate animation."""
        self._busy = busy
        if busy:
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def set_error(self, *, error: bool) -> None:
        """Show the critical color."""
        self._error = error
        self.update()

    def set_paused(self, *, paused: bool) -> None:
        """Show the caution color."""
        self._paused = paused
        self.update()

    def set_range(self, minimum: int, maximum: int) -> None:
        """Set the value range."""
        self._minimum, self._maximum = minimum, maximum
        self.update()

    def set_value(self, value: int) -> None:
        """Set the progress value."""
        self._value = max(self._minimum, min(self._maximum, value))
        self.update()

    def value(self) -> int:
        """Return the progress value."""
        return self._value

    def _advance(self) -> None:
        self._phase = (self._phase + 0.012) % 1.0
        self.update()


class FluentProgressRing(QWidget):
    """Circular progress (determinate arc or spinning busy arc) with optional percent."""

    def __init__(self, parent: QWidget | None = None, *, size: int = 40, show_text: bool = False) -> None:
        """Create a progress ring."""
        super().__init__(parent)
        self._value = 0
        self._busy = False
        self._angle = 0.0
        self._show_text = show_text
        self._timer = QTimer(self)
        self._timer.setInterval(_BUSY_INTERVAL_MS)
        self._timer.timeout.connect(self._advance)
        self.setFixedSize(size, size)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the track and arc."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        stroke = max(3.0, self.width() / 12)
        rect = QRectF(self.rect()).adjusted(stroke, stroke, -stroke, -stroke)
        if not self._busy:
            track = QPen(palette.control_strong_stroke if not palette.dark else palette.control_strong_fill, stroke)
            painter.setPen(track)
            painter.drawEllipse(rect)
        pen = QPen(palette.accent, stroke)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        if self._busy:
            span = 100 + 80 * math.sin(math.radians(self._angle * 2))
            painter.drawArc(rect, int((90 - self._angle) * 16), int(-span * 16))
        elif self._value > 0:
            painter.drawArc(rect, 90 * 16, int(-360 * 16 * self._value / 100))
        if self._show_text and not self._busy:
            painter.setPen(palette.text_primary)
            painter.drawText(QRectF(self.rect()), int(Qt.AlignmentFlag.AlignCenter), f"{self._value}%")
        painter.end()

    def set_busy(self, *, busy: bool) -> None:
        """Start or stop the spinning animation."""
        self._busy = busy
        if busy:
            self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def set_value(self, value: int) -> None:
        """Set the percentage (0-100)."""
        self._value = max(0, min(100, value))
        self.update()

    def value(self) -> int:
        """Return the percentage."""
        return self._value

    def _advance(self) -> None:
        self._angle = (self._angle + 6) % 360
        self.update()


class FluentQRCode(QWidget):
    """QR code for a text or URL, painted in the theme text color."""

    def __init__(
        self, text: str = "", parent: QWidget | None = None, *, size: int = 160, ecc: Ecc = Ecc.MEDIUM
    ) -> None:
        """Create a QR code view."""
        super().__init__(parent)
        self._ecc = ecc
        self._modules: list[list[bool]] = []
        self._dark: QColor | None = None
        self._light: QColor | None = None
        self.setFixedSize(size, size)
        self.set_text(text)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the quiet zone and modules."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        light = self._light or QColor("#ffffff")
        dark = self._dark or QColor("#000000")
        paint_surface(painter, self.rect(), light, palette.card_stroke, RADIUS_CONTROL)
        self._paint_modules(painter, QRectF(self.rect()), dark)
        painter.end()

    def set_colors(self, dark: QColor | None, light: QColor | None) -> None:
        """Override module colors (`None` = black on white for reliable scanning)."""
        self._dark, self._light = dark, light
        self.update()

    def set_text(self, text: str) -> None:
        """Encode a new payload."""
        self._text = text
        self._modules = encode_qr(text, self._ecc) if text else []
        self.update()

    def text(self) -> str:
        """Return the encoded payload."""
        return self._text

    def to_pixmap(self, size: int = 512) -> QPixmap:
        """Render the code to a square pixmap (black on white)."""
        pixmap = QPixmap(size, size)
        pixmap.fill(self._light or QColor("#ffffff"))
        painter = antialiased_painter(pixmap)
        painter.setRenderHint(painter.RenderHint.Antialiasing, on=False)
        self._paint_modules(painter, QRectF(0, 0, size, size), self._dark or QColor("#000000"))
        painter.end()
        return pixmap

    def _paint_modules(self, painter: QPainter, rect: QRectF, color: QColor) -> None:
        if not self._modules:
            return
        count = len(self._modules) + 8
        cell = min(rect.width(), rect.height()) / count
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        for y, row in enumerate(self._modules):
            for x, dark in enumerate(row):
                if dark:
                    painter.drawRect(
                        QRectF(rect.left() + (x + 4) * cell, rect.top() + (y + 4) * cell, cell + 0.3, cell + 0.3)
                    )


class FluentSkeleton(QWidget):
    """Loading placeholder with a moving shimmer."""

    def __init__(self, parent: QWidget | None = None, *, shape: SkeletonShape = SkeletonShape.TEXT) -> None:
        """Create a skeleton placeholder."""
        super().__init__(parent)
        self._shape = shape
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(_BUSY_INTERVAL_MS * 2)
        self._timer.timeout.connect(self._advance)
        self._timer.start()
        if shape == SkeletonShape.TEXT:
            self.setFixedHeight(14)
        elif shape == SkeletonShape.CIRCLE:
            self.setFixedSize(40, 40)
        else:
            self.setMinimumHeight(80)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the shape with a gradient band moving across it."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        base = palette.subtle_hover if not palette.dark else palette.control_fill_hover
        highlight = with_alpha(palette.text_primary, 18)
        gradient = QLinearGradient(
            rect.left() - rect.width() + rect.width() * 2 * self._phase,
            0,
            rect.left() + rect.width() * 2 * self._phase,
            0,
        )
        gradient.setColorAt(0.0, base)
        gradient.setColorAt(0.5, highlight)
        gradient.setColorAt(1.0, base)
        radius = rect.height() / 2 if self._shape == SkeletonShape.CIRCLE else RADIUS_CONTROL
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()

    def stop(self) -> None:
        """Stop the shimmer animation."""
        self._timer.stop()

    def _advance(self) -> None:
        self._phase = (self._phase + 0.02) % 1.0
        self.update()


class FluentStatCard(QWidget):
    """Card with a big number, a trend arrow, a title, and a description."""

    def __init__(
        self,
        title: str,
        value: str,
        parent: QWidget | None = None,
        *,
        description: str = "",
        trend: Trend = Trend.FLAT,
        trend_text: str = "",
        icon: str = "",
    ) -> None:
        """Create a stat card."""
        super().__init__(parent)
        self._trend = trend
        self._icon_name = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_M)
        layout.setSpacing(SPACE_XS)
        header = QHBoxLayout()
        self._title = CaptionLabel(title, self)
        header.addWidget(self._title)
        header.addStretch(1)
        layout.addLayout(header)
        row = QHBoxLayout()
        self._value = FluentText(value, self, style=TextStyle.TITLE)
        self._trend_label = FluentText(trend_text, self, style=TextStyle.BODY_STRONG)
        row.addWidget(self._value)
        row.addWidget(self._trend_label, 0, Qt.AlignmentFlag.AlignBottom)
        row.addStretch(1)
        layout.addLayout(row)
        self._description = CaptionLabel(description, self)
        self._description.setVisible(bool(description))
        layout.addWidget(self._description)
        bind_theme(self, self.refresh_theme)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card surface and the corner icon."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        if self._icon_name:
            icon = themed_icon(self._icon_name, palette, palette.text_secondary, ICON_SIZE_LARGE)
            icon.paint(painter, self.width() - SPACE_L - ICON_SIZE_LARGE, SPACE_M, ICON_SIZE_LARGE, ICON_SIZE_LARGE)
        painter.end()

    def refresh_theme(self) -> None:
        """Re-color the trend text."""
        palette = palette_for(self)
        color = {Trend.UP: palette.success, Trend.DOWN: palette.critical, Trend.FLAT: palette.text_secondary}[
            self._trend
        ]
        arrow = {Trend.UP: "▲ ", Trend.DOWN: "▼ ", Trend.FLAT: ""}[self._trend]
        text = self._trend_label.text().lstrip("▲▼ ")
        self._trend_label.setText(f"{arrow}{text}" if text else "")
        self._trend_label.setStyleSheet(f"QLabel {{ color: {css(color)}; background: transparent; }}")
        self.update()

    def set_value(self, value: str, *, trend: Trend | None = None, trend_text: str | None = None) -> None:
        """Update the number and optionally the trend."""
        self._value.setText(value)
        if trend is not None:
            self._trend = trend
        if trend_text is not None:
            self._trend_label.setText(trend_text)
        self.refresh_theme()


class FluentSteps(QWidget):
    """Horizontal step indicator: finished, current, and pending steps."""

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, steps: Sequence[str] = ()) -> None:
        """Create a step indicator."""
        super().__init__(parent)
        self._steps = list(steps)
        self._current = 0
        self.setMinimumHeight(56)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bind_theme(self, self.update)

    def count(self) -> int:
        """Return the number of steps."""
        return len(self._steps)

    def current(self) -> int:
        """Return the current step index."""
        return self._current

    def next_step(self) -> None:
        """Advance to the next step."""
        self.set_current(self._current + 1)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint circles, connectors, and labels."""
        if not self._steps:
            return
        palette = palette_for(self)
        painter = antialiased_painter(self)
        count = len(self._steps)
        width = self.width() / count
        radius = 12
        cy = radius + 4
        for index, title in enumerate(self._steps):
            cx = width * index + width / 2
            if index + 1 < count:
                color = palette.accent if index < self._current else palette.control_strong_stroke
                painter.setPen(QPen(color, 2))
                painter.drawLine(int(cx + radius + 4), cy, int(cx + width - radius - 4), cy)
            circle = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            done = index < self._current
            current = index == self._current
            if done or current:
                paint_surface(painter, circle, palette.accent, None, radius)
                painter.setPen(palette.text_on_accent)
            else:
                paint_surface(painter, circle, None, palette.control_strong_stroke, radius, stroke_width=1.5)
                painter.setPen(palette.text_secondary)
            painter.drawText(circle, int(Qt.AlignmentFlag.AlignCenter), "✓" if done else str(index + 1))
            painter.setPen(palette.text_primary if current else palette.text_secondary)
            label = QRectF(cx - width / 2, cy + radius + 4, width, 20)
            painter.drawText(label, int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop), title)
        painter.end()

    def previous_step(self) -> None:
        """Go back one step."""
        self.set_current(self._current - 1)

    def set_current(self, index: int) -> None:
        """Select a step (clamped)."""
        index = max(0, min(len(self._steps), index))
        if index == self._current:
            return
        self._current = index
        self.update()
        self.current_changed.emit(index)

    def set_steps(self, steps: Sequence[str]) -> None:
        """Replace step titles."""
        self._steps = list(steps)
        self._current = min(self._current, len(self._steps))
        self.update()


class FluentTag(QWidget):
    """Rounded tag (chip) that can be closable or checkable."""

    closed = Signal()
    toggled = Signal(bool)

    def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        severity: Severity = Severity.NEUTRAL,
        closable: bool = False,
        checkable: bool = False,
    ) -> None:
        """Create a tag."""
        super().__init__(parent)
        self._text = text
        self._severity = severity
        self._closable = closable
        self._checkable = checkable
        self._checked = False
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if closable or checkable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.update)

    def is_checked(self) -> bool:
        """Return the checked state (checkable tags only)."""
        return self._checked

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Close when the close glyph is clicked; toggle checkable tags."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._closable and event.position().x() >= self.width() - 22:
            self.closed.emit()
            self.hide()
            return
        if self._checkable:
            self.set_checked(checked=not self._checked)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the tag body, text, and close glyph."""
        palette = palette_for(self)
        foreground, background = severity_colors(palette, self._severity)
        if self._checkable and self._checked:
            foreground, background = palette.text_on_accent, palette.accent
        painter = antialiased_painter(self)
        rect = QRectF(self.rect())
        paint_surface(painter, rect, background, with_alpha(foreground, 60), rect.height() / 2)
        painter.setPen(foreground)
        text_rect = rect.adjusted(SPACE_M, 0, -(22 if self._closable else SPACE_M), 0)
        painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), self._text)
        if self._closable:
            icon = themed_icon("x", palette, foreground, 12)
            icon.paint(painter, int(rect.right() - 18), int(rect.center().y() - 6), 12, 12)
        painter.end()

    def set_checked(self, *, checked: bool) -> None:
        """Set the checked state and emit `toggled`."""
        if self._checked == checked:
            return
        self._checked = checked
        self.update()
        self.toggled.emit(checked)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return text width plus padding (and the close glyph)."""
        extra = 22 if self._closable else SPACE_M
        return QSize(self.fontMetrics().horizontalAdvance(self._text) + SPACE_M + extra, CONTROL_HEIGHT - 8)

    def text(self) -> str:
        """Return the tag text."""
        return self._text


class FluentTimeline(QWidget):
    """Vertical timeline: dots on a rail with time, title, and text."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty timeline."""
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACE_L + SPACE_S, 0, 0, 0)
        self._layout.setSpacing(SPACE_L)
        self._entries: list[tuple[TimelineEntry, QWidget]] = []
        bind_theme(self, self.update)

    def add_entry(self, entry: TimelineEntry) -> None:
        """Append an event."""
        block = QWidget(self)
        column = QVBoxLayout(block)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(2)
        column.addWidget(CaptionLabel(entry.timestamp, block))
        column.addWidget(FluentText(entry.title, block, style=TextStyle.BODY_STRONG))
        if entry.content:
            column.addWidget(FluentText(entry.content, block, role=TextRole.SECONDARY, word_wrap=True))
        self._layout.addWidget(block)
        self._entries.append((entry, block))
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the rail and the dots next to each event."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        x = SPACE_S
        if len(self._entries) > 1:
            first = self._entries[0][1].geometry().top() + 8
            last = self._entries[-1][1].geometry().top() + 8
            painter.setPen(QPen(palette.divider if not palette.dark else palette.control_strong_stroke, 2))
            painter.drawLine(x, first, x, last)
        for entry, block in self._entries:
            foreground, _ = severity_colors(palette, entry.severity)
            y = block.geometry().top() + 8
            paint_surface(
                painter, QRectF(x - 5, y - 5, 10, 10), foreground, palette.solid_quarternary_bg, 5, stroke_width=2
            )
        painter.end()


@dataclass
class TimelineEntry:
    """One event on a `FluentTimeline`."""

    timestamp: str
    title: str
    content: str = ""
    severity: Severity = Severity.ACCENT


class _CountdownTile(QWidget):
    def __init__(self, caption: str, parent: QWidget) -> None:
        super().__init__(parent)
        column = QVBoxLayout(self)
        column.setContentsMargins(SPACE_M, SPACE_S, SPACE_M, SPACE_S)
        column.setSpacing(0)
        self.value_label = FluentText("00", self, style=TextStyle.TITLE)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption_label = CaptionLabel(caption, self)
        caption_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(self.value_label)
        column.addWidget(caption_label)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.setPen(QPen(palette.divider, 1))
        y = self.height() // 2
        painter.drawLine(SPACE_XS, y, self.width() - SPACE_XS, y)
        painter.end()


def severity_colors(palette: FluentPalette, severity: Severity) -> tuple[QColor, QColor]:
    """Return `(foreground, background)` colors for a severity."""
    return {
        Severity.ACCENT: (palette.accent, with_alpha(palette.accent, 40)),
        Severity.SUCCESS: (palette.success, palette.success_bg),
        Severity.CAUTION: (palette.caution, palette.caution_bg),
        Severity.CRITICAL: (palette.critical, palette.critical_bg),
        Severity.NEUTRAL: (palette.neutral, palette.neutral_bg),
    }[severity]


def severity_icon_name(severity: Severity) -> str:
    """Return the Lucide icon that represents a severity."""
    return {
        Severity.ACCENT: "info",
        Severity.SUCCESS: "circle-check",
        Severity.CAUTION: "triangle-alert",
        Severity.CRITICAL: "circle-x",
        Severity.NEUTRAL: "info",
    }[severity]
