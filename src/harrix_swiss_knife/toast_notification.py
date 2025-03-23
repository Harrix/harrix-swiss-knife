from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout


class ToastNotification(QDialog):
    """
    Represents a toast notification window that displays a message and
    automatically closes after a specified duration.

    Args:

    - `message` (`str`): The text to be displayed in the notification.
    - `duration` (`int`): The time in milliseconds after which the window closes. Defaults to `1000`.
    - `parent`: The parent widget, usually `None`.

    Attributes:

    - `label` (`QLabel`): The label used to display the message with specific styling.
    """

    def __init__(self, message: str, duration: int = 1000, parent=None):
        # Inherit QDialog
        super().__init__(parent)

        # Set window flags
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Set transparent background for the entire dialog
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Message text
        self.label = QLabel(message, self)
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 15px 20px;"
            "border-radius: 10px;"
            "font-size: 16pt;"
            "font-weight: bold;"
        )
        self.label.setAlignment(Qt.AlignCenter)

        # Layout the contents without margins
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Start a timer that closes the window after the duration
        QTimer.singleShot(duration, self.close)
