"""Qt helper for creating emoji icons without clipping.

Some emoji glyphs have a tight bounding box that is taller than it is wide.
If we scale naively by width (or pick a fixed point size), the glyph can be
visually clipped (often at the bottom). This helper sizes the font using the
glyph's tight bounding rect and centers the result without clipping.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QFont, QFontMetricsF, QIcon, QPainter, QPixmap


def create_emoji_icon(emoji: str, size: int = 64) -> QIcon:
    """Create a square `QIcon` for an emoji, scaled to avoid clipping."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

    target = float(size) * 0.90
    base_font = QFont()
    base_font.setPointSizeF(float(size))

    metrics = QFontMetricsF(base_font)
    rect = metrics.tightBoundingRect(emoji)
    rect_w = max(rect.width(), 1.0)
    rect_h = max(rect.height(), 1.0)

    # If the glyph is taller than wide, fit by height; otherwise fit by width.
    scale = (target / rect_h) if (rect_h > rect_w) else (target / rect_w)

    font = QFont(base_font)
    font.setPointSizeF(max(1.0, base_font.pointSizeF() * scale))
    painter.setFont(font)

    metrics2 = QFontMetricsF(font)
    rect2 = metrics2.tightBoundingRect(emoji)

    x = (float(size) - rect2.width()) / 2.0
    y = (float(size) - rect2.height()) / 2.0
    baseline = QPointF(x - rect2.left(), y - rect2.top())

    painter.drawText(baseline, emoji)
    painter.end()

    return QIcon(pixmap)

