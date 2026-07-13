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
- [🏛️ Class `QuickLauncherDialog`](#️-class-quicklauncherdialog)
  - [⚙️ Method `__init__`](#️-method-__init__-1)
  - [⚙️ Method `eventFilter`](#️-method-eventfilter)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent-1)
  - [⚙️ Method `mouseMoveEvent`](#️-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#️-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#️-method-mousereleaseevent)
  - [⚙️ Method `present`](#️-method-present)
  - [⚙️ Method `set_action_classes`](#️-method-set_action_classes)
  - [⚙️ Method `toggle`](#️-method-toggle)
  - [⚙️ Method `update_session`](#️-method-update_session)

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
        cancel_button = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        cancel_button.clicked.connect(self.reject)
        save_button = make_emoji_push_button("Save", SAVE_BUTTON_EMOJI)
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
        cancel_button = make_emoji_push_button("Cancel", CANCEL_BUTTON_EMOJI)
        cancel_button.clicked.connect(self.reject)
        save_button = make_emoji_push_button("Save", SAVE_BUTTON_EMOJI)
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
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []
        self._dragging = False
        self._drag_position = QPoint()

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        self._close_button = QPushButton("X")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.clicked.connect(self.hide)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(self._close_button)
        self._layout.addLayout(header)

        self._cards = QListWidget(self)
        configure_action_card_grid(self._cards, min_height=_card_grid_min_height(split=False))
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._layout.addWidget(self._cards, stretch=1)

        self._markdown_section_label = QLabel("New Markdown")
        section_font = QFont(self._markdown_section_label.font())
        section_font.setBold(True)
        self._markdown_section_label.setFont(section_font)
        self._markdown_section_label.setCursor(Qt.CursorShape.OpenHandCursor)
        self._layout.addWidget(self._markdown_section_label)

        self._markdown_cards = QListWidget(self)
        configure_action_card_grid(self._markdown_cards, min_height=_card_grid_min_height(split=True))
        self._markdown_cards.itemClicked.connect(self._on_markdown_item_clicked)
        self._layout.addWidget(self._markdown_cards, stretch=1)

        self._hint = QLabel(self)
        self._hint.setStyleSheet("color: palette(mid);")
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)
        self._layout.addWidget(self._hint)
        self._update_hint()

        for draggable_widget in (title, header_spacer, self._hint, self._markdown_section_label):
            draggable_widget.installEventFilter(self)

        self._apply_split_layout(enabled=False)

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._center_on_screen()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Start window drag from passive header and hint widgets."""
        if isinstance(watched, QWidget) and self._is_drag_excluded_widget(watched):
            return False

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._start_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and isinstance(event, QMouseEvent)
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._move_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._end_drag()
            return True

        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Move the overlay while dragging from dialog margins."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging from dialog margins and background."""
        if event.button() == Qt.MouseButton.LeftButton and self._can_start_drag_at(event.position().toPoint()):
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stop dragging the overlay."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def present(self) -> None:
        """Show and focus the overlay."""
        self._update_hint()
        self._retarget_to_active_modal_parent()
        self.resize(_OVERLAY_DEFAULT_SIZE)
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
            item.setIcon(_action_icon(action_cls, CARD_ICON_SIZE))
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
        split_markdown = load_quick_launcher_markdown_in_panel()
        self._apply_split_layout(enabled=split_markdown)
        if split_markdown:
            choices, _action_map = OnNewMarkdown(output_bus=output_bus).build_picker_choices()
            self._set_markdown_choices(choices)
        else:
            self._markdown_cards.clear()

    def _apply_split_layout(self, *, enabled: bool) -> None:
        """Show or hide the markdown panel and adjust card grid heights."""
        self._markdown_section_label.setVisible(enabled)
        self._markdown_cards.setVisible(enabled)
        card_min_height = _card_grid_min_height(split=enabled)
        configure_action_card_grid(self._cards, min_height=card_min_height)
        if enabled:
            configure_action_card_grid(self._markdown_cards, min_height=card_min_height)
        self._layout.setStretch(self._layout.indexOf(self._cards), 1)
        self._layout.setStretch(self._layout.indexOf(self._markdown_cards), 1 if enabled else 0)

    def _can_start_drag_at(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        if child is None:
            return True
        return not self._is_drag_excluded_widget(child)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.center().y() - self.height() // 3
        self.move(x, y)

    def _end_drag(self) -> None:
        if self._dragging:
            self.releaseMouse()
        self._dragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _is_drag_excluded_widget(self, widget: QWidget) -> bool:
        if widget is self._close_button or self._close_button.isAncestorOf(widget):
            return True
        if widget is self._cards or self._cards.isAncestorOf(widget):
            return True
        return widget is self._markdown_cards or self._markdown_cards.isAncestorOf(widget)

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._run_action(item)

    def _on_markdown_item_clicked(self, item: QListWidgetItem) -> None:
        title = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(title, str):
            return
        self.hide()
        OnNewMarkdown(output_bus=self._output_bus).execute_picker_choice(title)

    def _retarget_to_active_modal_parent(self) -> None:
        """Parent launcher to active modal dialog so it stays interactive."""
        modal_parent = QApplication.activeModalWidget()
        if modal_parent is self:
            modal_parent = None
        target_parent = modal_parent if modal_parent is not None else self._default_parent

        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        if self.parentWidget() is not target_parent:
            self.setParent(target_parent, flags)
        else:
            self.setWindowFlags(flags)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)

    def _run_action(self, item: QListWidgetItem) -> None:
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action_cls, type):
            return

        self.hide()
        action = action_cls(output_bus=self._output_bus)
        action()

    def _set_markdown_choices(self, choices: list[tuple[str, str]]) -> None:
        self._markdown_cards.clear()
        for icon, title in choices:
            item = QListWidgetItem(title, self._markdown_cards)
            item.setData(Qt.ItemDataRole.UserRole, title)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            if icon:
                item.setIcon(create_emoji_icon(icon, CARD_ICON_SIZE))
            self._markdown_cards.addItem(item)

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.grabMouse()

    def _update_hint(self) -> None:
        hint_parts = ["Click a card to run", "Drag to move", "Esc or X to close"]
        hotkey = load_quick_launcher_hotkey()
        if hotkey:
            hint_parts.append(f"{hotkey} to toggle")
        self._hint.setText(" · ".join(hint_parts))
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
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []
        self._dragging = False
        self._drag_position = QPoint()

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        self._close_button = QPushButton("X")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.clicked.connect(self.hide)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(self._close_button)
        self._layout.addLayout(header)

        self._cards = QListWidget(self)
        configure_action_card_grid(self._cards, min_height=_card_grid_min_height(split=False))
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._layout.addWidget(self._cards, stretch=1)

        self._markdown_section_label = QLabel("New Markdown")
        section_font = QFont(self._markdown_section_label.font())
        section_font.setBold(True)
        self._markdown_section_label.setFont(section_font)
        self._markdown_section_label.setCursor(Qt.CursorShape.OpenHandCursor)
        self._layout.addWidget(self._markdown_section_label)

        self._markdown_cards = QListWidget(self)
        configure_action_card_grid(self._markdown_cards, min_height=_card_grid_min_height(split=True))
        self._markdown_cards.itemClicked.connect(self._on_markdown_item_clicked)
        self._layout.addWidget(self._markdown_cards, stretch=1)

        self._hint = QLabel(self)
        self._hint.setStyleSheet("color: palette(mid);")
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)
        self._layout.addWidget(self._hint)
        self._update_hint()

        for draggable_widget in (title, header_spacer, self._hint, self._markdown_section_label):
            draggable_widget.installEventFilter(self)

        self._apply_split_layout(enabled=False)

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._center_on_screen()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Start window drag from passive header and hint widgets.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QWidget) and self._is_drag_excluded_widget(watched):
            return False

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._start_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and isinstance(event, QMouseEvent)
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._move_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._end_drag()
            return True

        return False
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

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Move the overlay while dragging from dialog margins.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start dragging from dialog margins and background.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._can_start_drag_at(event.position().toPoint()):
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Stop dragging the overlay.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `present`

```python
def present(self) -> None
```

Show and focus the overlay.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self._update_hint()
        self._retarget_to_active_modal_parent()
        self.resize(_OVERLAY_DEFAULT_SIZE)
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
            item.setIcon(_action_icon(action_cls, CARD_ICON_SIZE))
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
        split_markdown = load_quick_launcher_markdown_in_panel()
        self._apply_split_layout(enabled=split_markdown)
        if split_markdown:
            choices, _action_map = OnNewMarkdown(output_bus=output_bus).build_picker_choices()
            self._set_markdown_choices(choices)
        else:
            self._markdown_cards.clear()
```

</details>
