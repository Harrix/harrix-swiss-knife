---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_window_lightbox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppWindowLightboxDialog`](#%EF%B8%8F-class-appwindowlightboxdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `attach_content`](#%EF%B8%8F-method-attach_content)
  - [⚙️ Method `current_index (property)`](#%EF%B8%8F-method-current_index-property)
  - [⚙️ Method `empty_caption`](#%EF%B8%8F-method-empty_caption)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `finish_setup`](#%EF%B8%8F-method-finish_setup)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_caption`](#%EF%B8%8F-method-set_caption)
  - [⚙️ Method `show_item`](#%EF%B8%8F-method-show_item)
  - [⚙️ Method `show_next`](#%EF%B8%8F-method-show_next)
  - [⚙️ Method `show_previous`](#%EF%B8%8F-method-show_previous)

</details>

## 🏛️ Class `AppWindowLightboxDialog`

```python
class AppWindowLightboxDialog(QDialog)
```

Overlay with close, prev/next, backdrop swatches, and a caption.

Subclasses attach a content widget and implement `show_item`.

<details>
<summary>Code:</summary>

```python
class AppWindowLightboxDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        item_count: int = 0,
        current_index: int = 0,
    ) -> None:
        """Build chrome fitted to the owner window.

        Args:

        - `parent` (`QWidget | None`): Widget whose top-level window is covered.
        - `item_count` (`int`): Number of browsable items. Defaults to `0`.
        - `current_index` (`int`): Initial item index. Defaults to `0`.

        """
        owner = parent.window() if parent is not None else None
        super().__init__(owner)
        self._item_count = max(0, item_count)
        self._index = max(0, min(current_index, self._item_count - 1)) if self._item_count else 0
        self._content: QWidget | None = None

        qt_modality.set_owner_window_modal(self)
        self.setObjectName("appWindowLightbox")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        if owner is not None:
            owner.installEventFilter(self)
            self._fit_to_owner()
        else:
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                self.setGeometry(screen.availableGeometry())
            else:
                self.resize(1280, 720)

        self._close_button = self._make_button("", "Close")
        self._close_button.setIcon(create_emoji_icon(CLOSE_BUTTON_EMOJI, 22))
        self._close_button.clicked.connect(self.accept)
        self._previous_button = self._make_button("←", "Previous (Left arrow)")
        self._previous_button.clicked.connect(self.show_previous)
        self._next_button = self._make_button("→", "Next (Right arrow)")
        self._next_button.clicked.connect(self.show_next)

        self._black_backdrop_button = self._make_backdrop_button(color="black")
        self._black_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("black"))
        self._white_backdrop_button = self._make_backdrop_button(color="white")
        self._white_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("white"))
        self._set_backdrop_color("white")

        self._previous_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self._previous_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._previous_shortcut.activated.connect(self.show_previous)
        self._next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self._next_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._next_shortcut.activated.connect(self.show_next)

        self._caption = QLabel(self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            "color: white; background: rgba(20, 20, 20, 180);border-radius: 7px; padding: 6px 12px;"
        )

    def attach_content(self, widget: QWidget) -> None:
        """Place `widget` under the overlay chrome and close on backdrop clicks."""
        self._content = widget
        backdrop_clicked = getattr(widget, "backdrop_clicked", None)
        if backdrop_clicked is not None:
            backdrop_clicked.connect(self.accept)

    @property
    def current_index(self) -> int:
        """Current item index."""
        return self._index

    def empty_caption(self) -> str:
        """Caption when there are no items."""
        return "Nothing to display"

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Keep the overlay aligned with the owner window."""
        owner = self.parentWidget()
        if watched is owner and event.type() in {QEvent.Type.Resize, QEvent.Type.Move}:
            self._fit_to_owner()
        return super().eventFilter(watched, event)

    def finish_setup(self) -> None:
        """Size chrome and display the current item after content is attached."""
        self._position_controls()
        self._show_current()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Escape and left/right navigation."""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        if event.key() == Qt.Key.Key_Left:
            self.show_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.show_next()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep content and overlay controls aligned."""
        super().resizeEvent(event)
        self._position_controls()

    def set_caption(self, text: str) -> None:
        """Update the bottom caption."""
        self._caption.setText(text)

    def show_item(self, index: int) -> None:
        """Display the item at `index`. Subclasses must implement this."""
        msg = f"{type(self).__name__} must implement show_item"
        raise NotImplementedError(msg)

    def show_next(self) -> None:
        """Show the next item, wrapping at the end."""
        if self._item_count > 1:
            self._index = (self._index + 1) % self._item_count
            self._show_current()

    def show_previous(self) -> None:
        """Show the previous item, wrapping at the beginning."""
        if self._item_count > 1:
            self._index = (self._index - 1) % self._item_count
            self._show_current()

    def _fit_to_owner(self) -> None:
        owner = self.parentWidget()
        if owner is None:
            return
        if self.isWindow():
            top_left = owner.mapToGlobal(QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), owner.width(), owner.height())
            return
        self.setGeometry(owner.rect())

    def _make_backdrop_button(self, *, color: str) -> QPushButton:
        button = QPushButton(self)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setFixedSize(_SWATCH_SIZE, _SWATCH_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoDefault(False)
        button.setDefault(False)
        button.setToolTip("Black backdrop" if color == "black" else "White backdrop")
        border = "#888" if color == "white" else "#ccc"
        radius = _SWATCH_SIZE // 2
        button.setStyleSheet(
            f"QPushButton {{ background: {color}; border: 1px solid {border};"
            f"border-radius: {radius}px; padding: 0; }}"
            "QPushButton:checked { border: 3px solid #2f80ed; }"
        )
        return button

    def _make_button(self, text: str, tooltip: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setFixedSize(QSize(_BUTTON_SIZE, _BUTTON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoDefault(False)
        button.setDefault(False)
        button.setToolTip(tooltip)
        button.setStyleSheet(
            "QPushButton { color: white; font-size: 24px; font-weight: bold;"
            "background: rgba(40, 40, 40, 125); border: 1px solid rgba(255, 255, 255, 90);"
            "border-radius: 9px; }"
            "QPushButton:hover { background: rgba(40, 40, 40, 190); }"
        )
        button.raise_()
        return button

    def _position_controls(self) -> None:
        if self._content is not None:
            self._content.setGeometry(self.rect())
        self._black_backdrop_button.move(_SIDE_MARGIN, _SIDE_MARGIN)
        self._white_backdrop_button.move(_SIDE_MARGIN + self._black_backdrop_button.width() + 8, _SIDE_MARGIN)
        self._close_button.move(self.width() - _BUTTON_SIZE - _SIDE_MARGIN, _SIDE_MARGIN)
        center_y = (self.height() - _BUTTON_SIZE) // 2
        self._previous_button.move(_SIDE_MARGIN, center_y)
        self._next_button.move(self.width() - _BUTTON_SIZE - _SIDE_MARGIN, center_y)
        caption_width = min(640, max(240, self.width() - 240))
        self._caption.setFixedWidth(caption_width)
        self._caption.adjustSize()
        self._caption.move((self.width() - caption_width) // 2, self.height() - self._caption.height() - _SIDE_MARGIN)
        for widget in (
            self._black_backdrop_button,
            self._white_backdrop_button,
            self._close_button,
            self._previous_button,
            self._next_button,
            self._caption,
        ):
            widget.raise_()

    def _set_backdrop_color(self, color: str) -> None:
        is_black = color == "black"
        fill = "black" if is_black else "white"
        self.setStyleSheet(f"#appWindowLightbox {{ background-color: {fill}; }}")
        self._black_backdrop_button.setChecked(is_black)
        self._white_backdrop_button.setChecked(not is_black)

    def _show_current(self) -> None:
        if self._item_count <= 0:
            self.set_caption(self.empty_caption())
            self._previous_button.hide()
            self._next_button.hide()
            return
        self.show_item(self._index)
        show_navigation = self._item_count > 1
        self._previous_button.setVisible(show_navigation)
        self._next_button.setVisible(show_navigation)
        self._position_controls()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, item_count: int = 0, current_index: int = 0) -> None
```

Build chrome fitted to the owner window.

Args:

- `parent` (`QWidget | None`): Widget whose top-level window is covered.
- `item_count` (`int`): Number of browsable items. Defaults to `0`.
- [`current_index`](#%EF%B8%8F-method-current_index-property) (`int`): Initial item index. Defaults to `0`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        item_count: int = 0,
        current_index: int = 0,
    ) -> None:
        owner = parent.window() if parent is not None else None
        super().__init__(owner)
        self._item_count = max(0, item_count)
        self._index = max(0, min(current_index, self._item_count - 1)) if self._item_count else 0
        self._content: QWidget | None = None

        qt_modality.set_owner_window_modal(self)
        self.setObjectName("appWindowLightbox")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        if owner is not None:
            owner.installEventFilter(self)
            self._fit_to_owner()
        else:
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                self.setGeometry(screen.availableGeometry())
            else:
                self.resize(1280, 720)

        self._close_button = self._make_button("", "Close")
        self._close_button.setIcon(create_emoji_icon(CLOSE_BUTTON_EMOJI, 22))
        self._close_button.clicked.connect(self.accept)
        self._previous_button = self._make_button("←", "Previous (Left arrow)")
        self._previous_button.clicked.connect(self.show_previous)
        self._next_button = self._make_button("→", "Next (Right arrow)")
        self._next_button.clicked.connect(self.show_next)

        self._black_backdrop_button = self._make_backdrop_button(color="black")
        self._black_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("black"))
        self._white_backdrop_button = self._make_backdrop_button(color="white")
        self._white_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("white"))
        self._set_backdrop_color("white")

        self._previous_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self._previous_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._previous_shortcut.activated.connect(self.show_previous)
        self._next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self._next_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._next_shortcut.activated.connect(self.show_next)

        self._caption = QLabel(self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            "color: white; background: rgba(20, 20, 20, 180);border-radius: 7px; padding: 6px 12px;"
        )
```

</details>

### ⚙️ Method `attach_content`

```python
def attach_content(self, widget: QWidget) -> None
```

Place `widget` under the overlay chrome and close on backdrop clicks.

<details>
<summary>Code:</summary>

```python
def attach_content(self, widget: QWidget) -> None:
        self._content = widget
        backdrop_clicked = getattr(widget, "backdrop_clicked", None)
        if backdrop_clicked is not None:
            backdrop_clicked.connect(self.accept)
```

</details>

### ⚙️ Method `current_index (property)`

```python
def current_index(self) -> int
```

Current item index.

<details>
<summary>Code:</summary>

```python
def current_index(self) -> int:
        return self._index
```

</details>

### ⚙️ Method `empty_caption`

```python
def empty_caption(self) -> str
```

Caption when there are no items.

<details>
<summary>Code:</summary>

```python
def empty_caption(self) -> str:
        return "Nothing to display"
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Keep the overlay aligned with the owner window.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        owner = self.parentWidget()
        if watched is owner and event.type() in {QEvent.Type.Resize, QEvent.Type.Move}:
            self._fit_to_owner()
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `finish_setup`

```python
def finish_setup(self) -> None
```

Size chrome and display the current item after content is attached.

<details>
<summary>Code:</summary>

```python
def finish_setup(self) -> None:
        self._position_controls()
        self._show_current()
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle Escape and left/right navigation.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        if event.key() == Qt.Key.Key_Left:
            self.show_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.show_next()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep content and overlay controls aligned.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_controls()
```

</details>

### ⚙️ Method `set_caption`

```python
def set_caption(self, text: str) -> None
```

Update the bottom caption.

<details>
<summary>Code:</summary>

```python
def set_caption(self, text: str) -> None:
        self._caption.setText(text)
```

</details>

### ⚙️ Method `show_item`

```python
def show_item(self, index: int) -> None
```

Display the item at `index`. Subclasses must implement this.

<details>
<summary>Code:</summary>

```python
def show_item(self, index: int) -> None:
        msg = f"{type(self).__name__} must implement show_item"
        raise NotImplementedError(msg)
```

</details>

### ⚙️ Method `show_next`

```python
def show_next(self) -> None
```

Show the next item, wrapping at the end.

<details>
<summary>Code:</summary>

```python
def show_next(self) -> None:
        if self._item_count > 1:
            self._index = (self._index + 1) % self._item_count
            self._show_current()
```

</details>

### ⚙️ Method `show_previous`

```python
def show_previous(self) -> None
```

Show the previous item, wrapping at the beginning.

<details>
<summary>Code:</summary>

```python
def show_previous(self) -> None:
        if self._item_count > 1:
            self._index = (self._index - 1) % self._item_count
            self._show_current()
```

</details>
