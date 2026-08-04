"""Live scrolling and full-recording waveform display."""

from __future__ import annotations

from collections import deque
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife.apps.common.audio_recording.pcm_utils import waveform_buckets_from_pcm

LEVEL_BAR_COUNT = 120
WAVEFORM_BG = QColor("#1e1e1e")
WAVEFORM_GRID = QColor("#3a3a3a")
WAVEFORM_CENTER = QColor("#616161")
WAVEFORM_FILL = QColor(76, 175, 80, 200)
WAVEFORM_OUTLINE = QColor("#81c784")
WAVEFORM_LIVE_FILL = QColor(102, 187, 106, 210)
WAVEFORM_PLAYHEAD = QColor("#ffeb3b")


class AudioLevelWidget(QWidget):
    """Live scrolling and full-recording waveform display."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize waveform widget."""
        super().__init__(parent)
        self._mode: Literal["idle", "live", "overview"] = "idle"
        self._live_buckets: deque[tuple[float, float]] = deque(
            [(0.0, 0.0)] * LEVEL_BAR_COUNT,
            maxlen=LEVEL_BAR_COUNT,
        )
        self._overview_pcm = b""
        self._playback_ratio: float | None = None
        self.setMinimumHeight(72)
        self.setVisible(False)

    def begin_live(self) -> None:
        """Switch to scrolling live waveform mode."""
        self._mode = "live"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * LEVEL_BAR_COUNT, maxlen=LEVEL_BAR_COUNT)
        self.setVisible(True)
        self.update()

    def clear(self) -> None:
        """Reset widget to idle state."""
        self._mode = "idle"
        self._overview_pcm = b""
        self._playback_ratio = None
        self._live_buckets = deque([(0.0, 0.0)] * LEVEL_BAR_COUNT, maxlen=LEVEL_BAR_COUNT)
        self.setVisible(False)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Paint live or overview waveform."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return

        painter.fillRect(0, 0, width, height, WAVEFORM_BG)
        center_y = height / 2.0
        margin = 8
        half_height = max(4.0, (height - margin * 2) / 2.0)

        for ratio in (0.25, 0.75):
            grid_y = margin + ratio * (height - margin * 2)
            painter.setPen(QPen(WAVEFORM_GRID, 1, Qt.PenStyle.DotLine))
            painter.drawLine(0, int(grid_y), width, int(grid_y))

        painter.setPen(QPen(WAVEFORM_CENTER, 1))
        painter.drawLine(0, int(center_y), width, int(center_y))

        if self._mode == "live":
            buckets = list(self._live_buckets)
            fill_color = WAVEFORM_LIVE_FILL
        elif self._mode == "overview" and self._overview_pcm:
            bucket_count = max(32, width // 2)
            buckets = waveform_buckets_from_pcm(self._overview_pcm, bucket_count)
            fill_color = WAVEFORM_FILL
        else:
            return

        if not buckets:
            return

        path = QPainterPath()
        path.moveTo(0.0, center_y)
        bucket_width = width / len(buckets)
        for index, (_peak_neg, peak_pos) in enumerate(buckets):
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_pos * half_height)

        last_x = (len(buckets) - 1) * bucket_width + bucket_width / 2.0
        path.lineTo(last_x, center_y)

        for index in range(len(buckets) - 1, -1, -1):
            peak_neg, _peak_pos = buckets[index]
            x = index * bucket_width + bucket_width / 2.0
            path.lineTo(x, center_y - peak_neg * half_height)

        path.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fill_color)
        painter.drawPath(path)

        painter.setPen(QPen(WAVEFORM_OUTLINE, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        if self._mode == "overview" and self._playback_ratio is not None:
            playhead_x = max(0.0, min(float(width), self._playback_ratio * width))
            painter.setPen(QPen(WAVEFORM_PLAYHEAD, 2))
            painter.drawLine(int(playhead_x), 0, int(playhead_x), height)

    def push_envelope(self, peak_neg: float, peak_pos: float) -> None:
        """Append one live waveform bucket and repaint."""
        if self._mode != "live":
            return
        self._live_buckets.append((peak_neg, peak_pos))
        self.update()

    def resizeEvent(self, event) -> None:  # noqa: ANN001, N802
        """Repaint overview buckets when the widget is resized."""
        super().resizeEvent(event)
        if self._mode == "overview":
            self.update()

    def set_playback_position(self, ratio: float | None) -> None:
        """Set playhead position from 0 to 1, or hide it when `ratio` is `None`."""
        if self._playback_ratio != ratio:
            self._playback_ratio = ratio
            self.update()

    def show_overview(self, pcm_data: bytes) -> None:
        """Show the full recording waveform."""
        self._mode = "overview"
        self._overview_pcm = pcm_data
        self._playback_ratio = None
        self.setVisible(bool(pcm_data))
        self.update()
