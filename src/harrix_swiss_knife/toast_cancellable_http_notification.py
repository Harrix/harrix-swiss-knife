"""Toast notification for cancellable HTTP/HTTPS requests with elapsed time display."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QPushButton, QWidget

from harrix_swiss_knife import toast_countdown_notification

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent, QResizeEvent

_CLOSE_SYMBOL = "\u00d7"

_CANCEL_HINT = "Press Esc to stop the request"

_DEFAULT_CLOSE_BUTTON_SIDE = 24
_COMPACT_CLOSE_BUTTON_SIDE = 18

_DEFAULT_CLOSE_BUTTON_STYLE = (
    "QPushButton {"
    "background-color: transparent;"
    "border: none;"
    "padding: 0px;"
    "margin: 0px;"
    "}"
    "QPushButton:hover {"
    "background-color: rgba(255, 255, 255, 40);"
    "border-radius: 4px;"
    "}"
)

_COMPACT_CLOSE_BUTTON_STYLE = (
    "QPushButton {"
    "background-color: transparent;"
    "border: none;"
    "padding: 0px;"
    "margin: 0px;"
    "}"
    "QPushButton:hover {"
    "background-color: rgba(255, 255, 255, 40);"
    "border-radius: 3px;"
    "}"
)


class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification):
    """Toast with elapsed timer and user-initiated request cancellation.

    Attributes:

    - `cancel_requested` (`Signal`): Emitted once when the user cancels the request.
    - `completed` (`bool`): True after `mark_completed()` was called.

    """

    cancel_requested: Signal = Signal()

    def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        """Initialize cancellable HTTP toast with countdown and close control."""
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        self._close_button = QPushButton(self)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setFlat(True)
        self._close_button.setStyleSheet(_DEFAULT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._close_button.setToolTip("Cancel request")
        self._close_button.clicked.connect(self._on_user_cancel)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_close_button()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop timer and emit cancel when closed by the user before completion."""
        if not self._completed and not self._cancelled:
            self._emit_cancel_requested()
        self.timer.stop()
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel the request when the user presses Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self._on_user_cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def mark_completed(self) -> None:
        """Mark the request as finished so closing the toast does not emit cancel."""
        self._completed = True

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition the close button when the toast is resized."""
        super().resizeEvent(event)
        self._position_close_button()

    def _apply_close_button_icon(self, *, compact: bool) -> None:
        side = _COMPACT_CLOSE_BUTTON_SIDE if compact else _DEFAULT_CLOSE_BUTTON_SIDE
        self._close_button.setFixedSize(side, side)
        self._close_button.setIconSize(QSize(side, side))
        self._close_button.setIcon(_make_close_icon(side))

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and close button."""
        super()._apply_compact_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(_COMPACT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=True)
        self._position_close_button()
        self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and close button."""
        super()._apply_default_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(_DEFAULT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._position_close_button()
        self._refresh_label_text()

    def _emit_cancel_requested(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        self.cancel_requested.emit()

    def _on_user_cancel(self) -> None:
        """Handle close button click or Escape key."""
        if self._completed or self._cancelled:
            return
        self._emit_cancel_requested()
        self.close()

    def _position_close_button(self) -> None:
        """Place the close button at the top-right corner of the message label."""
        if not hasattr(self, "_close_button"):
            return
        label_geom = self.label.geometry()
        side = _COMPACT_CLOSE_BUTTON_SIDE if self._is_pinned else _DEFAULT_CLOSE_BUTTON_SIDE
        margin = 2 if self._is_pinned else 4
        self._close_button.move(
            label_geom.x() + label_geom.width() - side - margin,
            label_geom.y() + margin,
        )
        self._close_button.raise_()

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed seconds, and cancel hint."""
        if self._is_pinned:
            self.label.setText(f"{self.message}\n{self.elapsed_seconds}s")
        else:
            self.label.setText(
                f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}\n{_CANCEL_HINT}",
            )
        self.adjustSize()
        self._position_close_button()
        if self._is_pinned:
            self._move_to_bottom_right_corner()


def _make_close_icon(side: int) -> QIcon:
    """Render a centered close symbol for the given button side length."""
    pixmap = QPixmap(side, side)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = painter.font()
    font.setPixelSize(max(10, int(side * 0.72)))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, _CLOSE_SYMBOL)
    painter.end()
    return QIcon(pixmap)
