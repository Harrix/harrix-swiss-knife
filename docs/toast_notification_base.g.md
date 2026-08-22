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
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `is_pinned (property)`](#%EF%B8%8F-method-is_pinned-property)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `present`](#%EF%B8%8F-method-present)
  - [⚙️ Method `pump_events`](#%EF%B8%8F-method-pump_events)
  - [⚙️ Method `reposition_action_buttons`](#%EF%B8%8F-method-reposition_action_buttons)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `restack_group (classmethod)`](#%EF%B8%8F-method-restack_group-classmethod)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
  - [⚙️ Method `stack_members (classmethod)`](#%EF%B8%8F-method-stack_members-classmethod)
  - [⚙️ Method `user_moved (property)`](#%EF%B8%8F-method-user_moved-property)
- [🔧 Function `compute_toast_stack_positions`](#-function-compute_toast_stack_positions)
- [🔧 Function `event_targets_widget`](#-function-event_targets_widget)
- [🔧 Function `format_toast_cancel_hint_html`](#-function-format_toast_cancel_hint_html)
- [🔧 Function `make_action_icon`](#-function-make_action_icon)
- [🔧 Function `process_events_allowing_widget`](#-function-process_events_allowing_widget)

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
        # Clicks must reach the dialog so dragging and double-click pin work.
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._apply_default_style()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Dragging tracking variables
        self.dragging = False
        self.drag_position = QPoint()
        self._user_moved = False

        # Pinned state (bottom-right near system tray)
        self._is_pinned = False
        self.stack_order = next(_stack_seq)

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

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Unregister from the stack and restack remaining toasts of the same pin group."""
        was_pinned = self.is_pinned
        _active_toasts.discard(self)
        super().closeEvent(event)
        self.restack_group(pinned=was_pinned)

    @property
    def is_pinned(self) -> bool:
        """Whether the toast uses the compact bottom-right layout."""
        return self._is_pinned

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
            self._user_moved = True
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
        """Size, position via the toast stack, and show on top."""
        self.adjustSize()
        self.show()
        self.raise_()
        self.activateWindow()
        self._position_collapse_button()

    def pump_events(self) -> None:
        """Process queued Qt events while keeping this toast clickable and draggable.

        Use during long UI-thread work instead of
        `QApplication.processEvents(ExcludeUserInputEvents)`, which updates the
        toast text but drops mouse input.

        """
        process_events_allowing_widget(self)

    def reposition_action_buttons(self) -> None:
        """Place collapse (and subclass) action buttons after a move or resize."""
        self._position_collapse_button()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition the collapse button when the toast is resized."""
        super().resizeEvent(event)
        self._position_collapse_button()

    @classmethod
    def restack_group(cls, *, pinned: bool) -> None:
        """Reposition all visible toasts in the given pin group."""
        toasts = cls.stack_members(pinned=pinned)
        if not toasts:
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            return

        area = screen.availableGeometry()
        for toast in toasts:
            toast.adjustSize()

        points = compute_toast_stack_positions(
            [toast.size() for toast in toasts],
            area=area,
            pinned=pinned,
        )
        for toast, point in zip(toasts, points, strict=True):
            toast.move(point)
            toast.reposition_action_buttons()

        toasts[-1].raise_()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Register in the active stack and restack the pin group."""
        super().showEvent(event)
        _active_toasts.add(self)
        self.restack_group(pinned=self.is_pinned)

    @classmethod
    def stack_members(cls, *, pinned: bool) -> list[ToastNotificationBase]:
        """Return visible toasts in a pin group that still follow automatic stacking."""
        return [
            toast
            for toast in sorted(_active_toasts, key=lambda item: item.stack_order)
            if toast.isVisible() and toast.is_pinned == pinned and not toast.user_moved
        ]

    @property
    def user_moved(self) -> bool:
        """Whether the user dragged this toast away from the automatic stack."""
        return self._user_moved

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

    def _move_to_bottom_right_corner(self, *, margin: int = SCREEN_MARGIN) -> None:
        """Move the notification to the bottom-right of the primary screen."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.move(_toast_home_point(area, self.size(), pinned=True, margin=margin))

    def _move_to_screen_center(self) -> None:
        """Move the notification to the center of the primary screen."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.move(_toast_home_point(area, self.size(), pinned=False, margin=SCREEN_MARGIN))

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
        self._user_moved = False
        if self._is_pinned:
            self._is_pinned = False
            self._apply_default_style()
            self.adjustSize()
        else:
            self._is_pinned = True
            self._apply_compact_style()
            self.adjustSize()
        self.restack_group(pinned=False)
        self.restack_group(pinned=True)

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
        # Clicks must reach the dialog so dragging and double-click pin work.
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._apply_default_style()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Dragging tracking variables
        self.dragging = False
        self.drag_position = QPoint()
        self._user_moved = False

        # Pinned state (bottom-right near system tray)
        self._is_pinned = False
        self.stack_order = next(_stack_seq)

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

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Unregister from the stack and restack remaining toasts of the same pin group.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        was_pinned = self.is_pinned
        _active_toasts.discard(self)
        super().closeEvent(event)
        self.restack_group(pinned=was_pinned)
```

</details>

### ⚙️ Method `is_pinned (property)`

```python
def is_pinned(self) -> bool
```

Whether the toast uses the compact bottom-right layout.

<details>
<summary>Code:</summary>

```python
def is_pinned(self) -> bool:
        return self._is_pinned
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
            self._user_moved = True
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

Size, position via the toast stack, and show on top.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self.adjustSize()
        self.show()
        self.raise_()
        self.activateWindow()
        self._position_collapse_button()
```

</details>

### ⚙️ Method `pump_events`

```python
def pump_events(self) -> None
```

Process queued Qt events while keeping this toast clickable and draggable.

Use during long UI-thread work instead of
`QApplication.processEvents(ExcludeUserInputEvents)`, which updates the
toast text but drops mouse input.

<details>
<summary>Code:</summary>

```python
def pump_events(self) -> None:
        process_events_allowing_widget(self)
```

</details>

### ⚙️ Method `reposition_action_buttons`

```python
def reposition_action_buttons(self) -> None
```

Place collapse (and subclass) action buttons after a move or resize.

<details>
<summary>Code:</summary>

```python
def reposition_action_buttons(self) -> None:
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

### ⚙️ Method `restack_group (classmethod)`

```python
def restack_group(cls, *, pinned: bool) -> None
```

Reposition all visible toasts in the given pin group.

<details>
<summary>Code:</summary>

```python
def restack_group(cls, *, pinned: bool) -> None:
        toasts = cls.stack_members(pinned=pinned)
        if not toasts:
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            return

        area = screen.availableGeometry()
        for toast in toasts:
            toast.adjustSize()

        points = compute_toast_stack_positions(
            [toast.size() for toast in toasts],
            area=area,
            pinned=pinned,
        )
        for toast, point in zip(toasts, points, strict=True):
            toast.move(point)
            toast.reposition_action_buttons()

        toasts[-1].raise_()
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Register in the active stack and restack the pin group.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        _active_toasts.add(self)
        self.restack_group(pinned=self.is_pinned)
```

</details>

### ⚙️ Method `stack_members (classmethod)`

```python
def stack_members(cls, *, pinned: bool) -> list[ToastNotificationBase]
```

Return visible toasts in a pin group that still follow automatic stacking.

<details>
<summary>Code:</summary>

```python
def stack_members(cls, *, pinned: bool) -> list[ToastNotificationBase]:
        return [
            toast
            for toast in sorted(_active_toasts, key=lambda item: item.stack_order)
            if toast.isVisible() and toast.is_pinned == pinned and not toast.user_moved
        ]
```

</details>

### ⚙️ Method `user_moved (property)`

```python
def user_moved(self) -> bool
```

Whether the user dragged this toast away from the automatic stack.

<details>
<summary>Code:</summary>

```python
def user_moved(self) -> bool:
        return self._user_moved
```

</details>

## 🔧 Function `compute_toast_stack_positions`

```python
def compute_toast_stack_positions(sizes: list[QSize], *, area: QRect, pinned: bool, gap: int = STACK_GAP, margin: int = SCREEN_MARGIN) -> list[QPoint]
```

Return top-left points for toasts ordered oldest → newest.

Newest sits at the home anchor (screen center, or bottom-right when pinned).
Older toasts stack upward with `gap` when they fit above the available top
margin; otherwise they share the home position (overlap).

<details>
<summary>Code:</summary>

```python
def compute_toast_stack_positions(
    sizes: list[QSize],
    *,
    area: QRect,
    pinned: bool,
    gap: int = STACK_GAP,
    margin: int = SCREEN_MARGIN,
) -> list[QPoint]:
    if not sizes:
        return []

    points: list[QPoint] = [QPoint() for _ in sizes]
    newest_index = len(sizes) - 1
    newest_home = _toast_home_point(area, sizes[newest_index], pinned=pinned, margin=margin)
    points[newest_index] = newest_home
    stack_top = newest_home.y()

    for index in range(newest_index - 1, -1, -1):
        size = sizes[index]
        home = _toast_home_point(area, size, pinned=pinned, margin=margin)
        proposed_y = stack_top - gap - size.height()
        if proposed_y >= area.y() + margin:
            points[index] = QPoint(home.x(), proposed_y)
            stack_top = proposed_y
        else:
            points[index] = home

    return points
```

</details>

## 🔧 Function `event_targets_widget`

```python
def event_targets_widget(watched: QObject, root: QWidget) -> bool
```

Return whether `watched` belongs to `root` or its native window.

<details>
<summary>Code:</summary>

```python
def event_targets_widget(watched: QObject, root: QWidget) -> bool:
    root_window = root.windowHandle()
    current: QObject | None = watched
    while current is not None:
        if current is root or current is root_window:
            return True
        current = current.parent()
    return False
```

</details>

## 🔧 Function `format_toast_cancel_hint_html`

```python
def format_toast_cancel_hint_html(body: str, hint: str, *, compact: bool = False) -> str
```

Return rich text with `hint` on a smaller line under `body`.

Args:

- `body` (`str`): Main toast lines, separated by newlines.
- `hint` (`str`): Cancel hint such as `Press Esc to cancel`.
- `compact` (`bool`): Use the compact hint size. Defaults to `False`.

Returns:

- `str`: HTML for a `QLabel` with `RichText` format.

<details>
<summary>Code:</summary>

```python
def format_toast_cancel_hint_html(body: str, hint: str, *, compact: bool = False) -> str:
    size = CANCEL_HINT_FONT_SIZE_COMPACT if compact else CANCEL_HINT_FONT_SIZE
    lines = "<br>".join(escape(part) for part in body.split("\n"))
    return f'{lines}<br><span style="font-size: {size}; font-weight: normal;">{escape(hint)}</span>'
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

## 🔧 Function `process_events_allowing_widget`

```python
def process_events_allowing_widget(widget: QWidget | None) -> None
```

Pump the event loop so `widget` stays interactive during long UI-thread work.

The rest of the UI still receives paint and timer events, but mouse and
keyboard input is delivered only to `widget` and its descendants. That keeps
a toast draggable without letting the owner window re-enter catalog load
handlers.

<details>
<summary>Code:</summary>

```python
def process_events_allowing_widget(widget: QWidget | None) -> None:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return
    if widget is None:
        app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        return
    event_filter = _AllowWidgetInputFilter(widget)
    app.installEventFilter(event_filter)
    try:
        app.processEvents()
    finally:
        app.removeEventFilter(event_filter)
```

</details>
