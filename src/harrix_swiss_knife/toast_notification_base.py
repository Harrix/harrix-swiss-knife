from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class ToastNotificationBase(QDialog):
    """
    Base class for toast notifications.

    This class provides a foundation for creating toast-style notification windows
    that appear temporarily on screen. It creates a semi-transparent, frameless
    dialog with a message displayed in the center.

    Attributes:

    - `message` (`str`): The text to be displayed in the notification.
    - `label` (`QLabel`): The label widget that displays the message.

    Args:

    - `message` (`str`): The text to be displayed in the notification.
    - `parent` (`QWidget`, optional): The parent widget. Defaults to `None`.
    """

    def __init__(self, message: str, parent=None):
        super().__init__(parent)

        # Window settings
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Message
        self.message = message
        self.label = QLabel(self.message, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 15px 20px;"
            "border-radius: 10px;"
            "font-size: 16pt;"
            "font-weight: bold;"
        )

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
