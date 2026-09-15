---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `capture_action_picker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CaptureActionPickerDialog`](#%EF%B8%8F-class-captureactionpickerdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `selected_action_name`](#%EF%B8%8F-method-selected_action_name)
- [🔧 Function `choose_capture_hotkey_action`](#-function-choose_capture_hotkey_action)

</details>

## 🏛️ Class `CaptureActionPickerDialog`

```python
class CaptureActionPickerDialog(QDialog)
```

Frameless Quick-Launcher-style picker for screenshot / record actions.

<details>
<summary>Code:</summary>

```python
class CaptureActionPickerDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the picker with the same chrome and icon cards as OnQuickLauncher."""
        super().__init__(parent)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._selected: str | None = None
        self._dragging = False
        self._drag_position = QPoint()

        apply_opaque_white(self)
        self.setObjectName("quickLauncherDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_DIALOG_BORDER_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Capture")
        title_font = QFont(title.font())
        grow_qfont(title_font)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        self._close_button = QPushButton("")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_button_icon(self._close_button, CLOSE_BUTTON_ICON, icon_size=18)
        self._close_button.clicked.connect(self.reject)

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
        configure_action_card_grid(self._cards)
        style_transparent_icon_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._cards.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._cards.customContextMenuRequested.connect(self._on_cards_context_menu)
        self._actions_section, _, actions_layout = create_command_section(title="Actions", bordered=False)
        actions_layout.addWidget(self._cards)
        self._layout.addWidget(self._actions_section, stretch=0)

        self._hint = QLabel("Hold a capture hotkey to open · Esc to close")
        self._hint.setStyleSheet("color: palette(mid);")
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self._hint, stretch=1)
        self._size_grip = QSizeGrip(self)
        footer.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self._layout.addLayout(footer)

        for draggable_widget in (title, header_spacer, self._hint):
            draggable_widget.installEventFilter(self)

        self._populate_cards()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        center_widget_on_available_screen(self)
        QTimer.singleShot(0, self._fit_to_content)

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
        """Close the picker on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
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

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Allow edge resize for this frameless window on Windows."""
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit the icon grid height when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grid_for_width)

    def selected_action_name(self) -> str | None:
        """Return the action class name chosen by the user."""
        return self._selected

    def _accept_action(self, action_cls: type[ActionBase]) -> None:
        self._selected = action_cls.__name__
        self.accept()

    def _can_start_drag_at(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        if child is None:
            return True
        return not self._is_drag_excluded_widget(child)

    def _end_drag(self) -> None:
        self._dragging = False

    def _fit_to_content(self) -> None:
        self.setMinimumHeight(_OVERLAY_MIN_SIZE.height())
        sync_action_card_grid(self._cards)
        natural = measure_icon_grid_height(self._cards)
        self._cards.setMinimumHeight(natural)
        self._cards.setMaximumHeight(natural)
        self._cards.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._cards.updateGeometry()
        self._actions_section.updateGeometry()
        self.adjustSize()
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        height = max(self.sizeHint().height(), _OVERLAY_MIN_SIZE.height())
        self.resize(width, height)
        self.setMinimumHeight(height)
        center_widget_on_available_screen(self)
        if self._cards.count():
            self._cards.setCurrentRow(0)
            self._cards.setFocus()

    def _is_drag_excluded_widget(self, widget: QWidget) -> bool:
        if widget is self._cards or self._cards.isAncestorOf(widget):
            return True
        if widget is self._close_button or self._close_button.isAncestorOf(widget):
            return True
        return widget is self._size_grip or self._size_grip.isAncestorOf(widget)

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _on_cards_context_menu(self, pos: QPoint) -> None:
        """Show the same copy name/class/path commands as OnQuickLauncher."""
        item = self._cards.itemAt(pos)
        if item is None:
            return
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action_cls, type):
            return
        show_action_class_context_menu(
            parent=self,
            global_pos=self._cards.mapToGlobal(pos),
            action_cls=action_cls,
        )

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(action_cls, type):
            self._accept_action(action_cls)

    def _populate_cards(self) -> None:
        self._cards.clear()
        for action_cls in CAPTURE_PICKER_ACTIONS:
            item = QListWidgetItem(strip_md_inline_code_markers(action_cls.title), self._cards)
            item.setData(Qt.ItemDataRole.UserRole, action_cls)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            item.setIcon(create_action_icon(action_cls, CARD_ICON_SIZE))
            self._cards.addItem(item)

    def _refit_grid_for_width(self) -> None:
        if not self.isVisible():
            return
        self.setMinimumHeight(_OVERLAY_MIN_SIZE.height())
        sync_action_card_grid(self._cards)
        natural = measure_icon_grid_height(self._cards)
        self._cards.setMinimumHeight(natural)
        self._cards.setMaximumHeight(natural)
        self._cards.updateGeometry()
        height = max(self.sizeHint().height(), _OVERLAY_MIN_SIZE.height())
        if self.height() != height:
            self.resize(self.width(), height)
            self.setMinimumHeight(height)

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the picker with the same chrome and icon cards as OnQuickLauncher.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._selected: str | None = None
        self._dragging = False
        self._drag_position = QPoint()

        apply_opaque_white(self)
        self.setObjectName("quickLauncherDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_DIALOG_BORDER_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Capture")
        title_font = QFont(title.font())
        grow_qfont(title_font)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        self._close_button = QPushButton("")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_button_icon(self._close_button, CLOSE_BUTTON_ICON, icon_size=18)
        self._close_button.clicked.connect(self.reject)

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
        configure_action_card_grid(self._cards)
        style_transparent_icon_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._cards.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._cards.customContextMenuRequested.connect(self._on_cards_context_menu)
        self._actions_section, _, actions_layout = create_command_section(title="Actions", bordered=False)
        actions_layout.addWidget(self._cards)
        self._layout.addWidget(self._actions_section, stretch=0)

        self._hint = QLabel("Hold a capture hotkey to open · Esc to close")
        self._hint.setStyleSheet("color: palette(mid);")
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self._hint, stretch=1)
        self._size_grip = QSizeGrip(self)
        footer.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self._layout.addLayout(footer)

        for draggable_widget in (title, header_spacer, self._hint):
            draggable_widget.installEventFilter(self)

        self._populate_cards()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        center_widget_on_available_screen(self)
        QTimer.singleShot(0, self._fit_to_content)
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

Close the picker on Escape.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
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

### ⚙️ Method `nativeEvent`

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]
```

Allow edge resize for this frameless window on Windows.

<details>
<summary>Code:</summary>

```python
def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Refit the icon grid height when the window width changes.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grid_for_width)
```

</details>

### ⚙️ Method `selected_action_name`

```python
def selected_action_name(self) -> str | None
```

Return the action class name chosen by the user.

<details>
<summary>Code:</summary>

```python
def selected_action_name(self) -> str | None:
        return self._selected
```

</details>

## 🔧 Function `choose_capture_hotkey_action`

```python
def choose_capture_hotkey_action(*, parent: QWidget | None = None) -> str | None
```

Show the capture-action picker and return the selected class name, or `None`.

<details>
<summary>Code:</summary>

```python
def choose_capture_hotkey_action(*, parent: QWidget | None = None) -> str | None:
    dialog = CaptureActionPickerDialog(parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_action_name()
```

</details>
