---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `toast_cancellable_http_notification.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ToastCancellableHttpNotification`](#️-class-toastcancellablehttpnotification)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `closeEvent`](#️-method-closeevent)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `mark_completed`](#️-method-mark_completed)
  - [⚙️ Method `_emit_cancel_requested`](#️-method-_emit_cancel_requested)
  - [⚙️ Method `_on_user_cancel`](#️-method-_on_user_cancel)
  - [⚙️ Method `_refresh_label_text`](#️-method-_refresh_label_text)

</details>

## 🏛️ Class `ToastCancellableHttpNotification`

```python
class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification)
```

Toast with elapsed timer and user-initiated request cancellation.

Attributes:

- `cancel_requested` (`Signal`): Emitted once when the user cancels the request.
- `completed` (`bool`): True after `mark_completed()` was called.

<details>
<summary>Code:</summary>

```python
class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification):

    cancel_requested: Signal = Signal()

    def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        """Initialize cancellable HTTP toast with countdown and Cancel button."""
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        self._cancel_button = QPushButton("Cancel", self)
        self._cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_button.setStyleSheet(
            "background-color: rgba(80, 80, 80, 230);"
            "color: white;"
            "padding: 6px 14px;"
            "border-radius: 6px;"
            "font-size: 11pt;"
            "font-weight: bold;",
        )
        self._cancel_button.clicked.connect(self._on_user_cancel)

        layout = self.layout()
        if layout is not None:
            layout.addWidget(self._cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(8)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop timer and emit cancel when closed by the user before completion."""
        if not self._completed and not self._cancelled:
            self._emit_cancel_requested()
        self.timer.stop()
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel the request when the user presses Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self._on_user_cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def mark_completed(self) -> None:
        """Mark the request as finished so closing the toast does not emit cancel."""
        self._completed = True

    def _emit_cancel_requested(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        self.cancel_requested.emit()

    def _on_user_cancel(self) -> None:
        """Handle Cancel button click or Escape key."""
        if self._completed or self._cancelled:
            return
        self._emit_cancel_requested()
        self.close()

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed seconds, and cancel hint."""
        self.label.setText(
            f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}\n{_CANCEL_HINT}",
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None
```

Initialize cancellable HTTP toast with countdown and Cancel button.

<details>
<summary>Code:</summary>

```python
def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        self._cancel_button = QPushButton("Cancel", self)
        self._cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_button.setStyleSheet(
            "background-color: rgba(80, 80, 80, 230);"
            "color: white;"
            "padding: 6px 14px;"
            "border-radius: 6px;"
            "font-size: 11pt;"
            "font-weight: bold;",
        )
        self._cancel_button.clicked.connect(self._on_user_cancel)

        layout = self.layout()
        if layout is not None:
            layout.addWidget(self._cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(8)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Stop timer and emit cancel when closed by the user before completion.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if not self._completed and not self._cancelled:
            self._emit_cancel_requested()
        self.timer.stop()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Cancel the request when the user presses Escape.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self._on_user_cancel()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `mark_completed`

```python
def mark_completed(self) -> None
```

Mark the request as finished so closing the toast does not emit cancel.

<details>
<summary>Code:</summary>

```python
def mark_completed(self) -> None:
        self._completed = True
```

</details>

### ⚙️ Method `_emit_cancel_requested`

```python
def _emit_cancel_requested(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _emit_cancel_requested(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        self.cancel_requested.emit()
```

</details>

### ⚙️ Method `_on_user_cancel`

```python
def _on_user_cancel(self) -> None
```

Handle Cancel button click or Escape key.

<details>
<summary>Code:</summary>

```python
def _on_user_cancel(self) -> None:
        if self._completed or self._cancelled:
            return
        self._emit_cancel_requested()
        self.close()
```

</details>

### ⚙️ Method `_refresh_label_text`

```python
def _refresh_label_text(self) -> None
```

Update label with message, elapsed seconds, and cancel hint.

<details>
<summary>Code:</summary>

```python
def _refresh_label_text(self) -> None:
        self.label.setText(
            f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}\n{_CANCEL_HINT}",
        )
```

</details>
