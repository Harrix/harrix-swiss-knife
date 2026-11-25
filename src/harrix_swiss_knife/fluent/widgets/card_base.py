"""Painted card surfaces that the Fluent card widgets build on."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface, with_alpha
from harrix_swiss_knife.fluent.theme import bind_theme, palette_for
from harrix_swiss_knife.fluent.tokens import (
    RADIUS_CARD,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import (
        QColor,
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
        self._caution_tint = False
        self._danger_tint = False
        self._success_tint = False
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card surface."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill, stroke = self._tint_surface_colors(palette)
        paint_surface(painter, self.rect(), fill, stroke, RADIUS_CARD)
        painter.end()

    def set_caution_tint(self, *, enabled: bool) -> None:
        """Use the caution surface colors (soft amber) when `enabled` is true."""
        if self._caution_tint == enabled and (not enabled or not (self._danger_tint or self._success_tint)):
            return
        self._caution_tint = enabled
        if enabled:
            self._danger_tint = False
            self._success_tint = False
        self.update()

    def set_danger_tint(self, *, enabled: bool) -> None:
        """Use the critical surface colors (soft red) when `enabled` is true."""
        if self._danger_tint == enabled and (not enabled or not (self._caution_tint or self._success_tint)):
            return
        self._danger_tint = enabled
        if enabled:
            self._caution_tint = False
            self._success_tint = False
        self.update()

    def set_success_tint(self, *, enabled: bool) -> None:
        """Use the success surface colors (soft green) when `enabled` is true."""
        if self._success_tint == enabled and (not enabled or not (self._caution_tint or self._danger_tint)):
            return
        self._success_tint = enabled
        if enabled:
            self._caution_tint = False
            self._danger_tint = False
        self.update()

    def _tint_surface_colors(self, palette: FluentPalette) -> tuple[QColor, QColor]:
        """Return `(fill, stroke)` for the active tint, or card defaults."""
        if self._success_tint:
            return palette.success_bg, with_alpha(palette.success, 140)
        if self._danger_tint:
            return palette.critical_bg, with_alpha(palette.critical, 140)
        if self._caution_tint:
            return palette.caution_bg, with_alpha(palette.caution, 140)
        return palette.card_bg, palette.card_stroke


class FluentInteractiveCard(FluentCard):
    """Clickable card with hover/pressed fills, keyboard activation, and menu signals."""

    clicked = Signal()
    context_menu_requested = Signal(QPoint)
    shortcut_menu_requested = Signal(QPoint)

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
        """Show the pressed fill; middle/right-click ask for identity / shortcut menus."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.context_menu_requested.emit(event.globalPosition().toPoint())
            event.accept()
            return
        elif event.button() == Qt.MouseButton.RightButton:
            self.shortcut_menu_requested.emit(event.globalPosition().toPoint())
            event.accept()
            return
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
        tinted = self._caution_tint or self._danger_tint or self._success_tint
        if tinted:
            fill, stroke = self._tint_surface_colors(palette)
            if self._selected:
                stroke = palette.accent
        else:
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
