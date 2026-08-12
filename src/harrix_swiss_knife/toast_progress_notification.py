"""Toast notification with elapsed time and a determinate progress bar."""

from __future__ import annotations

from PySide6.QtWidgets import QProgressBar, QVBoxLayout, QWidget

from harrix_swiss_knife import toast_countdown_notification


class ToastProgressNotification(toast_countdown_notification.ToastCountdownNotification):
    """Countdown toast that also shows `done / total` progress.

    Attributes:

    - `done` (`int`): Completed work units.
    - `total` (`int`): Total work units (0 means unknown / indeterminate).
    - `progress_bar` (`QProgressBar`): Determinate progress indicator under the label.

    """

    def __init__(
        self,
        message: str = "Process is running…",
        *,
        total: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize progress toast with countdown and progress bar."""
        self._done = 0
        self._total = max(0, total)
        super().__init__(message, parent)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setMinimumWidth(220)
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.addWidget(self.progress_bar)

        self._apply_progress_style(compact=False)
        self.set_progress(0, self._total)

    @property
    def done(self) -> int:
        """Number of completed work units."""
        return self._done

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

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and progress bar."""
        super()._apply_compact_style()
        self._apply_progress_style(compact=True)
        if hasattr(self, "progress_bar"):
            self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and progress bar."""
        super()._apply_default_style()
        self._apply_progress_style(compact=False)
        if hasattr(self, "progress_bar"):
            self._refresh_label_text()

    def _apply_progress_style(self, *, compact: bool) -> None:
        """Style the progress bar to continue the toast chrome."""
        if not hasattr(self, "progress_bar"):
            return
        if compact:
            self.progress_bar.setStyleSheet(
                "QProgressBar {"
                "background-color: rgba(40, 40, 40, 230);"
                "color: white;"
                "border: none;"
                "border-radius: 0px 0px 8px 8px;"
                "padding: 2px 12px 8px 12px;"
                "text-align: center;"
                "font-size: 9pt;"
                "font-weight: bold;"
                "min-height: 10px;"
                "max-height: 18px;"
                "}"
                "QProgressBar::chunk {"
                "background-color: rgba(90, 170, 255, 220);"
                "border-radius: 3px;"
                "}",
            )
            self.label.setStyleSheet(
                "background-color: rgba(40, 40, 40, 230);"
                "color: white;"
                "padding: 8px 12px 4px 12px;"
                "border-radius: 8px 8px 0px 0px;"
                "font-size: 10pt;"
                "font-weight: bold;",
            )
            return

        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "border: none;"
            "border-radius: 0px 0px 10px 10px;"
            "padding: 4px 20px 14px 20px;"
            "text-align: center;"
            "font-size: 11pt;"
            "font-weight: bold;"
            "min-height: 14px;"
            "max-height: 24px;"
            "}"
            "QProgressBar::chunk {"
            "background-color: rgba(90, 170, 255, 220);"
            "border-radius: 4px;"
            "}",
        )
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 15px 20px 6px 20px;"
            "border-radius: 10px 10px 0px 0px;"
            "font-size: 16pt;"
            "font-weight: bold;",
        )

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed time, and progress summary."""
        if not hasattr(self, "progress_bar"):
            return
        elapsed = getattr(self, "elapsed_seconds", 0)
        if self._is_pinned:
            progress = f"{self._done}/{self._total}" if self._total > 0 else str(self._done)
            self.label.setText(f"{self.message}\n{elapsed}s · {progress}")
        elif self._total > 0:
            self.label.setText(
                f"{self.message}\nSeconds elapsed: {elapsed}\nProgress: {self._done} / {self._total}",
            )
        else:
            self.label.setText(f"{self.message}\nSeconds elapsed: {elapsed}")
        previous_size = self.size()
        self.adjustSize()
        self.reposition_action_buttons()
        if self.size() != previous_size:
            self.restack_group(pinned=self.is_pinned)
