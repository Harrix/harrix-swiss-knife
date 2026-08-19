"""Toast countdown notification module with elapsed time display.

This module provides a toast notification that displays a running counter of elapsed time,
useful for indicating ongoing processes while showing how much time has passed.

"""

from PySide6.QtCore import QElapsedTimer, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife import toast_notification_base

_SECONDS_PER_MINUTE = 60
_SECONDS_PER_HOUR = 3600


class ToastCountdownNotification(toast_notification_base.ToastNotificationBase):
    """A toast notification that displays an elapsed time counter.

    This class extends ToastNotificationBase to show a notification with a running
    counter that tracks elapsed time in seconds. Useful for indicating ongoing
    processes while showing how much time has passed.

    Attributes:

    - `elapsed_seconds` (`int`): The number of seconds that have elapsed since starting the countdown.
    - `elapsed_timer` (`QElapsedTimer`): Monotonic timer used to measure elapsed time.
    - `timer` (`QTimer`): Timer object that triggers the time update every second.

    Args:

    - `message` (`str`, optional): The text to be displayed in the notification.
      Defaults to `Process is running…`.
    - `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

    """

    def __init__(self, message: str = "Process is running…", parent: QWidget | None = None) -> None:
        """Initialize the countdown notification with timer functionality.

        Args:

        - `message` (`str`, optional): The text to be displayed in the notification.
          Defaults to `Process is running…`.
        - `parent` (`QWidget | None`, optional): The parent widget. Defaults to `None`.

        """
        super().__init__(message, parent)

        self.elapsed_seconds: int = 0
        self.elapsed_timer: QElapsedTimer = QElapsedTimer()
        self.timer: QTimer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle the notification close event.

        Stops the timer when the notification is closed to prevent memory leaks.

        Args:

        - `event` (`QCloseEvent`): The close event object.

        """
        self.timer.stop()
        super().closeEvent(event)

    def start_countdown(self, *, present: bool = True) -> None:
        """Start the countdown timer and initialize the display.

        Args:

        - `present` (`bool`): When `True`, position and show the notification first.
          Defaults to `True`.

        """
        if present:
            self.present()
        self.elapsed_timer.start()
        self.timer.start(1000)
        self._refresh_label_text()

    def update_time(self) -> None:
        """Update the elapsed time counter.

        This method is called automatically every second when the timer is active.

        """
        self.elapsed_seconds = self.elapsed_timer.elapsed() // 1000
        self._refresh_label_text()

    def _refresh_label_text(self) -> None:
        """Update the notification text with the current elapsed time.

        Refreshes the label to show the original message and clock time
        (`MM:SS` or `HH:MM:SS`) since the countdown started.

        """
        self.label.setText(f"{self.message}\nTime elapsed: {format_elapsed_clock(self.elapsed_seconds)}")


def format_elapsed_clock(seconds: int) -> str:
    """Format elapsed seconds as `MM:SS`, or `HH:MM:SS` after 60 minutes.

    Args:

    - `seconds` (`int`): Non-negative elapsed time in whole seconds.

    Returns:

    - `str`: Clock string such as `00:23`, `01:15`, or `01:00:01`.

    """
    total = max(0, int(seconds))
    if total >= _SECONDS_PER_HOUR:
        hours, rem = divmod(total, _SECONDS_PER_HOUR)
        minutes, secs = divmod(rem, _SECONDS_PER_MINUTE)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    minutes, secs = divmod(total, _SECONDS_PER_MINUTE)
    return f"{minutes:02d}:{secs:02d}"
