"""Looping roller and the roller-based picker button."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QPoint, QRectF, QSize, Qt, QVariantAnimation, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.style import scroll_bar_qss
from harrix_swiss_knife.fluent.theme import bind_theme, css, fluent_font, palette_for
from harrix_swiss_knife.fluent.tokens import (
    RADIUS_CONTROL,
    RADIUS_OVERLAY,
    SPACE_S,
    SPACE_XS,
    TYPE_BODY,
)
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentPrimaryButton

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtGui import QMouseEvent, QPaintEvent, QWheelEvent

_CLICK_SLOP_PX = 3
_ROLLER_ROW_HEIGHT = 40
_ROLLER_VISIBLE_ROWS = 7
_ROLLER_WIDTH = 80


class FluentRoller(QWidget):
    """Vertical scroll wheel of values that snaps to the middle row."""

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = (), looping: bool = False) -> None:
        """Create a roller."""
        super().__init__(parent)
        self._items = list(items)
        self._looping = looping
        self._offset = 0.0
        self._current = 0
        self._drag_y: float | None = None
        self._press_y = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation)
        self.setFixedSize(_ROLLER_WIDTH, _ROLLER_ROW_HEIGHT * _ROLLER_VISIBLE_ROWS)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.update)

    def current_index(self) -> int:
        """Return the selected index."""
        return self._current

    def current_text(self) -> str:
        """Return the selected item."""
        return self._items[self._current] if self._items else ""

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Drag the wheel."""
        if self._drag_y is None:
            return
        delta = event.position().y() - self._drag_y
        self._drag_y = event.position().y()
        self._offset -= delta / _ROLLER_ROW_HEIGHT
        self._clamp()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging."""
        self._drag_y = event.position().y()
        self._press_y = event.position().y()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Snap after a drag, or select the clicked row."""
        moved = abs(event.position().y() - self._press_y) > _CLICK_SLOP_PX
        self._drag_y = None
        if not moved:
            row = int(event.position().y() // _ROLLER_ROW_HEIGHT) - _ROLLER_VISIBLE_ROWS // 2
            self.set_current(self._normalize(round(self._offset) + row))
            return
        self.set_current(self._normalize(round(self._offset)))

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint rows around the highlighted middle row."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        middle = QRectF(
            SPACE_XS,
            (_ROLLER_VISIBLE_ROWS // 2) * _ROLLER_ROW_HEIGHT + 2,
            self.width() - 2 * SPACE_XS,
            _ROLLER_ROW_HEIGHT - 4,
        )
        paint_surface(painter, middle, palette.accent, None, RADIUS_CONTROL)
        painter.setFont(fluent_font(self.font(), TYPE_BODY))
        if not self._items:
            painter.end()
            return
        base = int(self._offset // 1)
        fraction = self._offset - base
        half = _ROLLER_VISIBLE_ROWS // 2
        for row in range(-half - 1, half + 2):
            index = base + row
            if not self._looping and not 0 <= index < len(self._items):
                continue
            text = self._items[index % len(self._items)]
            y = (row + half - fraction) * _ROLLER_ROW_HEIGHT
            rect = QRectF(0, y, self.width(), _ROLLER_ROW_HEIGHT)
            selected = abs(row - fraction) < 0.5  # noqa: PLR2004
            painter.setPen(palette.text_on_accent if selected else palette.text_primary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        painter.end()

    def set_current(self, index: int) -> None:
        """Select `index` with a snap animation."""
        if not self._items:
            return
        index = self._normalize(index)
        target = float(index)
        if self._looping:
            base = round(self._offset) - self._normalize(round(self._offset))
            target = base + index
        self._animation.stop()
        self._animation.setStartValue(self._offset)
        self._animation.setEndValue(target)
        self._animation.start()
        changed = index != self._current
        self._current = index
        if changed:
            self.current_changed.emit(index)

    def set_items(self, items: Sequence[str]) -> None:
        """Replace the values."""
        self._items = list(items)
        self._current = min(self._current, max(0, len(self._items) - 1))
        self._offset = float(self._current)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the fixed roller size."""
        return QSize(_ROLLER_WIDTH, _ROLLER_ROW_HEIGHT * _ROLLER_VISIBLE_ROWS)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Step one row per wheel notch."""
        step = -1 if event.angleDelta().y() > 0 else 1
        self.set_current(self._current + step)
        event.accept()

    def _clamp(self) -> None:
        if not self._looping:
            self._offset = max(0.0, min(float(len(self._items) - 1), self._offset))

    def _normalize(self, index: int) -> int:
        if not self._items:
            return 0
        if self._looping:
            return index % len(self._items)
        return max(0, min(len(self._items) - 1, index))

    def _on_animation(self, value: object) -> None:
        self._offset = float(value)  # ty: ignore[invalid-argument-type]
        self.update()


class FluentRollerPicker(FluentPushButton):
    """Button that opens a flyout of side-by-side rollers with Accept / Cancel."""

    accepted = Signal(list)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        columns: Sequence[Sequence[str]] = (),
        looping: bool = True,
        placeholder: str = "Select",
    ) -> None:
        """Create a roller picker with one roller per column."""
        super().__init__(placeholder, parent)
        self._placeholder = placeholder
        self._separator = " "
        self._popup = QFrame(
            self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self._popup.setObjectName("FluentRollerPopup")
        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        row = QHBoxLayout()
        row.setSpacing(0)
        self.rollers: list[FluentRoller] = []
        for column in columns:
            roller = FluentRoller(self._popup, items=column, looping=looping)
            self.rollers.append(roller)
            row.addWidget(roller)
        outer.addLayout(row)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
        accept = FluentPrimaryButton("OK", self._popup)
        cancel = FluentPushButton("Cancel", self._popup)
        accept.clicked.connect(self._accept)
        cancel.clicked.connect(self._popup.hide)
        buttons.addWidget(accept, 1)
        buttons.addWidget(cancel, 1)
        outer.addLayout(buttons)
        self.clicked.connect(self.open_popup)
        self._values: list[str] = []
        bind_theme(self._popup, self._recolor_popup)

    def format_values(self, values: list[str]) -> str:
        """Return the button caption for accepted values."""
        return self._separator.join(values)

    def open_popup(self) -> None:
        """Show the rollers centered under the button."""
        self._popup.adjustSize()
        x = self.width() // 2 - self._popup.width() // 2
        self._popup.move(self.mapToGlobal(QPoint(max(0, x), self.height() + SPACE_XS)))
        self._popup.show()

    def values(self) -> list[str]:
        """Return the accepted values (one per roller)."""
        return list(self._values)

    def _accept(self) -> None:
        self._values = [roller.current_text() for roller in self.rollers]
        self.setText(self.format_values(self._values))
        self._popup.hide()
        self.accepted.emit(self.values())

    def _recolor_popup(self) -> None:
        palette = palette_for(self)
        surface = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self._popup.setStyleSheet(
            f"QFrame#FluentRollerPopup {{ background: {css(surface)}; border: 1px solid {css(palette.popup_stroke)};"
            f" border-radius: {RADIUS_OVERLAY}px; }}\n{scroll_bar_qss(palette)}",
        )
