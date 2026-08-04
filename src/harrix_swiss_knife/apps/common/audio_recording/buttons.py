"""Painted record / playback control buttons."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QEnterEvent, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

RECORD_BUTTON_SIZE = 56
PLAY_BUTTON_SIZE = 40
PLAY_BUTTON_GAP = 12

RECORD_CAPTION_IDLE_STYLE = """
    QLabel {
        color: #c62828;
    }
    QLabel:hover {
        color: #e53935;
    }
"""

RECORD_CAPTION_STOP_STYLE = """
    QLabel {
        color: #1a1a1a;
    }
    QLabel:hover {
        color: #333333;
    }
"""


class ClickableLabel(QLabel):
    """Label that emits `clicked` on left mouse press."""

    clicked = Signal()

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        """Initialize clickable label."""
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit `clicked` for left-button presses."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class PauseButton(QPushButton):
    """Pause button with two vertical bars."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize pause button."""
        super().__init__(parent)
        self.setFixedSize(PLAY_BUTTON_SIZE, PLAY_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Pause playback")
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Highlight the pause icon on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Restore the pause icon when the pointer leaves."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw the pause icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#1565c0")
        if self.isDown():
            color = QColor("#0d47a1")
        elif self.underMouse():
            color = QColor("#1e88e5")

        bar_width = 5.0
        bar_height = 18.0
        gap = 5.0
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        left_x = center_x - gap / 2.0 - bar_width
        right_x = center_x + gap / 2.0
        top_y = center_y - bar_height / 2.0

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(QRectF(left_x, top_y, bar_width, bar_height), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(right_x, top_y, bar_width, bar_height), 1.5, 1.5)


class PlayButton(QPushButton):
    """Triangle play button for previewing a finished recording."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize play button."""
        super().__init__(parent)
        self.setFixedSize(PLAY_BUTTON_SIZE, PLAY_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Play recording")
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Repaint on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint when hover ends."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint a right-pointing triangle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#2e7d32")
        if self.isDown():
            color = QColor("#1b5e20")
        elif self.underMouse():
            color = QColor("#43a047")

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        triangle_height = 18.0
        triangle_width = 16.0
        left = center_x - triangle_width / 2.0 + 1.0
        top = center_y - triangle_height / 2.0
        triangle = QPolygonF(
            [
                QPointF(left, top),
                QPointF(left, top + triangle_height),
                QPointF(left + triangle_width, center_y),
            ]
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(triangle)


class RecordButton(QPushButton):
    """Record control: red ring + dot when idle, black rounded stop square while recording."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize record button."""
        super().__init__(parent)
        self._recording = False
        self.setFixedSize(RECORD_BUTTON_SIZE, RECORD_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Repaint on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint when hover ends."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint record ring or stop square."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0

        if self._recording:
            stop_side = 22.0
            corner_radius = 5.0
            stop_color = QColor("#000000")
            if self.isDown():
                stop_color = QColor("#333333")
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(stop_color)
            painter.drawRoundedRect(
                QRectF(
                    center_x - stop_side / 2.0,
                    center_y - stop_side / 2.0,
                    stop_side,
                    stop_side,
                ),
                corner_radius,
                corner_radius,
            )
            return

        red = QColor("#e53935")
        if self.isDown():
            red = QColor("#c62828")
        elif self.underMouse():
            red = QColor("#ef5350")

        outer_radius = 23.0
        ring_width = 2.5
        inner_radius = 16.0

        painter.setPen(QPen(red, ring_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            QRectF(
                center_x - outer_radius,
                center_y - outer_radius,
                outer_radius * 2.0,
                outer_radius * 2.0,
            )
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(red)
        painter.drawEllipse(
            QRectF(
                center_x - inner_radius,
                center_y - inner_radius,
                inner_radius * 2.0,
                inner_radius * 2.0,
            )
        )

    def set_recording(self, *, recording: bool) -> None:
        """Switch between record and stop appearance."""
        if self._recording != recording:
            self._recording = recording
            self.update()


class StopPlaybackButton(QPushButton):
    """Stop button for ending audio preview."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize stop button."""
        super().__init__(parent)
        self.setFixedSize(PLAY_BUTTON_SIZE, PLAY_BUTTON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Stop playback")
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Highlight the stop icon on hover."""
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: ANN001, N802
        """Restore the stop icon when the pointer leaves."""
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw the stop icon."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#212121")
        if self.isDown():
            color = QColor("#000000")
        elif self.underMouse():
            color = QColor("#424242")

        side = 16.0
        corner_radius = 3.0
        center_x = self.width() / 2.0
        center_y = self.height() / 2.0

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(
            QRectF(center_x - side / 2.0, center_y - side / 2.0, side, side),
            corner_radius,
            corner_radius,
        )
