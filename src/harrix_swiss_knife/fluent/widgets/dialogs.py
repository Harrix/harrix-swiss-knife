"""Fluent dialogs: in-window content dialog, dialog, message / input / color dialogs, popconfirm, wizard."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPoint, QPointF, QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QConicalGradient, QLinearGradient, QPainter, QRadialGradient
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.paint import antialiased_painter, paint_surface
from harrix_swiss_knife.fluent.theme import bind_theme, css, palette_for
from harrix_swiss_knife.fluent.tokens import (
    ANIMATION_NORMAL,
    RADIUS_CONTROL,
    RADIUS_OVERLAY,
    SPACE_L,
    SPACE_M,
    SPACE_S,
    SPACE_XL,
    SPACE_XS,
)
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentPrimaryButton
from harrix_swiss_knife.fluent.widgets.display import FluentSteps
from harrix_swiss_knife.fluent.widgets.enums import TextRole, TextStyle
from harrix_swiss_knife.fluent.widgets.input_base import FluentLineEdit
from harrix_swiss_knife.fluent.widgets.text_base import FluentText

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtGui import QMouseEvent, QPaintEvent
from harrix_swiss_knife.fluent.widgets.dialog_base import FluentDialog, FluentDialogBody

_DIALOG_MIN_WIDTH = 320
_DIALOG_MAX_WIDTH = 548
_HUE_RING_WIDTH = 18
_HEX_LENGTH = 7


class FluentColorDialog(FluentDialog):
    """Color picker: wheel, brightness slider, preview swatch, and hex input."""

    color_changed = Signal(QColor)

    def __init__(
        self, color: QColor | None = None, parent: QWidget | None = None, *, title: str = "Choose color"
    ) -> None:
        """Create a color dialog."""
        super().__init__(title, "", parent)
        self._color = QColor(color) if color is not None and color.isValid() else QColor("#005fb8")
        row = QHBoxLayout()
        row.setSpacing(SPACE_L)
        self._wheel = _HueRing(self)
        row.addWidget(self._wheel)
        side = QVBoxLayout()
        side.setSpacing(SPACE_S)
        self._swatch = QFrame(self)
        self._swatch.setFixedSize(96, 64)
        side.addWidget(self._swatch)
        self._hex = FluentLineEdit(self, clearable=False)
        self._hex.setMaxLength(_HEX_LENGTH)
        side.addWidget(self._hex)
        side.addStretch(1)
        row.addLayout(side)
        self.content_layout.addLayout(row)
        self._slider = _ValueSlider(self)
        self.content_layout.addWidget(self._slider)
        self._wheel.color_picked.connect(self._on_wheel)
        self._slider.value_changed.connect(self._on_value)
        self._hex.editingFinished.connect(self._on_hex)
        self._apply(self._color)

    def color(self) -> QColor:
        """Return the chosen color."""
        return QColor(self._color)

    @staticmethod
    def get_color(color: QColor | None = None, parent: QWidget | None = None) -> QColor | None:
        """Show the dialog and return the color, or `None` when cancelled."""
        dialog = FluentColorDialog(color, parent)
        return dialog.color() if dialog.exec() == QDialog.DialogCode.Accepted else None

    def _apply(self, color: QColor) -> None:
        self._color = QColor(color)
        self._wheel.set_color(color)
        self._slider.set_color(color)
        self._hex.setText(color.name())
        self._swatch.setStyleSheet(
            f"QFrame {{ background: {color.name()}; border-radius: {RADIUS_CONTROL}px;"
            " border: 1px solid rgba(0, 0, 0, 30); }",
        )
        self.color_changed.emit(self.color())

    def _on_hex(self) -> None:
        color = QColor(self._hex.text().strip())
        if color.isValid():
            self._apply(color)

    def _on_value(self, value: float) -> None:
        self._apply(QColor.fromHsvF(max(0.0, self._color.hsvHueF()), self._color.hsvSaturationF(), value))

    def _on_wheel(self, color: QColor) -> None:
        self._apply(QColor.fromHsvF(max(0.0, color.hsvHueF()), color.hsvSaturationF(), self._color.valueF() or 1.0))


class FluentContentDialog(QWidget):
    """In-window modal: dims the host window with a smoke layer and shows a dialog card.

    Unlike `FluentDialog` it has no OS frame, which matches WinUI `ContentDialog`
    and PyQt-Fluent-Widgets `MessageBox`.

    """

    accepted = Signal()
    rejected = Signal()
    finished = Signal(bool)

    def __init__(
        self,
        title: str,
        content: str,
        host: QWidget,
        *,
        primary_text: str = "OK",
        secondary_text: str = "Cancel",
    ) -> None:
        """Create a content dialog over `host` (call `open()` to show it)."""
        window = host.window()
        super().__init__(window)
        self._host = window
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.card = QFrame(self)
        self.card.setObjectName("FluentContentDialogCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        self._body = FluentDialogBody(title, content, self.card)
        card_layout.addWidget(self._body)
        self.content_layout = self._body.content_layout
        self.primary_button = self._body.primary
        self.secondary_button = self._body.secondary
        self.primary_button.setText(primary_text)
        self.secondary_button.setText(secondary_text)
        self.secondary_button.setVisible(bool(secondary_text))
        self.primary_button.clicked.connect(self.accept)
        self.secondary_button.clicked.connect(self.reject)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.card.setGraphicsEffect(shadow)
        self._opacity = QGraphicsOpacityEffect(self)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(ANIMATION_NORMAL)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.refresh_theme)

    def accept(self) -> None:
        """Close the dialog and emit `accepted`."""
        self._finish(accepted=True)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Follow host window resizes."""
        if watched is self._host and event.type() == QEvent.Type.Resize:
            self._sync_geometry()
        return False

    def open(self) -> None:
        """Show the dialog over the host window."""
        self._sync_geometry()
        self.setGraphicsEffect(self._opacity)
        self._opacity.setOpacity(0.0)
        self.show()
        self.raise_()
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.start()
        self.primary_button.setFocus()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the smoke layer."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), palette_for(self).smoke)
        painter.end()

    def refresh_theme(self) -> None:
        """Re-color the card."""
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self.card.setStyleSheet(
            f"QFrame#FluentContentDialogCard {{ background: {css(fill)};"
            f" border: 1px solid {css(palette.popup_stroke)}; border-radius: {RADIUS_OVERLAY}px; }}",
        )
        self.update()

    def reject(self) -> None:
        """Close the dialog and emit `rejected`."""
        self._finish(accepted=False)

    def _finish(self, *, accepted: bool) -> None:
        self._host.removeEventFilter(self)
        (self.accepted if accepted else self.rejected).emit()
        self.finished.emit(accepted)
        self.close()

    def _sync_geometry(self) -> None:
        self.setGeometry(self._host.rect())
        width = max(_DIALOG_MIN_WIDTH, min(_DIALOG_MAX_WIDTH, self.width() - 2 * SPACE_XL))
        self.card.setFixedWidth(width)
        self.card.adjustSize()
        self.card.move((self.width() - self.card.width()) // 2, (self.height() - self.card.height()) // 2)


class FluentInputDialog(FluentDialog):
    """Dialog that asks for one line of text."""

    def __init__(
        self, title: str, label: str = "", parent: QWidget | None = None, *, text: str = "", placeholder: str = ""
    ) -> None:
        """Create an input dialog."""
        super().__init__(title, label, parent)
        self.line_edit = FluentLineEdit(self, placeholder=placeholder)
        self.line_edit.setText(text)
        self.content_layout.addWidget(self.line_edit)
        self.line_edit.returnPressed.connect(self.accept)

    @staticmethod
    def get_text(parent: QWidget | None, title: str, label: str = "", *, text: str = "") -> tuple[str, bool]:
        """Show the dialog and return `(text, accepted)`."""
        dialog = FluentInputDialog(title, label, parent, text=text)
        dialog.line_edit.setFocus()
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.line_edit.text(), accepted

    def text(self) -> str:
        """Return the entered text."""
        return self.line_edit.text()


class FluentMessageDialog(FluentDialog):
    """Information / question dialog with only text and one or two buttons."""

    @staticmethod
    def ask(parent: QWidget | None, title: str, text: str, *, yes: str = "Yes", no: str = "No") -> bool:
        """Show a question and return whether the primary button was pressed."""
        dialog = FluentMessageDialog(title, text, parent, primary_text=yes, secondary_text=no)
        return dialog.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def inform(parent: QWidget | None, title: str, text: str) -> None:
        """Show information with a single OK button."""
        FluentMessageDialog(title, text, parent, primary_text="OK", secondary_text="").exec()


class FluentPopconfirm(QFrame):
    """Small confirmation flyout next to a button ("Delete this item?" Yes / No)."""

    confirmed = Signal()
    cancelled = Signal()

    def __init__(
        self, text: str, anchor: QWidget, *, title: str = "", confirm_text: str = "Yes", cancel_text: str = "No"
    ) -> None:
        """Create a popconfirm for `anchor` (call `popup()` to show)."""
        super().__init__(
            anchor, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self._anchor = anchor
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_M)
        layout.setSpacing(SPACE_S)
        if title:
            layout.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG))
        layout.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        row = QHBoxLayout()
        row.addStretch(1)
        cancel = FluentPushButton(cancel_text, self)
        confirm = FluentPrimaryButton(confirm_text, self)
        cancel.clicked.connect(self._cancel)
        confirm.clicked.connect(self._confirm)
        row.addWidget(cancel)
        row.addWidget(confirm)
        layout.addLayout(row)
        self.setMaximumWidth(320)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the flyout surface."""
        palette = palette_for(self._anchor)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_OVERLAY)
        painter.end()

    def popup(self) -> None:
        """Show above the anchor (or below when there is no room)."""
        self.adjustSize()
        top_left = self._anchor.mapToGlobal(QPoint(0, 0))
        y = top_left.y() - self.height() - SPACE_XS
        if y < 0:
            y = top_left.y() + self._anchor.height() + SPACE_XS
        self.move(top_left.x(), y)
        self.show()

    def _cancel(self) -> None:
        self.close()
        self.cancelled.emit()

    def _confirm(self) -> None:
        self.close()
        self.confirmed.emit()


class FluentWizard(FluentDialog):
    """Multi-page dialog with a step indicator and Back / Next / Finish buttons."""

    page_changed = Signal(int)

    def __init__(self, title: str, parent: QWidget | None = None, *, steps: Sequence[str] = ()) -> None:
        """Create a wizard; add pages in the same order as `steps`."""
        super().__init__(title, "", parent, primary_text="Next", secondary_text="Back")
        self.setMinimumSize(560, 420)
        self.steps = FluentSteps(self, steps=steps)
        self.pages = QStackedWidget(self)
        self.content_layout.addWidget(self.steps)
        self.content_layout.addWidget(self.pages, 1)
        self.primary_button.clicked.disconnect()
        self.secondary_button.clicked.disconnect()
        self.primary_button.clicked.connect(self.next_page)
        self.secondary_button.clicked.connect(self.previous_page)
        self._sync_buttons()

    def add_page(self, widget: QWidget) -> int:
        """Append a page and return its index."""
        index = self.pages.addWidget(widget)
        self._sync_buttons()
        return index

    def current_index(self) -> int:
        """Return the current page index."""
        return self.pages.currentIndex()

    def next_page(self) -> None:
        """Advance, or accept on the last page."""
        index = self.pages.currentIndex()
        if index >= self.pages.count() - 1:
            self.steps.set_current(self.pages.count())
            self.accept()
            return
        self._go(index + 1)

    def previous_page(self) -> None:
        """Go back one page."""
        self._go(self.pages.currentIndex() - 1)

    def _go(self, index: int) -> None:
        if not 0 <= index < self.pages.count():
            return
        self.pages.setCurrentIndex(index)
        self.steps.set_current(index)
        self._sync_buttons()
        self.page_changed.emit(index)

    def _sync_buttons(self) -> None:
        index = self.pages.currentIndex()
        self.secondary_button.setEnabled(index > 0)
        last = index >= self.pages.count() - 1
        self.primary_button.setText("Finish" if last else "Next")


class _HueRing(QWidget):
    """Color wheel: hue around the ring, saturation from the center."""

    color_picked = Signal(QColor)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._color = QColor.fromHsv(210, 255, 255)
        self.setFixedSize(220, 220)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def color(self) -> QColor:
        return QColor(self._color)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._pick(event.position())

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pick(event.position())

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = antialiased_painter(self)
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        center = rect.center()
        hue = QConicalGradient(center, 0)
        for step in range(7):
            hue.setColorAt(step / 6, QColor.fromHsv((360 - step * 60) % 360, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(hue)
        painter.drawEllipse(rect)
        white = QRadialGradient(center, rect.width() / 2)
        white.setColorAt(0, QColor(255, 255, 255, 255))
        white.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(white)
        painter.drawEllipse(rect)
        angle = math.radians(max(self._color.hsvHue(), 0))
        radius = self._color.hsvSaturationF() * rect.width() / 2
        marker = QPointF(center.x() + math.cos(angle) * radius, center.y() - math.sin(angle) * radius)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(marker, 7, 7)
        painter.setPen(QColor(0, 0, 0, 120))
        painter.drawEllipse(marker, 8, 8)
        painter.end()

    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    def _pick(self, position: QPointF) -> None:
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        dx = position.x() - rect.center().x()
        dy = rect.center().y() - position.y()
        saturation = min(1.0, math.hypot(dx, dy) / (rect.width() / 2))
        hue = (math.degrees(math.atan2(dy, dx)) + 360) % 360
        self._color = QColor.fromHsvF(hue / 360, saturation, self._color.valueF() or 1.0)
        self.update()
        self.color_picked.emit(self.color())


class _ValueSlider(QWidget):
    """Horizontal brightness slider for the current hue and saturation."""

    value_changed = Signal(float)

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._color = QColor.fromHsv(210, 255, 255)
        self.setFixedHeight(20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._pick(event.position().x())

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._pick(event.position().x())

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = antialiased_painter(self)
        rect = QRectF(self.rect()).adjusted(10, 4, -10, -4)
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0, QColor(0, 0, 0))
        gradient.setColorAt(1, QColor.fromHsvF(max(0.0, self._color.hsvHueF()), self._color.hsvSaturationF(), 1.0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)
        x = rect.left() + rect.width() * self._color.valueF()
        paint_surface(painter, QRectF(x - 8, 2, 16, 16), QColor(255, 255, 255), QColor(0, 0, 0, 90), 8)
        painter.end()

    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    def _pick(self, x: float) -> None:
        width = max(1, self.width() - 20)
        value = max(0.0, min(1.0, (x - 10) / width))
        self._color = QColor.fromHsvF(max(0.0, self._color.hsvHueF()), self._color.hsvSaturationF(), value)
        self.update()
        self.value_changed.emit(value)
