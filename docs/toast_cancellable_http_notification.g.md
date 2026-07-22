---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `toast_cancellable_http_notification.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ToastCancellableHttpNotification`](#%EF%B8%8F-class-toastcancellablehttpnotification)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `mark_completed`](#%EF%B8%8F-method-mark_completed)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)

</details>

## 🏛️ Class `ToastCancellableHttpNotification`

```python
class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification)
```

Toast with elapsed timer and user-initiated request cancellation.

Attributes:

- `cancel_requested` (`Signal`): Emitted once when the user cancels the request.
- `completed` (`bool`): `True` after `mark_completed()` was called.

<details>
<summary>Code:</summary>

```python
class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification):

    cancel_requested: Signal = Signal()

    def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        """Initialize cancellable HTTP toast with countdown and close control."""
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        self._close_button = QPushButton(self)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setFlat(True)
        self._close_button.setStyleSheet(_DEFAULT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._close_button.setToolTip("Cancel request")
        self._close_button.clicked.connect(self._on_user_cancel)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_close_button()

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

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition the close button when the toast is resized."""
        super().resizeEvent(event)
        self._position_close_button()

    def _apply_close_button_icon(self, *, compact: bool) -> None:
        side = _COMPACT_CLOSE_BUTTON_SIDE if compact else _DEFAULT_CLOSE_BUTTON_SIDE
        self._close_button.setFixedSize(side, side)
        self._close_button.setIconSize(QSize(side, side))
        self._close_button.setIcon(_make_close_icon(side))

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and close button."""
        super()._apply_compact_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(_COMPACT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=True)
        self._position_close_button()
        self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and close button."""
        super()._apply_default_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(_DEFAULT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._position_close_button()
        self._refresh_label_text()

    def _emit_cancel_requested(self) -> None:
        if self._cancelled:
            return
        self._cancelled = True
        self.cancel_requested.emit()

    def _on_user_cancel(self) -> None:
        """Handle close button click or Escape key."""
        if self._completed or self._cancelled:
            return
        self._emit_cancel_requested()
        self.close()

    def _position_close_button(self) -> None:
        """Place the close button at the top-right corner of the message label."""
        if not hasattr(self, "_close_button"):
            return
        label_geom = self.label.geometry()
        side = _COMPACT_CLOSE_BUTTON_SIDE if self._is_pinned else _DEFAULT_CLOSE_BUTTON_SIDE
        margin = 2 if self._is_pinned else 4
        self._close_button.move(
            label_geom.x() + label_geom.width() - side - margin,
            label_geom.y() + margin,
        )
        self._close_button.raise_()

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed seconds, and cancel hint."""
        if self._is_pinned:
            self.label.setText(f"{self.message}\n{self.elapsed_seconds}s")
        else:
            self.label.setText(
                f"{self.message}\nSeconds elapsed: {self.elapsed_seconds}\n{_CANCEL_HINT}",
            )
        self.adjustSize()
        self._position_close_button()
        if self._is_pinned:
            self._move_to_bottom_right_corner()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None
```

Initialize cancellable HTTP toast with countdown and close control.

<details>
<summary>Code:</summary>

```python
def __init__(self, message: str = "Request in progress…", parent: QWidget | None = None) -> None:
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        self._close_button = QPushButton(self)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setFlat(True)
        self._close_button.setStyleSheet(_DEFAULT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._close_button.setToolTip("Cancel request")
        self._close_button.clicked.connect(self._on_user_cancel)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_close_button()
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

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reposition the close button when the toast is resized.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_close_button()
```

</details>
