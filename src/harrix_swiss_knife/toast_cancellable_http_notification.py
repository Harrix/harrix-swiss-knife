"""Toast notification for cancellable HTTP/HTTPS requests with elapsed time display."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QWidget

from harrix_swiss_knife import toast_countdown_notification

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent

_CANCEL_HINT = "Press Esc or Cancel to stop the request"


class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification):
    """Toast with elapsed timer and user-initiated request cancellation.

    Attributes:

    - `cancel_requested` (`Signal`): Emitted once when the user cancels the request.
    - `completed` (`bool`): True after ``mark_completed()`` was called.

    """

    cancel_requested: Signal = Signal()

    def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        """Initialize cancellable HTTP toast with countdown and Cancel button."""
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        self._cancel_button = QPushButton("Cancel", self)
        self._cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_button.setStyleSheet(
            "background-color: rgba(80, 80, 80, 230);"
            "color: white;"
            "padding: 6px 14px;"
            "border-radius: 6px;"
            "font-size: 11pt;"
            "font-weight: bold;",
        )
        self._cancel_button.clicked.connect(self._on_user_cancel)

        layout = self.layout()
        if layout is not None:
            layout.addWidget(self._cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(8)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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

    def _emit_cancel_requested(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        self.cancel_requested.emit()

    def _on_user_cancel(self) -> None:
        """Handle Cancel button click or Escape key."""
        if self._completed or self._cancelled:
            return
        self._emit_cancel_requested()
        self.close()

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed seconds, and cancel hint."""
        self.label.setText(
            f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}\n{_CANCEL_HINT}",
        )
