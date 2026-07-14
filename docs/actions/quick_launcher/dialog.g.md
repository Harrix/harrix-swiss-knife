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
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent-1)
  - [⚙️ Method `present`](#️-method-present)
  - [⚙️ Method `resizeEvent`](#️-method-resizeevent)
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

Resizable always-on-top window listing quick-launcher actions.

<details>
<summary>Code:</summary>

```python
class QuickLauncherDialog(QDialog):

    _instance: ClassVar[QuickLauncherDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the quick launcher dialog."""
        super().__init__(parent)
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowTitle("Quick launcher")
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)

        self._close_button = QPushButton("X")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.clicked.connect(self.hide)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(self._close_button)
        self._layout.addLayout(header)

        self._cards = QListWidget(self)
        configure_action_card_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._layout.addWidget(self._cards, stretch=1)

        self._markdown_section_label = QLabel("New Markdown")
        section_font = QFont(self._markdown_section_label.font())
        section_font.setBold(True)
        self._markdown_section_label.setFont(section_font)
        self._layout.addWidget(self._markdown_section_label)

        self._markdown_cards = QListWidget(self)
        configure_action_card_grid(self._markdown_cards)
        self._markdown_cards.itemClicked.connect(self._on_markdown_item_clicked)
        self._layout.addWidget(self._markdown_cards, stretch=1)

        self._hint = QLabel(self)
        self._hint.setStyleSheet("color: palette(mid);")
        self._layout.addWidget(self._hint)
        self._update_hint()

        self._apply_split_layout(enabled=False)
        self._center_on_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    def present(self) -> None:
        """Show and focus the overlay."""
        self._update_hint()
        self._retarget_to_active_modal_parent()
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.resize(width, _OVERLAY_DEFAULT_SIZE.height())
        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self._present_after_show)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reflow icon grids when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grids_for_width)

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
        QTimer.singleShot(0, self._fit_to_content)

    def _apply_split_layout(self, *, enabled: bool) -> None:
        """Show or hide the markdown panel."""
        self._markdown_section_label.setVisible(enabled)
        self._markdown_cards.setVisible(enabled)
        configure_action_card_grid(self._cards)
        if enabled:
            configure_action_card_grid(self._markdown_cards)
        self._layout.setStretch(self._layout.indexOf(self._cards), 1)
        self._layout.setStretch(self._layout.indexOf(self._markdown_cards), 1 if enabled else 0)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.center().y() - self.height() // 3
        self.move(x, y)

    def _fit_to_content(self) -> None:
        """Resize the window to fit all cards when screen height allows."""
        split = self._markdown_cards.isVisible()
        cards_natural = _measure_card_grid_height(self._cards)
        markdown_natural = _measure_card_grid_height(self._markdown_cards) if split else 0
        markdown_label_height = self._markdown_section_label.sizeHint().height() if split else 0

        chrome_height = _layout_vertical_chrome(self._layout, self._hint)
        spacing_total = _layout_spacing_total(self._layout, split=split)
        grids_natural = cards_natural + markdown_label_height + markdown_natural
        content_height = chrome_height + spacing_total + grids_natural

        screen = QApplication.primaryScreen()
        screen_max_height = screen.availableGeometry().height() if screen is not None else content_height
        target_height = min(content_height, screen_max_height)
        target_height = max(target_height, _OVERLAY_MIN_SIZE.height())

        available_for_grids = target_height - chrome_height - spacing_total - markdown_label_height
        if grids_natural <= available_for_grids:
            _apply_card_grid_height(self._cards, natural=cards_natural, allocated=cards_natural)
            if split:
                _apply_card_grid_height(
                    self._markdown_cards,
                    natural=markdown_natural,
                    allocated=markdown_natural,
                )
        elif split and grids_natural > 0:
            cards_allocated = max(120, int(available_for_grids * cards_natural / grids_natural))
            markdown_allocated = max(120, available_for_grids - cards_allocated)
            _apply_card_grid_height(self._cards, natural=cards_natural, allocated=cards_allocated)
            _apply_card_grid_height(
                self._markdown_cards,
                natural=markdown_natural,
                allocated=markdown_allocated,
            )
        else:
            _apply_card_grid_height(
                self._cards,
                natural=cards_natural,
                allocated=max(120, available_for_grids),
            )

        width = max(self.width(), _OVERLAY_MIN_SIZE.width())
        self.resize(width, target_height)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._run_action(item)

    def _on_markdown_item_clicked(self, item: QListWidgetItem) -> None:
        title = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(title, str):
            return
        self.hide()
        OnNewMarkdown(output_bus=self._output_bus).execute_picker_choice(title)

    def _present_after_show(self) -> None:
        self._fit_to_content()
        self._center_on_screen()
        if self._cards.count():
            self._cards.setCurrentRow(0)
            self._cards.setFocus()

    def _refit_grids_for_width(self) -> None:
        """Update card grid minimum heights after manual resize."""
        if not self.isVisible():
            return

        cards_natural = _measure_card_grid_height(self._cards)
        _apply_card_grid_height(self._cards, natural=cards_natural, allocated=cards_natural, allow_growth=True)

        if self._markdown_cards.isVisible():
            markdown_natural = _measure_card_grid_height(self._markdown_cards)
            _apply_card_grid_height(
                self._markdown_cards,
                natural=markdown_natural,
                allocated=markdown_natural,
                allow_growth=True,
            )

    def _retarget_to_active_modal_parent(self) -> None:
        """Parent launcher to active modal dialog so it stays interactive."""
        modal_parent = QApplication.activeModalWidget()
        if modal_parent is self:
            modal_parent = None
        target_parent = modal_parent if modal_parent is not None else self._default_parent

        flags = _WINDOW_FLAGS
        if self.parentWidget() is not target_parent:
            self.setParent(target_parent, flags)
        else:
            self.setWindowFlags(flags)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowTitle("Quick launcher")

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

    def _update_hint(self) -> None:
        hint_parts = ["Click a card to run", "Esc or X to close"]
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

Build the quick launcher dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowTitle("Quick launcher")
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)

        self._close_button = QPushButton("X")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.clicked.connect(self.hide)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(self._close_button)
        self._layout.addLayout(header)

        self._cards = QListWidget(self)
        configure_action_card_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._layout.addWidget(self._cards, stretch=1)

        self._markdown_section_label = QLabel("New Markdown")
        section_font = QFont(self._markdown_section_label.font())
        section_font.setBold(True)
        self._markdown_section_label.setFont(section_font)
        self._layout.addWidget(self._markdown_section_label)

        self._markdown_cards = QListWidget(self)
        configure_action_card_grid(self._markdown_cards)
        self._markdown_cards.itemClicked.connect(self._on_markdown_item_clicked)
        self._layout.addWidget(self._markdown_cards, stretch=1)

        self._hint = QLabel(self)
        self._hint.setStyleSheet("color: palette(mid);")
        self._layout.addWidget(self._hint)
        self._update_hint()

        self._apply_split_layout(enabled=False)
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

Show and focus the overlay.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self._update_hint()
        self._retarget_to_active_modal_parent()
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.resize(width, _OVERLAY_DEFAULT_SIZE.height())
        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self._present_after_show)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reflow icon grids when the window width changes.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grids_for_width)
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
        QTimer.singleShot(0, self._fit_to_content)
```

</details>
