---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HotkeyCaptureDialog`](#️-class-hotkeycapturedialog)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `_save`](#️-method-_save)
- [🏛️ Class `QuickLauncherDialog`](#️-class-quicklauncherdialog)
  - [⚙️ Method `__init__`](#️-method-__init__-1)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent-1)
  - [⚙️ Method `present`](#️-method-present)
  - [⚙️ Method `set_action_classes`](#️-method-set_action_classes)
  - [⚙️ Method `toggle`](#️-method-toggle)
  - [⚙️ Method `update_session`](#️-method-update_session)
  - [⚙️ Method `_center_on_screen`](#️-method-_center_on_screen)
  - [⚙️ Method `_on_item_clicked`](#️-method-_on_item_clicked)
  - [⚙️ Method `_run_action`](#️-method-_run_action)
- [🔧 Function `_action_icon`](#-function-_action_icon)
- [🔧 Function `_configure_action_card_grid`](#-function-_configure_action_card_grid)

</details>

## 🏛️ Class `HotkeyCaptureDialog`

```python
class HotkeyCaptureDialog(QDialog)
```

Capture a keyboard shortcut for the quick launcher global hotkey.

<details>
<summary>Code:</summary>

```python
class HotkeyCaptureDialog(QDialog):

    hotkey_captured = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the hotkey capture dialog."""
        super().__init__(parent)
        self.setWindowTitle("Quick launcher hotkey")
        self.setModal(True)
        self.setMinimumWidth(420)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Press the key combination for the quick launcher.\n"
                "It will work globally while Harrix Swiss Knife is running in the tray.",
            ),
        )
        self._preview = QLabel("Waiting for keys…")
        preview_font = QFont(self._preview.font())
        preview_font.setPointSize(preview_font.pointSize() + 2)
        preview_font.setBold(True)
        self._preview.setFont(preview_font)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._preview)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Save")
        save_button.setDefault(True)
        save_button.clicked.connect(self._save)
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        layout.addLayout(buttons)

        self._captured_hotkey = ""

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Capture modifier + key and preview the portable hotkey string."""
        key = event.key()
        if key in {Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            super().keyPressEvent(event)
            return

        modifiers = event.modifiers() & Qt.KeyboardModifier.KeyboardModifierMask
        if key in {
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
            Qt.Key.Key_AltGr,
        }:
            self._preview.setText("Press a key with modifiers (Ctrl, Alt, Shift, Win)…")
            event.accept()
            return

        if modifiers == Qt.KeyboardModifier.NoModifier:
            self._preview.setText("Add at least one modifier (Ctrl, Alt, Shift, or Win)…")
            event.accept()
            return

        self._captured_hotkey = hotkey_string_from_event(key, modifiers)
        self._preview.setText(self._captured_hotkey)
        event.accept()

    def _save(self) -> None:
        if not self._captured_hotkey.strip():
            self._preview.setText("Press a key combination first.")
            return
        self.hotkey_captured.emit(self._captured_hotkey)
        self.accept()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the hotkey capture dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Quick launcher hotkey")
        self.setModal(True)
        self.setMinimumWidth(420)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Press the key combination for the quick launcher.\n"
                "It will work globally while Harrix Swiss Knife is running in the tray.",
            ),
        )
        self._preview = QLabel("Waiting for keys…")
        preview_font = QFont(self._preview.font())
        preview_font.setPointSize(preview_font.pointSize() + 2)
        preview_font.setBold(True)
        self._preview.setFont(preview_font)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._preview)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Save")
        save_button.setDefault(True)
        save_button.clicked.connect(self._save)
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        layout.addLayout(buttons)

        self._captured_hotkey = ""
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Capture modifier + key and preview the portable hotkey string.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        key = event.key()
        if key in {Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            super().keyPressEvent(event)
            return

        modifiers = event.modifiers() & Qt.KeyboardModifier.KeyboardModifierMask
        if key in {
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
            Qt.Key.Key_AltGr,
        }:
            self._preview.setText("Press a key with modifiers (Ctrl, Alt, Shift, Win)…")
            event.accept()
            return

        if modifiers == Qt.KeyboardModifier.NoModifier:
            self._preview.setText("Add at least one modifier (Ctrl, Alt, Shift, or Win)…")
            event.accept()
            return

        self._captured_hotkey = hotkey_string_from_event(key, modifiers)
        self._preview.setText(self._captured_hotkey)
        event.accept()
```

</details>

### ⚙️ Method `_save`

```python
def _save(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _save(self) -> None:
        if not self._captured_hotkey.strip():
            self._preview.setText("Press a key combination first.")
            return
        self.hotkey_captured.emit(self._captured_hotkey)
        self.accept()
```

</details>

## 🏛️ Class `QuickLauncherDialog`

```python
class QuickLauncherDialog(QDialog)
```

Always-on-top overlay listing quick-launcher actions.

<details>
<summary>Code:</summary>

```python
class QuickLauncherDialog(QDialog):

    _instance: ClassVar[QuickLauncherDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the quick launcher overlay dialog."""
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)

        close_button = QPushButton("X")
        close_button.setFixedSize(28, 28)
        close_button.setFlat(True)
        close_button.setToolTip("Close")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        self._cards = QListWidget(self)
        _configure_action_card_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._cards, stretch=1)

        hint = QLabel("Click a card to run · Esc or X to close")
        hint.setStyleSheet("color: palette(mid);")
        layout.addWidget(hint)

        self._center_on_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    def present(self) -> None:
        """Center, show, and focus the overlay."""
        self.resize(_OVERLAY_DEFAULT_SIZE)
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        if self._cards.count():
            self._cards.setCurrentRow(0)
            self._cards.setFocus()

    def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None:
        """Rebuild the action card grid."""
        self._action_classes = list(action_classes)
        self._cards.clear()
        for action_cls in self._action_classes:
            item = QListWidgetItem(action_cls.title, self._cards)
            item.setData(Qt.ItemDataRole.UserRole, action_cls)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            item.setIcon(_action_icon(action_cls, _CARD_ICON_SIZE))
            self._cards.addItem(item)

    @classmethod
    def toggle(
        cls,
        *,
        parent: QWidget | None,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        """Show or hide the singleton quick launcher dialog."""
        if cls._instance is None:
            cls._instance = cls(parent)
        dialog = cls._instance
        dialog.update_session(output_bus=output_bus, action_classes=action_classes)

        if dialog.isVisible():
            dialog.hide()
            return

        dialog.present()

    def update_session(
        self,
        *,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        """Refresh output bus and action list before showing."""
        self._output_bus = output_bus
        self.set_action_classes(action_classes)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.center().y() - self.height() // 3
        self.move(x, y)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._run_action(item)

    def _run_action(self, item: QListWidgetItem) -> None:
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action_cls, type):
            return

        self.hide()
        action = action_cls(output_bus=self._output_bus)
        action()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the quick launcher overlay dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)

        close_button = QPushButton("X")
        close_button.setFixedSize(28, 28)
        close_button.setFlat(True)
        close_button.setToolTip("Close")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        self._cards = QListWidget(self)
        _configure_action_card_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._cards, stretch=1)

        hint = QLabel("Click a card to run · Esc or X to close")
        hint.setStyleSheet("color: palette(mid);")
        layout.addWidget(hint)

        self._center_on_screen()
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Hide the overlay on Escape.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `present`

```python
def present(self) -> None
```

Center, show, and focus the overlay.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self.resize(_OVERLAY_DEFAULT_SIZE)
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        if self._cards.count():
            self._cards.setCurrentRow(0)
            self._cards.setFocus()
```

</details>

### ⚙️ Method `set_action_classes`

```python
def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None
```

Rebuild the action card grid.

<details>
<summary>Code:</summary>

```python
def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None:
        self._action_classes = list(action_classes)
        self._cards.clear()
        for action_cls in self._action_classes:
            item = QListWidgetItem(action_cls.title, self._cards)
            item.setData(Qt.ItemDataRole.UserRole, action_cls)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            item.setIcon(_action_icon(action_cls, _CARD_ICON_SIZE))
            self._cards.addItem(item)
```

</details>

### ⚙️ Method `toggle`

```python
def toggle(cls) -> None
```

Show or hide the singleton quick launcher dialog.

<details>
<summary>Code:</summary>

```python
def toggle(
        cls,
        *,
        parent: QWidget | None,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        if cls._instance is None:
            cls._instance = cls(parent)
        dialog = cls._instance
        dialog.update_session(output_bus=output_bus, action_classes=action_classes)

        if dialog.isVisible():
            dialog.hide()
            return

        dialog.present()
```

</details>

### ⚙️ Method `update_session`

```python
def update_session(self) -> None
```

Refresh output bus and action list before showing.

<details>
<summary>Code:</summary>

```python
def update_session(
        self,
        *,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        self._output_bus = output_bus
        self.set_action_classes(action_classes)
```

</details>

### ⚙️ Method `_center_on_screen`

```python
def _center_on_screen(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.center().y() - self.height() // 3
        self.move(x, y)
```

</details>

### ⚙️ Method `_on_item_clicked`

```python
def _on_item_clicked(self, item: QListWidgetItem) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._run_action(item)
```

</details>

### ⚙️ Method `_run_action`

```python
def _run_action(self, item: QListWidgetItem) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _run_action(self, item: QListWidgetItem) -> None:
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action_cls, type):
            return

        self.hide()
        action = action_cls(output_bus=self._output_bus)
        action()
```

</details>

## 🔧 Function `_action_icon`

```python
def _action_icon(action_cls: type[ActionBase], size: int = _CARD_ICON_SIZE) -> QIcon
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _action_icon(action_cls: type[ActionBase], size: int = _CARD_ICON_SIZE) -> QIcon:
    icon_name = getattr(action_cls, "icon", "") or ""
    if ".svg" in icon_name:
        return QIcon(f":/assets/{icon_name}")
    if icon_name:
        return create_emoji_icon(icon_name, size)
    return QIcon()
```

</details>

## 🔧 Function `_configure_action_card_grid`

```python
def _configure_action_card_grid(list_widget: QListWidget) -> None
```

Apply the same icon-card layout used by New Markdown command picker.

<details>
<summary>Code:</summary>

```python
def _configure_action_card_grid(list_widget: QListWidget) -> None:
    list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    list_widget.setMinimumHeight(_OVERLAY_DEFAULT_SIZE.height() - 140)
    list_widget.setViewMode(QListWidget.ViewMode.IconMode)
    list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
    list_widget.setMovement(QListWidget.Movement.Static)
    list_widget.setSpacing(_CARD_SPACING)
    list_widget.setIconSize(QSize(_CARD_ICON_SIZE, _CARD_ICON_SIZE))
    list_widget.setWordWrap(True)
    list_widget.setUniformItemSizes(False)
    list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    list_widget.setFrameShape(QListWidget.Shape.NoFrame)
```

</details>
