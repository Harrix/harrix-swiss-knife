from PySide6.QtCore import QTime, QTimer

from harrix_swiss_knife import toast_notification_base


class ToastCountdownNotification(toast_notification_base.ToastNotificationBase):
    """A toast notification that displays an elapsed time counter.

    This class extends ToastNotificationBase to show a notification with a running
    counter that tracks elapsed time in seconds. Useful for indicating ongoing
    processes while showing how much time has passed.

    Attributes:

    - `elapsed_seconds` (`int`): The number of seconds that have elapsed since starting the countdown.
    - `timer` (`QTimer`): Timer object that triggers the time update every second.
    - `start_time` (`QTime`): The time when the countdown was started.

    Args:

    - `message` (`str`, optional): The text to be displayed in the notification.
      Defaults to `"Process is running…"`.
    - `parent` (`QWidget`, optional): The parent widget. Defaults to `None`.

    """

    def __init__(self, message: str = "Process is running…", parent=None) -> None:
        super().__init__(message, parent)

        self.elapsed_seconds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

    def _refresh_label_text(self) -> None:
        """Updates the notification text with the current elapsed time."""
        self.label.setText(f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}")

    def closeEvent(self, event) -> None:  # noqa: N802
        """Handle the notification close event.

        Stops the timer when the notification is closed to prevent memory leaks.

        Args:

        - `event`: The close event object.

        """
        self.timer.stop()
        super().closeEvent(event)

    def start_countdown(self) -> None:
        """Start the countdown timer and initializes the display."""
        self.start_time = QTime.currentTime()
        self.timer.start(1000)
        self._refresh_label_text()

    def update_time(self) -> None:
        """Update the elapsed time counter.

        This method is called automatically every second when the timer is active.
        """
        now = QTime.currentTime()
        self.elapsed_seconds = self.start_time.secsTo(now)
        self._refresh_label_text()
