from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class ToastCountdownNotification(QDialog):
    """
    A toast notification with a timer (stopwatch).
    Updates the elapsed time every second while the window is open.

    Attributes:

    - `message` (`str`): The initial message displayed. Defaults to "Process is running...".
    - `elapsed_seconds` (`int`): The number of seconds elapsed since the timer started.
    """

    def __init__(self, message: str = "Process is running...", parent=None):
        super().__init__(parent)

        # Make the window stay on top, without borders, and with a transparent background
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Label to display the message and time
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 15px 20px;"
            "border-radius: 10px;"
            "font-size: 16pt;"
            "font-weight: bold;"
        )

        # Initial text
        self.message = message
        self.elapsed_seconds = 0

        # Place the label in the layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Start a timer with 1-second intervals
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

    def _refresh_label_text(self):
        self.label.setText(f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}")

    def closeEvent(self, event):
        """
        Stops the timer when the window is closed.
        """
        self.timer.stop()
        return super().closeEvent(event)

    def start_countdown(self):
        """
        Starts the stopwatch.
        """
        self.start_time = QTime.currentTime()
        self.timer.start(1000)  # tick every second
        self._refresh_label_text()

    def update_time(self):
        """
        Updates the time display in the label.
        """
        now = QTime.currentTime()
        self.elapsed_seconds = self.start_time.secsTo(now)
        self._refresh_label_text()
