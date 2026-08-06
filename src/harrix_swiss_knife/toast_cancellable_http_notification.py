"""Toast notification for cancellable HTTP/HTTPS requests with elapsed time display."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QPushButton, QWidget

from harrix_swiss_knife import qt_modality, toast_countdown_notification, toast_notification_base

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent, QResizeEvent

_CLOSE_SYMBOL = "\u00d7"
_CANCEL_HINT = "Press Esc to stop the request"


class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification):
    """Toast with elapsed timer and user-initiated request cancellation.

    Shown as `WindowModal` so only the owner window hierarchy is blocked (sibling
    apps in the same process stay interactive). Prefer passing the active modal
    dialog as `parent` so Escape and the close button still work during flows
    like New Markdown → Fill with AI; `present()` focuses the toast.

    Attributes:

    - `cancel_requested` (`Signal`): Emitted once when the user cancels the request.
    - `completed` (`bool`): `True` after `mark_completed()` was called.

    """

    cancel_requested: Signal = Signal()

    def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        """Initialize cancellable HTTP toast with countdown and close control."""
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        # Must be set before show(); modality on an already-visible window is ignored.
        qt_modality.set_owner_window_modal(self)

        self._close_button = QPushButton(self)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setFlat(True)
        self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._close_button.setToolTip("Cancel request")
        self._close_button.clicked.connect(self._on_user_cancel)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_close_button()
        self._position_collapse_button()

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

    def present(self) -> None:
        """Show on top and take focus so Escape reaches this toast, not the parent dialog."""
        super().present()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._position_close_button()
        self._position_collapse_button()

    def reposition_action_buttons(self) -> None:
        """Place close and collapse buttons after a move or resize."""
        self._position_close_button()
        super().reposition_action_buttons()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition close and collapse buttons when the toast is resized."""
        super().resizeEvent(event)
        self._position_close_button()

    def _apply_close_button_icon(self, *, compact: bool) -> None:
        side = (
            toast_notification_base.COMPACT_ACTION_BUTTON_SIDE
            if compact
            else toast_notification_base.DEFAULT_ACTION_BUTTON_SIDE
        )
        self._close_button.setFixedSize(side, side)
        self._close_button.setIconSize(QSize(side, side))
        self._close_button.setIcon(toast_notification_base.make_action_icon(side, _CLOSE_SYMBOL))

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and close button."""
        super()._apply_compact_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(toast_notification_base.COMPACT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=True)
        self._position_close_button()
        self._position_collapse_button()
        self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and close button."""
        super()._apply_default_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._position_close_button()
        self._position_collapse_button()
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
        side = self._action_button_side()
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
        previous_size = self.size()
        self.adjustSize()
        self.reposition_action_buttons()
        if self.size() != previous_size:
            self.restack_group(pinned=self.is_pinned)

    def _trailing_controls_width(self) -> int:
        """Reserve space for the cancel button to the right of collapse."""
        if not hasattr(self, "_close_button"):
            return 0
        return self._action_button_side() + toast_notification_base.ACTION_BUTTON_GAP
