"""Painted card surfaces that the Fluent card widgets build on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.theme import bind_theme, palette_for
from harrix_swiss_knife.fluent.tokens import (
    RADIUS_CARD,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import (
        QContextMenuEvent,
        QEnterEvent,
        QFocusEvent,
        QKeyEvent,
        QMouseEvent,
        QPainter,
        QPaintEvent,
    )

    from harrix_swiss_knife.fluent.tokens import FluentPalette


class FluentCard(QWidget):
    """Static card surface (`card_bg` + `card_stroke`, 8 px corners) for any content."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty card; add content through `layout()` or your own layout."""
        super().__init__(parent)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card surface."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()


class FluentInteractiveCard(FluentCard):
    """Clickable card with hover/pressed fills, keyboard activation, and a context menu signal."""

    clicked = Signal()
    context_menu_requested = Signal(QPoint)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a clickable card."""
        self._hovered = False
        self._pressed = False
        self._selected = False
        self._focus_reason = Qt.FocusReason.OtherFocusReason
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        """Emit `context_menu_requested` with the global cursor position."""
        self.context_menu_requested.emit(event.globalPos())
        event.accept()

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Show the hover fill."""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Remember why focus arrived (keyboard focus draws the ring)."""
        self._focus_reason = event.reason()
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Hide the focus ring."""
        self.update()
        super().focusOutEvent(event)

    def is_selected(self) -> bool:
        """Return whether the card shows the selected (accent) state."""
        return self._selected

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Activate on Enter or Space."""
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space}:
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Drop the hover fill."""
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Show the pressed fill."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit `clicked` when released inside the card."""
        was_pressed = self._pressed
        self._pressed = False
        self.update()
        if (
            event.button() == Qt.MouseButton.LeftButton
            and was_pressed
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card with hover, pressed, selected, and focus states."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        painter.end()

    def paint_background(self, painter: QPainter, palette: FluentPalette) -> None:
        """Paint the state-dependent card surface (subclasses paint content on top)."""
        fill = palette.card_bg
        if self._pressed:
            fill = palette.card_bg_pressed
        elif self._hovered:
            fill = palette.card_bg_hover
        stroke = palette.accent if self._selected else palette.card_stroke
        paint_surface(painter, self.rect(), fill, stroke, RADIUS_CARD)
        if self.hasFocus() and self.focusPolicy() != Qt.FocusPolicy.NoFocus and self._focus_visible():
            paint_surface(painter, self.rect(), None, palette.focus_stroke_outer, RADIUS_CARD, stroke_width=2)

    def set_selected(self, *, selected: bool) -> None:
        """Show or hide the selected (accent border) state."""
        self._selected = selected
        self.update()

    def _focus_visible(self) -> bool:
        return self._focus_reason in {Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason}
