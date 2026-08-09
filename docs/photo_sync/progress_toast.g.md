---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `progress_toast.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PhotoSyncProgressController`](#%EF%B8%8F-class-photosyncprogresscontroller)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `attach`](#%EF%B8%8F-method-attach)
  - [⚙️ Method `detach`](#%EF%B8%8F-method-detach)
  - [⚙️ Method `hide`](#%EF%B8%8F-method-hide)
  - [⚙️ Method `request_refresh`](#%EF%B8%8F-method-request_refresh)
  - [⚙️ Method `set_open_dialog_callback`](#%EF%B8%8F-method-set_open_dialog_callback)
- [🏛️ Class `PhotoSyncProgressToast`](#%EF%B8%8F-class-photosyncprogresstoast)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `set_progress_text`](#%EF%B8%8F-method-set_progress_text)

</details>

## 🏛️ Class `PhotoSyncProgressController`

```python
class PhotoSyncProgressController(QObject)
```

Marshal server `on_change` onto the UI thread and drive the progress toast.

<details>
<summary>Code:</summary>

```python
class PhotoSyncProgressController(QObject):

    _refresh_requested = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Create a controller with no toast until a transfer starts."""
        super().__init__(parent)
        self._toast: PhotoSyncProgressToast | None = None
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self._refresh_requested.connect(self._on_refresh)
        self._open_dialog = _default_open_photo_sync_dialog

    def attach(self, server: PhotoSyncServer) -> None:
        """Listen for server status updates (safe from HTTP worker threads)."""
        server.set_on_change(self.request_refresh)

    def detach(self, server: PhotoSyncServer | None = None) -> None:
        """Clear the server callback and hide the toast."""
        if server is not None:
            server.set_on_change(None)
        self.hide()

    def hide(self) -> None:
        """Close the progress toast if it is visible."""
        self._hide_timer.stop()
        toast = self._toast
        self._toast = None
        if toast is not None:
            toast.close()

    def request_refresh(self) -> None:
        """Queue a UI refresh (callable from any thread)."""
        self._refresh_requested.emit()

    def set_open_dialog_callback(self, callback: Callable[[], None]) -> None:
        """Override the click action (mainly for tests)."""
        self._open_dialog = callback

    def _ensure_toast(self) -> PhotoSyncProgressToast:
        if self._toast is None:
            toast = PhotoSyncProgressToast("Photo sync…")
            toast.clicked.connect(self._open_dialog)
            self._toast = toast
        return self._toast

    def _on_refresh(self) -> None:
        server = get_shared_server()
        if server is None or not server.is_running:
            self.hide()
            return
        stats = server.stats
        if stats.session_total <= 0:
            return
        text = f"Photo sync: {stats.session_done} / {stats.session_total}"
        toast = self._ensure_toast()
        toast.set_progress_text(text)
        if not toast.isVisible():
            toast.present()
            toast.restack_group(pinned=True)
        if stats.session_in_progress:
            self._hide_timer.stop()
        else:
            # Show the completed count briefly, then hide.
            self._hide_timer.start(_COMPLETE_HIDE_DELAY_MS)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QObject | None = None) -> None
```

Create a controller with no toast until a transfer starts.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._toast: PhotoSyncProgressToast | None = None
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)
        self._refresh_requested.connect(self._on_refresh)
        self._open_dialog = _default_open_photo_sync_dialog
```

</details>

### ⚙️ Method `attach`

```python
def attach(self, server: PhotoSyncServer) -> None
```

Listen for server status updates (safe from HTTP worker threads).

<details>
<summary>Code:</summary>

```python
def attach(self, server: PhotoSyncServer) -> None:
        server.set_on_change(self.request_refresh)
```

</details>

### ⚙️ Method `detach`

```python
def detach(self, server: PhotoSyncServer | None = None) -> None
```

Clear the server callback and hide the toast.

<details>
<summary>Code:</summary>

```python
def detach(self, server: PhotoSyncServer | None = None) -> None:
        if server is not None:
            server.set_on_change(None)
        self.hide()
```

</details>

### ⚙️ Method `hide`

```python
def hide(self) -> None
```

Close the progress toast if it is visible.

<details>
<summary>Code:</summary>

```python
def hide(self) -> None:
        self._hide_timer.stop()
        toast = self._toast
        self._toast = None
        if toast is not None:
            toast.close()
```

</details>

### ⚙️ Method `request_refresh`

```python
def request_refresh(self) -> None
```

Queue a UI refresh (callable from any thread).

<details>
<summary>Code:</summary>

```python
def request_refresh(self) -> None:
        self._refresh_requested.emit()
```

</details>

### ⚙️ Method `set_open_dialog_callback`

```python
def set_open_dialog_callback(self, callback: Callable[[], None]) -> None
```

Override the click action (mainly for tests).

<details>
<summary>Code:</summary>

```python
def set_open_dialog_callback(self, callback: Callable[[], None]) -> None:
        self._open_dialog = callback
```

</details>

## 🏛️ Class `PhotoSyncProgressToast`

```python
class PhotoSyncProgressToast(ToastNotificationBase)
```

Toast-styled banner that stays pinned near the tray during a transfer.

Looks like other HSK toasts but is not [`ToastNotification`](../toast_notification.g.md#%EF%B8%8F-class-toastnotification) (no auto-dismiss
while a transfer is running). A short click (not a drag) emits `clicked`.

<details>
<summary>Code:</summary>

```python
class PhotoSyncProgressToast(ToastNotificationBase):

    clicked = Signal()

    def __init__(self, message: str = "Photo sync…") -> None:
        """Create a pinned progress toast with `message`."""
        super().__init__(message)
        self._press_global: QPoint | None = None
        self._dragged = False
        self._is_pinned = True
        self._apply_compact_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Open Photo sync")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Mark the gesture as a drag when the pointer moves far enough."""
        if self._press_global is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._press_global
            if abs(delta.x()) >= _DRAG_THRESHOLD_PX or abs(delta.y()) >= _DRAG_THRESHOLD_PX:
                self._dragged = True
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Remember press position to distinguish click from drag."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._dragged = False
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit `clicked` for a short left-button release without dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            was_drag = self._dragged
            self._press_global = None
            self._dragged = False
            super().mouseReleaseEvent(event)
            if not was_drag:
                self.clicked.emit()
            return
        super().mouseReleaseEvent(event)

    def set_progress_text(self, text: str) -> None:
        """Update the label and restack while staying pinned."""
        self.message = text
        self.label.setText(text)
        self.adjustSize()
        if not self.is_pinned:
            self._is_pinned = True
            self._apply_compact_style()
        self.restack_group(pinned=True)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str = 'Photo sync…') -> None
```

Create a pinned progress toast with `message`.

<details>
<summary>Code:</summary>

```python
def __init__(self, message: str = "Photo sync…") -> None:
        super().__init__(message)
        self._press_global: QPoint | None = None
        self._dragged = False
        self._is_pinned = True
        self._apply_compact_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Open Photo sync")
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Mark the gesture as a drag when the pointer moves far enough.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._press_global is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._press_global
            if abs(delta.x()) >= _DRAG_THRESHOLD_PX or abs(delta.y()) >= _DRAG_THRESHOLD_PX:
                self._dragged = True
        super().mouseMoveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Remember press position to distinguish click from drag.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._dragged = False
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Emit `clicked` for a short left-button release without dragging.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            was_drag = self._dragged
            self._press_global = None
            self._dragged = False
            super().mouseReleaseEvent(event)
            if not was_drag:
                self.clicked.emit()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `set_progress_text`

```python
def set_progress_text(self, text: str) -> None
```

Update the label and restack while staying pinned.

<details>
<summary>Code:</summary>

```python
def set_progress_text(self, text: str) -> None:
        self.message = text
        self.label.setText(text)
        self.adjustSize()
        if not self.is_pinned:
            self._is_pinned = True
            self._apply_compact_style()
        self.restack_group(pinned=True)
```

</details>
