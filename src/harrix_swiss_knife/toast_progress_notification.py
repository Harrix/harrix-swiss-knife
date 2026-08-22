"""Toast notification with elapsed time and a determinate progress bar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from harrix_swiss_knife import toast_countdown_notification, toast_notification_base

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent, QKeyEvent, QResizeEvent

_CLOSE_SYMBOL = "\u00d7"
_CANCEL_HINT = "Press Esc to cancel"


class ToastProgressNotification(toast_countdown_notification.ToastCountdownNotification):
    """Countdown toast that also shows `done / total` progress.

    Attributes:

    - `done` (`int`): Completed work units.
    - `total` (`int`): Total work units (0 means unknown / indeterminate).
    - `progress_bar` (`QProgressBar`): Determinate progress indicator under the label.
    - `cancel_requested` (`Signal`): Emitted once when a cancellable toast is cancelled.

    """

    cancel_requested = Signal()

    def __init__(
        self,
        message: str = "Process is running…",
        *,
        total: int = 0,
        parent: QWidget | None = None,
        cancellable: bool = False,
    ) -> None:
        """Initialize progress toast with countdown and progress bar."""
        self._done = 0
        self._total = max(0, total)
        self._cancellable = cancellable
        self._cancelled = False
        self._completed = False
        self._detail = ""
        super().__init__(message, parent)

        self._progress_container = QWidget(self)
        self._progress_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.progress_bar = QProgressBar(self._progress_container)
        self.progress_bar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setMinimumWidth(220)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label = QLabel(self._progress_container)
        self.detail_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.detail_label.hide()

        container_layout = QVBoxLayout(self._progress_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.progress_bar)
        container_layout.addWidget(self.detail_label)

        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.setSpacing(0)
            layout.addWidget(self._progress_container)

        if cancellable:
            self._close_button = QPushButton(self)
            self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self._close_button.setFlat(True)
            self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
            self._apply_close_button_icon(compact=False)
            self._close_button.setToolTip("Cancel")
            self._close_button.clicked.connect(self._on_user_cancel)
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self._position_close_button()

        self._apply_progress_style(compact=False)
        self.set_progress(0, self._total)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Emit cancel when the user closes a still-running cancellable toast."""
        if self._cancellable and not self._completed and not self._cancelled:
            self._emit_cancel_requested()
        super().closeEvent(event)

    @property
    def done(self) -> int:
        """Number of completed work units."""
        return self._done

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel a cancellable toast when the user presses Escape."""
        if self._cancellable and event.key() == Qt.Key.Key_Escape:
            self._on_user_cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def mark_completed(self) -> None:
        """Mark the job as finished so closing the toast does not emit cancel."""
        self._completed = True

    def reposition_action_buttons(self) -> None:
        """Place close and collapse buttons after a move or resize."""
        self._position_close_button()
        super().reposition_action_buttons()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition close and collapse buttons when the toast is resized."""
        super().resizeEvent(event)
        self._position_close_button()

    def set_detail(self, text: str) -> None:
        """Set the status line under the progress bar.

        Args:

        - `text` (`str`): Current operation, for example a habit name. Empty hides the line.

        """
        self._detail = str(text or "").strip()
        self._refresh_detail_label()
        previous_size = self.size()
        self.adjustSize()
        self.reposition_action_buttons()
        if self.size() != previous_size:
            self.restack_group(pinned=self.is_pinned)

    def set_progress(self, done: int, total: int | None = None) -> None:
        """Update progress values and refresh the progress bar.

        Args:

        - `done` (`int`): Completed work units.
        - `total` (`int | None`): Optional new total. When `None`, keep the current total.

        """
        if total is not None:
            self._total = max(0, total)
        if self._total <= 0:
            self._done = max(0, done)
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setValue(0)
        else:
            self._done = max(0, min(done, self._total))
            self.progress_bar.setRange(0, self._total)
            self.progress_bar.setValue(self._done)
        self._refresh_label_text()

    @property
    def total(self) -> int:
        """Total number of work units."""
        return self._total

    def _apply_close_button_icon(self, *, compact: bool) -> None:
        if not hasattr(self, "_close_button"):
            return
        side = (
            toast_notification_base.COMPACT_ACTION_BUTTON_SIDE
            if compact
            else toast_notification_base.DEFAULT_ACTION_BUTTON_SIDE
        )
        self._close_button.setFixedSize(side, side)
        self._close_button.setIconSize(QSize(side, side))
        self._close_button.setIcon(toast_notification_base.make_action_icon(side, _CLOSE_SYMBOL))

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and progress bar."""
        super()._apply_compact_style()
        self._apply_progress_style(compact=True)
        if hasattr(self, "_close_button"):
            self._close_button.setStyleSheet(toast_notification_base.COMPACT_ACTION_BUTTON_STYLE)
            self._apply_close_button_icon(compact=True)
            self._position_close_button()
        if hasattr(self, "progress_bar"):
            self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and progress bar."""
        super()._apply_default_style()
        self._apply_progress_style(compact=False)
        if hasattr(self, "_close_button"):
            self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
            self._apply_close_button_icon(compact=False)
            self._position_close_button()
        if hasattr(self, "progress_bar"):
            self._refresh_label_text()

    def _apply_progress_style(self, *, compact: bool) -> None:
        """Style the progress chrome: rounded track with vertically centered text."""
        if not hasattr(self, "progress_bar") or not hasattr(self, "_progress_container"):
            return

        if compact:
            radius = 8
            bar_radius = 5
            bar_height = 16
            h_pad = 12
            top_pad = 2
            bottom_pad = 8
            font_size = "9pt"
            detail_font = "8pt"
            label_padding = "8px 12px 4px 12px"
        else:
            radius = 10
            bar_radius = 6
            bar_height = 22
            h_pad = 20
            top_pad = 4
            bottom_pad = 14
            font_size = "11pt"
            detail_font = "10pt"
            label_padding = "15px 20px 6px 20px"

        self._progress_container.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "border-top-left-radius: 0px;"
            "border-top-right-radius: 0px;"
            f"border-bottom-left-radius: {radius}px;"
            f"border-bottom-right-radius: {radius}px;",
        )
        container_layout = self._progress_container.layout()
        if isinstance(container_layout, QVBoxLayout):
            container_layout.setContentsMargins(h_pad, top_pad, h_pad, bottom_pad)
            container_layout.setAlignment(self.progress_bar, Qt.AlignmentFlag.AlignVCenter)

        self.progress_bar.setFixedHeight(bar_height)
        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "background-color: rgba(70, 70, 70, 255);"
            "color: white;"
            "border: none;"
            f"border-radius: {bar_radius}px;"
            "padding: 0px;"
            "margin: 0px;"
            "text-align: center;"
            f"font-size: {font_size};"
            "font-weight: bold;"
            "}"
            "QProgressBar::chunk {"
            "background-color: rgba(90, 170, 255, 220);"
            f"border-radius: {bar_radius}px;"
            "margin: 0px;"
            "}",
        )
        if hasattr(self, "detail_label"):
            self.detail_label.setStyleSheet(
                "background-color: transparent;"
                "color: rgba(220, 220, 220, 255);"
                f"font-size: {detail_font};"
                "font-weight: normal;"
                "padding: 4px 0px 0px 0px;"
                "border: none;",
            )
            self._refresh_detail_label()
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            f"padding: {label_padding};"
            f"border-top-left-radius: {radius}px;"
            f"border-top-right-radius: {radius}px;"
            "border-bottom-left-radius: 0px;"
            "border-bottom-right-radius: 0px;"
            f"font-size: {'10pt' if compact else '16pt'};"
            "font-weight: bold;",
        )

    def _emit_cancel_requested(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        self.cancel_requested.emit()

    def _on_user_cancel(self) -> None:
        if not self._cancellable or self._completed or self._cancelled:
            return
        self._emit_cancel_requested()
        self.close()

    def _position_close_button(self) -> None:
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

    def _refresh_detail_label(self) -> None:
        """Show or hide the status line under the progress bar."""
        if not hasattr(self, "detail_label"):
            return
        if self._detail:
            self.detail_label.setText(self._detail)
            self.detail_label.show()
        else:
            self.detail_label.clear()
            self.detail_label.hide()

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed time, and progress summary."""
        if not hasattr(self, "progress_bar"):
            return
        elapsed = toast_countdown_notification.format_elapsed_clock(getattr(self, "elapsed_seconds", 0))
        show_hint = self._cancellable and not self._is_pinned
        if self._is_pinned:
            progress = f"{self._done}/{self._total}" if self._total > 0 else str(self._done)
            body = f"{self.message}\n{elapsed} · {progress}"
        elif self._total > 0:
            body = f"{self.message}\nTime elapsed: {elapsed}\nProgress: {self._done} / {self._total}"
        else:
            body = f"{self.message}\nTime elapsed: {elapsed}"
        if show_hint:
            self.label.setTextFormat(Qt.TextFormat.RichText)
            self.label.setText(
                toast_notification_base.format_toast_cancel_hint_html(
                    body,
                    _CANCEL_HINT,
                    compact=self._is_pinned,
                ),
            )
        else:
            self.label.setTextFormat(Qt.TextFormat.PlainText)
            self.label.setText(body)
        previous_size = self.size()
        self.adjustSize()
        self.reposition_action_buttons()
        if self.size() != previous_size:
            self.restack_group(pinned=self.is_pinned)

    def _trailing_controls_width(self) -> int:
        if not hasattr(self, "_close_button"):
            return 0
        return self._action_button_side() + toast_notification_base.ACTION_BUTTON_GAP
