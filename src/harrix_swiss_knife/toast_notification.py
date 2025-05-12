from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

from harrix_swiss_knife import toast_notification_base


class ToastNotification(toast_notification_base.ToastNotificationBase):
    """A temporary toast notification that automatically closes after a specified duration.

    This class extends ToastNotificationBase to add automatic closing functionality.
    The notification will appear on screen and automatically disappear after
    the specified duration.

    Attributes:

    - Inherits all attributes from `ToastNotificationBase`

    Args:

    - `message` (`str`): The text to be displayed in the notification.
    - `duration` (`int`, optional): Time in milliseconds before the notification
      automatically closes. Defaults to `1000`.
    - `parent` (`QWidget`, optional): The parent widget. Defaults to `None`.

    """

    def __init__(self, message: str, duration: int = 1000, parent: QWidget | None = None) -> None:
        super().__init__(message, parent)
        QTimer.singleShot(duration, self.close)
