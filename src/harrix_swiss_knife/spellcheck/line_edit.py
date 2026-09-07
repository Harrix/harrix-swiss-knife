"""Wavy red underlines for `QLineEdit` (no document/highlighter)."""

from __future__ import annotations

import contextlib

from PySide6.QtCore import QObject, QRect, QTimer
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QPaintEvent, QPen
from PySide6.QtWidgets import QLineEdit, QStyle, QStyleOptionFrame

from harrix_swiss_knife.spellcheck.engine import SpellEngine, get_spell_engine
from harrix_swiss_knife.spellcheck.tokenize import iter_word_spans

_WAVE_COLOR = QColor(220, 50, 47)
_DEBOUNCE_MS = 300


class LineEditSpellController(QObject):
    """Debounced misspelling ranges and post-paint wave underlines for a line edit."""

    def __init__(self, line_edit: QLineEdit, engine: SpellEngine | None = None) -> None:
        """Attach to `line_edit`; owns a debounce timer for `textChanged`."""
        super().__init__(line_edit)
        self._line_edit = line_edit
        self._engine = engine if engine is not None else get_spell_engine()
        self._misspellings: list[tuple[int, int]] = []
        self._original_paint = line_edit.paintEvent
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(_DEBOUNCE_MS)
        self._timer.timeout.connect(self._recompute)
        line_edit.textChanged.connect(self._schedule)
        line_edit.paintEvent = self._paint_event  # ty: ignore[invalid-assignment]
        self._recompute()

    def detach(self) -> None:
        """Restore the original `paintEvent` and stop listening."""
        self._timer.stop()
        with contextlib.suppress(TypeError, RuntimeError):
            self._line_edit.textChanged.disconnect(self._schedule)
        self._line_edit.paintEvent = self._original_paint  # ty: ignore[invalid-assignment]
        self._misspellings.clear()
        self._line_edit.update()

    def misspellings(self) -> list[tuple[int, int]]:
        """Return current `[start, end)` misspelled spans."""
        return list(self._misspellings)

    def refresh(self) -> None:
        """Recompute misspellings immediately (e.g. after Add to dictionary)."""
        self._timer.stop()
        self._recompute()

    def _draw_underlines(self, painter: QPainter) -> None:
        line_edit = self._line_edit
        text = line_edit.text()
        if not text:
            return
        option = QStyleOptionFrame()
        line_edit.initStyleOption(option)
        contents = line_edit.style().subElementRect(QStyle.SubElement.SE_LineEditContents, option, line_edit)
        margins = line_edit.textMargins()
        left = contents.left() + margins.left()
        fm = line_edit.fontMetrics()
        scroll_x = _line_edit_scroll_x(line_edit, contents.x() + margins.left())
        underline_y = _line_edit_underline_y(line_edit, contents, margins.top(), margins.bottom(), fm)
        painter.setClipRect(contents)
        painter.setPen(QPen(_WAVE_COLOR, 1))
        for start, end in self._misspellings:
            x1 = left + fm.horizontalAdvance(text[:start]) - scroll_x
            x2 = left + fm.horizontalAdvance(text[:end]) - scroll_x
            if x2 <= contents.left() or x1 >= contents.right():
                continue
            x1 = max(x1, float(contents.left()))
            x2 = min(x2, float(contents.right()))
            _draw_wave(painter, x1, x2, float(underline_y))

    def _paint_event(self, event: QPaintEvent) -> None:
        self._original_paint(event)
        if not self._misspellings:
            return
        painter = QPainter(self._line_edit)
        if not painter.isActive():
            return
        try:
            self._draw_underlines(painter)
        finally:
            painter.end()

    def _recompute(self) -> None:
        text = self._line_edit.text()
        engine = self._engine
        spans = [(start, end) for start, end, word in iter_word_spans(text) if not engine.lookup(word)]
        self._misspellings = spans
        self._line_edit.update()

    def _schedule(self, _text: str = "") -> None:
        self._timer.start()


def _draw_wave(painter: QPainter, x1: float, x2: float, y: float) -> None:
    if x2 - x1 < 1:
        return
    path = QPainterPath()
    path.moveTo(x1, y)
    x = x1
    up = True
    step = 2.0
    amp = 1.2
    while x < x2:
        next_x = min(x + step, x2)
        path.lineTo(next_x, y - amp if up else y + amp)
        x = next_x
        up = not up
    painter.drawPath(path)


def _line_edit_scroll_x(line_edit: QLineEdit, content_left: int) -> int:
    """Estimate horizontal scroll from cursor rect vs. text advance."""
    cursor = line_edit.cursorPosition()
    text = line_edit.text()
    advance = line_edit.fontMetrics().horizontalAdvance(text[:cursor])
    cursor_x = line_edit.cursorRect().x()
    return max(0, advance - (cursor_x - content_left))


def _line_edit_underline_y(
    line_edit: QLineEdit,
    contents: QRect,
    margin_top: int,
    margin_bottom: int,
    fm: QFontMetrics,
) -> int:
    """Y for the wave: under the baseline, matching QLineEdit vertical centering."""
    # Prefer the live caret rect — Qt already vertically centers text there.
    cursor_rect = line_edit.cursorRect()
    underline_from_baseline = max(1, fm.underlinePos())
    if cursor_rect.height() > 0:
        return min(cursor_rect.top() + fm.ascent() + underline_from_baseline, contents.bottom() - 1)

    available = contents.height() - margin_top - margin_bottom
    v_offset = max(0, (available - fm.height()) // 2)
    baseline = contents.top() + margin_top + v_offset + fm.ascent()
    return min(baseline + underline_from_baseline, contents.bottom() - 1)
