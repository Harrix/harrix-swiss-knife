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
  - [⚙️ Method `present`](#%EF%B8%8F-method-present)
  - [⚙️ Method `reposition_action_buttons`](#%EF%B8%8F-method-reposition_action_buttons)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)

</details>

## 🏛️ Class `ToastCancellableHttpNotification`

```python
class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification)
```

Toast with elapsed timer and user-initiated request cancellation.

Shown as `WindowModal` so only the owner window hierarchy is blocked (sibling
apps in the same process stay interactive). Prefer passing the active modal
dialog as `parent` so Escape and the close button still work during flows
like New Markdown → Fill with AI; `present()` focuses the toast.

Attributes:

- `cancel_requested` (`Signal`): Emitted once when the user cancels the request.
- `completed` (`bool`): `True` after `mark_completed()` was called.

<details>
<summary>Code:</summary>

```python
class ToastCancellableHttpNotification(toast_countdown_notification.ToastCountdownNotification):

    cancel_requested: Signal = Signal()

    def __init__(
        self,
        message: str = "Request in progress…",
        parent: QWidget | None = None,
        *,
        owner_modal: bool = True,
    ) -> None:
        """Initialize cancellable HTTP toast with countdown and close control.

        Args:

        - `message` (`str`): Toast text. Defaults to `Request in progress…`.
        - `parent` (`QWidget | None`): Owner widget. Defaults to `None`.
        - `owner_modal` (`bool`): Block the owner window while the request runs.
          Defaults to `True`.

        """
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        # Must be set before show(); modality on an already-visible window is ignored.
        if owner_modal:
            qt_modality.set_owner_window_modal(self)

        self._close_button = QPushButton(self)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setFlat(True)
        self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._close_button.setToolTip("Cancel request")
        self._close_button.clicked.connect(self._on_user_cancel)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_close_button()
        self._position_collapse_button()

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

    def present(self, *, activate: bool = True, pinned: bool | None = None) -> None:
        """Show on top and take focus so Escape reaches this toast, not the parent dialog."""
        super().present(activate=activate, pinned=pinned)
        if activate:
            self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._position_close_button()
        self._position_collapse_button()

    def reposition_action_buttons(self) -> None:
        """Place close and collapse buttons after a move or resize."""
        self._position_close_button()
        super().reposition_action_buttons()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition close and collapse buttons when the toast is resized."""
        super().resizeEvent(event)
        self._position_close_button()

    def _apply_close_button_icon(self, *, compact: bool) -> None:
        side = (
            toast_notification_base.COMPACT_ACTION_BUTTON_SIDE
            if compact
            else toast_notification_base.DEFAULT_ACTION_BUTTON_SIDE
        )
        self._close_button.setFixedSize(side, side)
        self._close_button.setIconSize(QSize(side, side))
        self._close_button.setIcon(toast_notification_base.make_action_icon(side, _CLOSE_SYMBOL))

    def _apply_compact_style(self) -> None:
        """Apply compact styling to the label and close button."""
        super()._apply_compact_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(toast_notification_base.COMPACT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=True)
        self._position_close_button()
        self._position_collapse_button()
        self._refresh_label_text()

    def _apply_default_style(self) -> None:
        """Apply default styling to the label and close button."""
        super()._apply_default_style()
        if not hasattr(self, "_close_button"):
            return
        self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._position_close_button()
        self._position_collapse_button()
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
        side = self._action_button_side()
        margin = self._action_button_margin()
        self._close_button.move(
            label_geom.x() + label_geom.width() - side - margin,
            label_geom.y() + margin,
        )
        self._close_button.raise_()

    def _refresh_label_text(self) -> None:
        """Update label with message, elapsed clock, and cancel hint."""
        elapsed = toast_countdown_notification.format_elapsed_clock(self.elapsed_seconds)
        if self._is_pinned:
            self.label.setTextFormat(Qt.TextFormat.PlainText)
            self.label.setText(f"{self.message}\n{elapsed}")
        else:
            self.label.setTextFormat(Qt.TextFormat.RichText)
            self.label.setText(
                toast_notification_base.format_toast_cancel_hint_html(
                    f"{self.message}\nTime elapsed: {elapsed}",
                    _CANCEL_HINT,
                    compact=False,
                ),
            )
        previous_size = self.size()
        self.adjustSize()
        self.reposition_action_buttons()
        if self.size() != previous_size:
            self.restack_group(pinned=self.is_pinned)

    def _trailing_controls_width(self) -> int:
        """Reserve space for the cancel button to the right of collapse."""
        if not hasattr(self, "_close_button"):
            return 0
        return self._action_button_side() + toast_notification_base.ACTION_BUTTON_GAP
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, message: str = 'Request in progress…', parent: QWidget | None = None, *, owner_modal: bool = True) -> None
```

Initialize cancellable HTTP toast with countdown and close control.

Args:

- `message` (`str`): Toast text. Defaults to `Request in progress…`.
- `parent` (`QWidget | None`): Owner widget. Defaults to `None`.
- `owner_modal` (`bool`): Block the owner window while the request runs.
  Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        message: str = "Request in progress…",
        parent: QWidget | None = None,
        *,
        owner_modal: bool = True,
    ) -> None:
        super().__init__(message, parent)

        self._cancelled = False
        self._completed = False

        # Must be set before show(); modality on an already-visible window is ignored.
        if owner_modal:
            qt_modality.set_owner_window_modal(self)

        self._close_button = QPushButton(self)
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.setFlat(True)
        self._close_button.setStyleSheet(toast_notification_base.DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_close_button_icon(compact=False)
        self._close_button.setToolTip("Cancel request")
        self._close_button.clicked.connect(self._on_user_cancel)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._position_close_button()
        self._position_collapse_button()
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

### ⚙️ Method `present`

```python
def present(self, *, activate: bool = True, pinned: bool | None = None) -> None
```

Show on top and take focus so Escape reaches this toast, not the parent dialog.

<details>
<summary>Code:</summary>

```python
def present(self, *, activate: bool = True, pinned: bool | None = None) -> None:
        super().present(activate=activate, pinned=pinned)
        if activate:
            self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self._position_close_button()
        self._position_collapse_button()
```

</details>

### ⚙️ Method `reposition_action_buttons`

```python
def reposition_action_buttons(self) -> None
```

Place close and collapse buttons after a move or resize.

<details>
<summary>Code:</summary>

```python
def reposition_action_buttons(self) -> None:
        self._position_close_button()
        super().reposition_action_buttons()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reposition close and collapse buttons when the toast is resized.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_close_button()
```

</details>
