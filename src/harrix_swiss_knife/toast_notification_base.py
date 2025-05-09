from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class ToastNotificationBase(QDialog):
    """Base class for toast notifications.

    This class provides a foundation for creating toast-style notification windows
    that appear temporarily on screen. It creates a semi-transparent, frameless
    dialog with a message displayed in the center.

    Attributes:
        message (str): The text to be displayed in the notification.
        label (QLabel): The label widget that displays the message.

    Args:
        message (str): The text to be displayed in the notification.
        parent (QWidget, optional): The parent widget. Defaults to None.

    """

    def __init__(self, message: str, parent=None) -> None:
        """Initializes the toast notification with the specified message and parent widget.

        Args:

        - `message` (`str`): The message to display in the toast notification.
        - `parent` (`Optional[QWidget]`): The parent widget of the notification. Defaults to `None`.

        """
        super().__init__(parent)

        # Window settings
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Message display
        self.message = message
        self.label = QLabel(self.message, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 15px 20px;"
            "border-radius: 10px;"
            "font-size: 16pt;"
            "font-weight: bold;",
        )

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Dragging tracking variables
        self.dragging = False
        self.drag_position = QPoint()

        # Enable mouse tracking for drag operations
        self.setMouseTracking(True)

        # Set cursor to indicate draggable window
        self.setCursor(Qt.OpenHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles the mouse move event to update the position of the notification during dragging.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the move action.

        """
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles the mouse press event to initiate dragging of the notification.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the press action.

        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)  # Change cursor to indicate active dragging
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handles the mouse release event to conclude the dragging of the notification.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the release action.

        """
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)  # Restore cursor to indicate draggable state
            event.accept()
