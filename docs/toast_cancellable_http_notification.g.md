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
  - [⚙️ Method `resizeEvent`](#️-method-resizeevent)
  - [⚙️ Method `_apply_close_button_icon`](#️-method-_apply_close_button_icon)
  - [⚙️ Method `_apply_compact_style`](#️-method-_apply_compact_style)
  - [⚙️ Method `_apply_default_style`](#️-method-_apply_default_style)
  - [⚙️ Method `_emit_cancel_requested`](#️-method-_emit_cancel_requested)
  - [⚙️ Method `_on_user_cancel`](#️-method-_on_user_cancel)
  - [⚙️ Method `_position_close_button`](#️-method-_position_close_button)
  - [⚙️ Method `_refresh_label_text`](#️-method-_refresh_label_text)
- [🔧 Function `_make_close_icon`](#-function-_make_close_icon)

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

### ⚙️ Method `_apply_close_button_icon`

```python
def _apply_close_button_icon(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _apply_close_button_icon(self, *, compact: bool) -> None:
        side = _COMPACT_CLOSE_BUTTON_SIDE if compact else _DEFAULT_CLOSE_BUTTON_SIDE
        self._close_button.setFixedSize(side, side)
        self._close_button.setIconSize(QSize(side, side))
        self._close_button.setIcon(_make_close_icon(side))
```

</details>

### ⚙️ Method `_apply_compact_style`

```python
def _apply_compact_style(self) -> None
```

Apply compact styling to the label and close button.

<details>
<summary>Code:</summary>

```python
def _apply_compact_style(self) -> None:
        super()._apply_compact_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(_COMPACT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=True)
        self._position_close_button()
        self._refresh_label_text()
```

</details>

### ⚙️ Method `_apply_default_style`

```python
def _apply_default_style(self) -> None
```

Apply default styling to the label and close button.

<details>
<summary>Code:</summary>

```python
def _apply_default_style(self) -> None:
        super()._apply_default_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(_DEFAULT_CLOSE_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._position_close_button()
        self._refresh_label_text()
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

Handle close button click or Escape key.

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

### ⚙️ Method `_position_close_button`

```python
def _position_close_button(self) -> None
```

Place the close button at the top-right corner of the message label.

<details>
<summary>Code:</summary>

```python
def _position_close_button(self) -> None:
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

## 🔧 Function `_make_close_icon`

```python
def _make_close_icon(side: int) -> QIcon
```

Render a centered close symbol for the given button side length.

<details>
<summary>Code:</summary>

```python
def _make_close_icon(side: int) -> QIcon:
    pixmap = QPixmap(side, side)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = painter.font()
    font.setPixelSize(max(10, int(side * 0.72)))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, _CLOSE_SYMBOL)
    painter.end()
    return QIcon(pixmap)
```

</details>
