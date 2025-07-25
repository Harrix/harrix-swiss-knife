---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `toast_notification_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ToastNotificationBase`](#%EF%B8%8F-class-toastnotificationbase)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)

</details>

## 🏛️ Class `ToastNotificationBase`

```python
class ToastNotificationBase(QDialog)
```

Base class for toast notifications.

This class provides a foundation for creating toast-style notification windows
that appear temporarily on screen. It creates a semi-transparent, frameless
dialog with a message displayed in the center.

Attributes:
message (str): The text to be displayed in the notification.
label (QLabel): The label widget that displays the message.

Args:
message (str): The text to be displayed in the notification.
parent (QWidget, optional): The parent widget. Defaults to None.

<details>
<summary>Code:</summary>

```python
class ToastNotificationBase(QDialog):

    def __init__(self, message: str, parent: QWidget | None = None) -> None:
        """Initialize the toast notification with the specified message and parent widget.

        Args:

        - `message` (`str`): The message to display in the toast notification.
        - `parent` (`Optional[QWidget]`): The parent widget of the notification. Defaults to `None`.

        """
        super().__init__(parent)

        # Window settings
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Message display
        self.message = message
        self.label = QLabel(self.message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse double-click event to move the notification to the right side of the screen.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the double-click action.

        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the screen geometry
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()

            # Calculate position at the right side of the screen
            # Position it with some margin from the right edge
            margin = 20
            new_x = screen_geometry.width() - self.width() - margin
            new_y = self.y()  # Keep the current vertical position

            # Move the notification to the right side
            self.move(new_x, new_y)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse move event to update the position of the notification during dragging.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the move action.

        """
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse press event to initiate dragging of the notification.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the press action.

        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)  # Change cursor to indicate active dragging
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse release event to conclude the dragging of the notification.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the release action.

        """
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)  # Restore cursor to indicate draggable state
            event.accept()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str, parent: QWidget | None = None) -> None
```

Initialize the toast notification with the specified message and parent widget.

Args:

- `message` (`str`): The message to display in the toast notification.
- `parent` (`Optional[QWidget]`): The parent widget of the notification. Defaults to `None`.

<details>
<summary>Code:</summary>

```python
def __init__(self, message: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # Window settings
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Message display
        self.message = message
        self.label = QLabel(self.message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self.setCursor(Qt.CursorShape.OpenHandCursor)
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Handle the mouse double-click event to move the notification to the right side of the screen.

Args:

- `event` (`QMouseEvent`): The mouse event triggering the double-click action.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the screen geometry
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()

            # Calculate position at the right side of the screen
            # Position it with some margin from the right edge
            margin = 20
            new_x = screen_geometry.width() - self.width() - margin
            new_y = self.y()  # Keep the current vertical position

            # Move the notification to the right side
            self.move(new_x, new_y)
            event.accept()
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Handle the mouse move event to update the position of the notification during dragging.

Args:

- `event` (`QMouseEvent`): The mouse event triggering the move action.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Handle the mouse press event to initiate dragging of the notification.

Args:

- `event` (`QMouseEvent`): The mouse event triggering the press action.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)  # Change cursor to indicate active dragging
            event.accept()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Handle the mouse release event to conclude the dragging of the notification.

Args:

- `event` (`QMouseEvent`): The mouse event triggering the release action.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)  # Restore cursor to indicate draggable state
            event.accept()
```

</details>
