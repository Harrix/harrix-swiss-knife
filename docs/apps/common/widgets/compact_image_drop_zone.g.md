---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `compact_image_drop_zone.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CompactImageDropZone`](#️-class-compactimagedropzone)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `eventFilter`](#️-method-eventfilter)
  - [⚙️ Method `focusInEvent`](#️-method-focusinevent)
  - [⚙️ Method `focusOutEvent`](#️-method-focusoutevent)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `mousePressEvent`](#️-method-mousepressevent)

</details>

## 🏛️ Class `CompactImageDropZone`

```python
class CompactImageDropZone(QWidget)
```

Compact zone to drop or paste an image and invoke a callback with file paths.

<details>
<summary>Code:</summary>

```python
class CompactImageDropZone(QWidget):

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_paths: Callable[[list[str]], None],
        hint_text: str = _DEFAULT_HINT,
        extra_drop_targets: Sequence[QWidget] = (),
        max_image_side: int | None = None,
    ) -> None:
        """Initialize compact image drop zone.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `on_paths` (`Callable[[list[str]], None]`): Called with image file paths on drop or paste.
        - `hint_text` (`str`): Label text shown in the drop area.
        - `extra_drop_targets` (`Sequence[QWidget]`): Additional widgets that accept image drops.
        - `max_image_side` (`int | None`): Downscale pasted clipboard images to this max side.

        """
        super().__init__(parent)
        self._on_paths = on_paths
        self._max_image_side = max_image_side
        self._hint_text = hint_text
        self.setObjectName("CompactImageDropZone")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setMinimumHeight(48)
        self._apply_focus_style(focused=False)
        self._setup_ui(hint_text)
        self._install_drop_handlers(extra_drop_targets)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Forward clicks on child widgets to this zone for focus and Ctrl+V."""
        if watched in (self._hint_label, self._paste_button) and event.type() == QEvent.Type.MouseButtonPress:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
        return super().eventFilter(watched, event)

    def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Show focused styling when the zone receives keyboard focus."""
        self._apply_focus_style(focused=True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Restore default styling when focus leaves the zone."""
        self._apply_focus_style(focused=False)
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Ctrl+V to paste image from clipboard."""
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._paste_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Focus the zone when clicked so Ctrl+V works."""
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(event)

    def _apply_focus_style(self, *, focused: bool) -> None:
        self.setStyleSheet(_FOCUSED_STYLE if focused else _NORMAL_STYLE)
        if hasattr(self, "_hint_label"):
            if focused:
                self._hint_label.setText(f"{self._hint_text}\n⌨️ Ctrl+V to paste")
                self._hint_label.setStyleSheet(_HINT_FOCUSED_STYLE)
            else:
                self._hint_label.setText(self._hint_text)
                self._hint_label.setStyleSheet(_HINT_STYLE)

    def _install_drop_handlers(self, extra_drop_targets: Sequence[QWidget]) -> None:
        targets = [self, *extra_drop_targets]
        for target in targets:
            install_url_drop_handlers(target, self._on_paths, filter_path=is_image_file_path)

    def _paste_from_clipboard(self) -> None:
        temp_path = save_clipboard_image_to_temp_file(max_image_side=self._max_image_side)
        if temp_path:
            self._on_paths([temp_path])

    def _setup_ui(self, hint_text: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(0)

        self._hint_label = QLabel(hint_text)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint_label.setStyleSheet(_HINT_STYLE)
        self._hint_label.setWordWrap(True)
        self._hint_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._hint_label.installEventFilter(self)
        layout.addWidget(self._hint_label, stretch=1)

        self._paste_button = QPushButton()
        self._paste_button.setIcon(create_emoji_icon(COPY_BUTTON_EMOJI, 18))
        self._paste_button.setFixedSize(32, 32)
        self._paste_button.setToolTip("Paste image from clipboard (Ctrl+V)")
        self._paste_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._paste_button.installEventFilter(self)
        self._paste_button.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            "QPushButton:hover { background-color: #bbdefb; border-radius: 4px; }"
        )
        self._paste_button.clicked.connect(self._paste_from_clipboard)
        layout.addWidget(self._paste_button)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize compact image drop zone.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `on_paths` (`Callable[[list[str]], None]`): Called with image file paths on drop or paste.
- `hint_text` (`str`): Label text shown in the drop area.
- `extra_drop_targets` (`Sequence[QWidget]`): Additional widgets that accept image drops.
- `max_image_side` (`int | None`): Downscale pasted clipboard images to this max side.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        on_paths: Callable[[list[str]], None],
        hint_text: str = _DEFAULT_HINT,
        extra_drop_targets: Sequence[QWidget] = (),
        max_image_side: int | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_paths = on_paths
        self._max_image_side = max_image_side
        self._hint_text = hint_text
        self.setObjectName("CompactImageDropZone")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setMinimumHeight(48)
        self._apply_focus_style(focused=False)
        self._setup_ui(hint_text)
        self._install_drop_handlers(extra_drop_targets)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Forward clicks on child widgets to this zone for focus and Ctrl+V.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched in (self._hint_label, self._paste_button) and event.type() == QEvent.Type.MouseButtonPress:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `focusInEvent`

```python
def focusInEvent(self, event: QFocusEvent) -> None
```

Show focused styling when the zone receives keyboard focus.

<details>
<summary>Code:</summary>

```python
def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        self._apply_focus_style(focused=True)
        super().focusInEvent(event)
```

</details>

### ⚙️ Method `focusOutEvent`

```python
def focusOutEvent(self, event: QFocusEvent) -> None
```

Restore default styling when focus leaves the zone.

<details>
<summary>Code:</summary>

```python
def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        self._apply_focus_style(focused=False)
        super().focusOutEvent(event)
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle Ctrl+V to paste image from clipboard.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._paste_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Focus the zone when clicked so Ctrl+V works.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(event)
```

</details>
