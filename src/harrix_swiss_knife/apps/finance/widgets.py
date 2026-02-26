"""Custom widgets for finance tracker."""

from __future__ import annotations

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QLabel


class ClickableCategoryLabel(QLabel):
    """QLabel with dropdown arrow indicator on the right side."""

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Override paintEvent to draw dropdown arrow."""
        super().paintEvent(event)

        # Draw dropdown arrow on the right side
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get arrow size and position
        arrow_size = 8
        margin = 4
        rect = self.rect()
        arrow_x = rect.width() - arrow_size - margin
        arrow_y = rect.height() // 2

        # Get text color for arrow
        text_color = self.palette().color(self.palette().ColorRole.WindowText)
        painter.setPen(text_color)
        painter.setBrush(text_color)

        # Draw triangle pointing down
        points = [
            QPoint(arrow_x, arrow_y - arrow_size // 2),
            QPoint(arrow_x + arrow_size, arrow_y - arrow_size // 2),
            QPoint(arrow_x + arrow_size // 2, arrow_y + arrow_size // 2),
        ]
        painter.drawPolygon(points)
