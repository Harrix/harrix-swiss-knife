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
  - [⚙️ Method `present`](#%EF%B8%8F-method-present)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
- [🔧 Function `make_action_icon`](#-function-make_action_icon)

</details>

## 🏛️ Class `ToastNotificationBase`

```python
class ToastNotificationBase(QDialog)
```

Base class for toast notifications.

This class provides a foundation for creating toast-style notification dialogs
that appear temporarily on screen. It creates a semi-transparent, frameless
dialog with a message displayed in the center.

Attributes:

- `message` (`str`): The text to be displayed in the notification.
- `label` (`QLabel`): The label widget that displays the message.

<details>
<summary>Code:</summary>

```python
class ToastNotificationBase(QDialog):

    def __init__(self, message: str, parent: QWidget | None = None) -> None:
        """Initialize the toast notification with the specified message and parent widget.

        Args:

        - `message` (`str`): The message to display in the toast notification.
        - `parent` (`QWidget | None`): The parent widget of the notification. Defaults to `None`.

        """
        super().__init__(parent)

        # Window settings
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Message display
        self.message = message
        self.label = QLabel(self.message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._apply_default_style()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Dragging tracking variables
        self.dragging = False
        self.drag_position = QPoint()

        # Pinned state (bottom-right near system tray)
        self._is_pinned = False

        # Enable mouse tracking for drag operations
        self.setMouseTracking(True)

        # Set cursor to indicate draggable window
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._collapse_button = QPushButton(self)
        self._collapse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapse_button.setFlat(True)
        self._collapse_button.setStyleSheet(DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_collapse_button_icon(compact=False)
        self._collapse_button.setToolTip("Collapse")
        self._collapse_button.clicked.connect(self._toggle_pinned)
        self._position_collapse_button()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Toggle pinned (compact, bottom-right) and expanded (large, centered) layout.

        First double-click pins the notification near the system tray with compact styling.
        A second double-click restores the default size and centers it on the primary screen.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the double-click action.

        """
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._toggle_pinned()
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

    def present(self) -> None:
        """Size, position at the center of the primary screen, and show on top."""
        self.adjustSize()
        self._move_to_screen_center()
        self.show()
        self.raise_()
        self.activateWindow()
        self._position_collapse_button()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition the collapse button when the toast is resized."""
        super().resizeEvent(event)
        self._position_collapse_button()

    def _action_button_side(self) -> int:
        """Return the action-button side length for the current pin state."""
        return COMPACT_ACTION_BUTTON_SIDE if self._is_pinned else DEFAULT_ACTION_BUTTON_SIDE

    def _apply_collapse_button_icon(self, *, compact: bool) -> None:
        side = COMPACT_ACTION_BUTTON_SIDE if compact else DEFAULT_ACTION_BUTTON_SIDE
        symbol = _EXPAND_SYMBOL if self._is_pinned else _COLLAPSE_SYMBOL
        self._collapse_button.setFixedSize(side, side)
        self._collapse_button.setIconSize(QSize(side, side))
        self._collapse_button.setIcon(make_action_icon(side, symbol))
        self._collapse_button.setToolTip("Expand" if self._is_pinned else "Collapse")

    def _apply_compact_style(self) -> None:
        """Apply compact styling with reduced font size for pinned notifications."""
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 8px 12px;"
            "border-radius: 8px;"
            "font-size: 10pt;"
            "font-weight: bold;",
        )
        if hasattr(self, "_collapse_button"):
            self._collapse_button.setStyleSheet(COMPACT_ACTION_BUTTON_STYLE)
            self._apply_collapse_button_icon(compact=True)
            self._position_collapse_button()

    def _apply_default_style(self) -> None:
        """Apply default styling for expanded, centered notifications."""
        self.label.setStyleSheet(
            "background-color: rgba(40, 40, 40, 230);"
            "color: white;"
            "padding: 15px 20px;"
            "border-radius: 10px;"
            "font-size: 16pt;"
            "font-weight: bold;",
        )
        if hasattr(self, "_collapse_button"):
            self._collapse_button.setStyleSheet(DEFAULT_ACTION_BUTTON_STYLE)
            self._apply_collapse_button_icon(compact=False)
            self._position_collapse_button()

    def _move_to_bottom_right_corner(self, *, margin: int = 20) -> None:
        """Move the notification to the bottom-right of the primary screen."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.move(
            area.x() + area.width() - self.width() - margin,
            area.y() + area.height() - self.height() - margin,
        )

    def _move_to_screen_center(self) -> None:
        """Move the notification to the center of the primary screen."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.move(
            area.x() + (area.width() - self.width()) // 2,
            area.y() + (area.height() - self.height()) // 2,
        )

    def _position_collapse_button(self) -> None:
        """Place the collapse button near the top-right of the message label."""
        if not hasattr(self, "_collapse_button"):
            return
        label_geom = self.label.geometry()
        side = self._action_button_side()
        margin = 2 if self._is_pinned else 4
        right_offset = self._trailing_controls_width()
        self._collapse_button.move(
            label_geom.x() + label_geom.width() - side - margin - right_offset,
            label_geom.y() + margin,
        )
        self._collapse_button.raise_()

    def _toggle_pinned(self) -> None:
        """Toggle between pinned compact layout and expanded centered layout."""
        if self._is_pinned:
            self._is_pinned = False
            self._apply_default_style()
            self.adjustSize()
            self._move_to_screen_center()
        else:
            self._is_pinned = True
            self._apply_compact_style()
            self.adjustSize()
            self._move_to_bottom_right_corner()

    def _trailing_controls_width(self) -> int:
        """Width reserved to the right of the collapse button for subclass controls."""
        return 0
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str, parent: QWidget | None = None) -> None
```

Initialize the toast notification with the specified message and parent widget.

Args:

- `message` (`str`): The message to display in the toast notification.
- `parent` (`QWidget | None`): The parent widget of the notification. Defaults to `None`.

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
        self._apply_default_style()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Dragging tracking variables
        self.dragging = False
        self.drag_position = QPoint()

        # Pinned state (bottom-right near system tray)
        self._is_pinned = False

        # Enable mouse tracking for drag operations
        self.setMouseTracking(True)

        # Set cursor to indicate draggable window
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._collapse_button = QPushButton(self)
        self._collapse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapse_button.setFlat(True)
        self._collapse_button.setStyleSheet(DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_collapse_button_icon(compact=False)
        self._collapse_button.setToolTip("Collapse")
        self._collapse_button.clicked.connect(self._toggle_pinned)
        self._position_collapse_button()
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Toggle pinned (compact, bottom-right) and expanded (large, centered) layout.

First double-click pins the notification near the system tray with compact styling.
A second double-click restores the default size and centers it on the primary screen.

Args:

- `event` (`QMouseEvent`): The mouse event triggering the double-click action.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._toggle_pinned()
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

### ⚙️ Method `present`

```python
def present(self) -> None
```

Size, position at the center of the primary screen, and show on top.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self.adjustSize()
        self._move_to_screen_center()
        self.show()
        self.raise_()
        self.activateWindow()
        self._position_collapse_button()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reposition the collapse button when the toast is resized.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_collapse_button()
```

</details>

## 🔧 Function `make_action_icon`

```python
def make_action_icon(side: int, symbol: str) -> QIcon
```

Render a centered action symbol for the given button side length.

<details>
<summary>Code:</summary>

```python
def make_action_icon(side: int, symbol: str) -> QIcon:
    pixmap = QPixmap(side, side)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = painter.font()
    font.setPixelSize(max(10, int(side * 0.72)))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, symbol)
    painter.end()
    return QIcon(pixmap)
```

</details>
