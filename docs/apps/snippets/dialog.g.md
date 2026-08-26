---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SnippetsDialog`](#%EF%B8%8F-class-snippetsdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `nativeEvent`](#%EF%B8%8F-method-nativeevent)
  - [⚙️ Method `present`](#%EF%B8%8F-method-present)
  - [⚙️ Method `reload_all`](#%EF%B8%8F-method-reload_all)
  - [⚙️ Method `toggle (classmethod)`](#%EF%B8%8F-method-toggle-classmethod)

</details>

## 🏛️ Class `SnippetsDialog`

```python
class SnippetsDialog(QDialog)
```

Resizable always-on-top window for quick text paste.

<details>
<summary>Code:</summary>

```python
class SnippetsDialog(QDialog):

    _instance: ClassVar[SnippetsDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the overlay and open the snippets database."""
        super().__init__(parent)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._dragging = False
        self._drag_position = QPoint()
        self._saved_clipboard = None
        self.db_manager: database_manager.DatabaseManager | None = None

        apply_opaque_white(self)
        self.setObjectName("snippetsDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_DIALOG_BORDER_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)
        self._build_header()
        self._build_body()
        self._build_resize_row()
        self.setMouseTracking(True)
        self._init_database()
        self.reload_all()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the overlay instead of destroying it."""
        event.ignore()
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Start window drag from the title."""
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
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Move the overlay while dragging from the background."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging from empty chrome."""
        if event.button() == Qt.MouseButton.LeftButton:
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

    def present(self) -> None:
        """Show and focus the overlay."""
        self.reload_all()
        self.show()
        self.raise_()
        self.activateWindow()
        self._phrases.focus_filter()

    def reload_all(self) -> None:
        """Reload every zone from the database."""
        if self.db_manager is None:
            return
        for zone, panel in self._panels.items():
            self._reload_zone(zone, panel)

    @classmethod
    def toggle(cls, parent: QWidget | None = None) -> None:
        """Show or hide the singleton overlay."""
        if cls._instance is not None and isValid(cls._instance):
            if cls._instance.isVisible():
                cls._instance.hide()
                return
            cls._instance.present()
            return
        dialog = cls(parent)
        cls._instance = dialog
        dialog.present()

    def _add_item(self, zone: str) -> None:
        dialog = ItemEditDialog(self, title=f"Add {_ZONE_TITLES[zone].lower()}", zone=zone)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        value, hint = dialog.values()
        if not value or self.db_manager is None:
            return
        self.db_manager.add_item(zone, value, hint)
        self._reload_zone(zone, self._panels[zone])

    def _add_many(self, zone: str) -> None:
        dialog = TextInputDialog(
            self,
            title=f"Add many {_ZONE_TITLES[zone].lower()}",
            description="One item per line. Symbols and colors use `value | hint`.",
            placeholder="Item",
            min_height=320,
        )
        apply_mono_font(dialog.text_edit)
        if dialog.exec() != QDialog.DialogCode.Accepted or self.db_manager is None:
            return
        items = parse_bulk_lines(dialog.get_text() or "", zone)
        if not items:
            return
        self.db_manager.add_items(zone, items)
        self._reload_zone(zone, self._panels[zone])

    def _build_body(self) -> None:
        self._phrases = ZonePanel(self, zone=ZONE_PHRASE, title="Add phrase", show_add=True, show_filter=True)
        self._emoji = ZonePanel(self, zone=ZONE_EMOJI, title="Add emoji", show_add=True)
        self._symbols = ZonePanel(self, zone=ZONE_SYMBOL, title="Add symbol", show_add=True)
        self._colors = ZonePanel(self, zone=ZONE_COLOR, title="Add color", show_add=True)
        self._panels = {
            ZONE_PHRASE: self._phrases,
            ZONE_EMOJI: self._emoji,
            ZONE_SYMBOL: self._symbols,
            ZONE_COLOR: self._colors,
        }
        for panel in self._panels.values():
            panel.item_activated.connect(self._paste_item)
            panel.add_requested.connect(lambda zone_panel=panel: self._add_item(zone_panel.zone))
            panel.add_many_requested.connect(lambda zone_panel=panel: self._add_many(zone_panel.zone))
            panel.edit_requested.connect(self._edit_item)
            panel.edit_all_requested.connect(lambda zone_panel=panel: self._edit_all(zone_panel.zone))
            panel.delete_requested.connect(self._delete_item)
            panel.sort_requested.connect(lambda mode, zone_panel=panel: self._sort_zone(zone_panel.zone, mode))

        right_split = QSplitter(Qt.Orientation.Vertical, self)
        right_split.addWidget(self._emoji)
        right_split.addWidget(self._symbols)
        right_split.setStretchFactor(0, _EMOJI_SPLIT_RATIO)
        right_split.setStretchFactor(1, _SYMBOL_SPLIT_RATIO)
        right_split.setSizes(
            [_EMOJI_SPLIT_RATIO * _EMOJI_SYMBOL_SPLIT_UNIT, _SYMBOL_SPLIT_RATIO * _EMOJI_SYMBOL_SPLIT_UNIT],
        )

        columns = QSplitter(Qt.Orientation.Horizontal, self)
        columns.addWidget(self._phrases)
        columns.addWidget(right_split)
        columns.addWidget(self._colors)
        columns.setStretchFactor(0, 2)
        columns.setStretchFactor(1, 2)
        columns.setStretchFactor(2, 2)
        self._layout.addWidget(columns, stretch=1)

    def _build_header(self) -> None:
        title = QLabel("Quick paste")
        title_font = QFont(title.font())
        grow_qfont(title_font)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)
        title.installEventFilter(self)

        close_button = QPushButton("X")
        close_button.setFixedSize(28, 28)
        close_button.setFlat(True)
        close_button.setToolTip("Close")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)
        header_spacer.installEventFilter(self)

        header = QHBoxLayout()
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(close_button)
        self._layout.addLayout(header)

    def _build_resize_row(self) -> None:
        resize_row = QHBoxLayout()
        resize_row.addStretch()
        resize_row.addWidget(QSizeGrip(self), alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addLayout(resize_row)

    def _delete_item(self, snippet: SnippetItem) -> None:
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Delete '{snippet.value}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes or self.db_manager is None:
            return
        self.db_manager.delete_item(snippet.item_id)
        self._reload_zone(snippet.zone, self._panels[snippet.zone])

    def _edit_all(self, zone: str) -> None:
        if self.db_manager is None:
            return
        items = self.db_manager.list_items(zone)
        dialog = TextInputDialog(
            self,
            title=f"Edit {_ZONE_TITLES[zone].lower()}",
            description="One item per line. Symbols and colors use `value | hint`.",
            initial_text=serialize_items(items, zone),
            min_height=400,
        )
        apply_mono_font(dialog.text_edit)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parsed = parse_bulk_lines(dialog.get_text() or "", zone)
        self.db_manager.replace_zone_items(zone, parsed)
        self._reload_zone(zone, self._panels[zone])

    def _edit_item(self, snippet: SnippetItem) -> None:
        dialog = ItemEditDialog(
            self,
            title=f"Edit {_ZONE_TITLES[snippet.zone].lower()}",
            zone=snippet.zone,
            initial_value=snippet.value,
            initial_hint=snippet.hint,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted or self.db_manager is None:
            return
        value, hint = dialog.values()
        if not value:
            return
        self.db_manager.update_item(snippet.item_id, value, hint)
        self._reload_zone(snippet.zone, self._panels[snippet.zone])

    def _end_drag(self) -> None:
        self._dragging = False

    def _init_database(self) -> None:
        config = h.dev.config_load(get_config_path_str())
        raw = str(config.get("sqlite_snippets") or "").strip()
        configured = Path(raw) if raw else Path("snippets.db")
        self.db_manager = init_tracker_database(
            self,
            configured,
            "snippets",
            Path(__file__).parent / "recover.sql",
            database_manager.DatabaseManager,
            has_required_tables=lambda dm: dm.table_exists("items"),
            missing_table_label="items table",
        )
        if self.db_manager is not None:
            ensure_seed_emojis(self.db_manager)

    def _mark_used(self, item_id: int) -> None:
        if self.db_manager is not None:
            self.db_manager.mark_used(item_id)

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _paste_item(self, snippet: SnippetItem) -> None:
        self._saved_clipboard = clone_clipboard_mime()
        self.hide()
        paste_text_then_restore_clipboard(
            snippet.value,
            self._saved_clipboard,
            on_finished=lambda: self._mark_used(snippet.item_id),
        )

    def _reload_zone(self, zone: str, panel: ZonePanel) -> None:
        if self.db_manager is None:
            return
        zone_sort = self.db_manager.get_zone_sort(zone)
        items = sort_items(self.db_manager.list_items(zone), zone_sort.mode, descending=zone_sort.descending)
        panel.set_items(items)
        panel.set_sort_state(zone_sort)

    def _sort_zone(self, zone: str, mode: str) -> None:
        if self.db_manager is None:
            return
        current = self.db_manager.get_zone_sort(zone)
        descending = not current.descending if current.mode == mode else False
        sort_mode: SortMode = mode if mode in {SORT_USED, SORT_ADDED, SORT_ALPHA} else SORT_ALPHA
        self.db_manager.set_zone_sort(zone, sort_mode, descending=descending)
        self._reload_zone(zone, self._panels[zone])

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Build the overlay and open the snippets database.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._dragging = False
        self._drag_position = QPoint()
        self._saved_clipboard = None
        self.db_manager: database_manager.DatabaseManager | None = None

        apply_opaque_white(self)
        self.setObjectName("snippetsDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_DIALOG_BORDER_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)
        self._build_header()
        self._build_body()
        self._build_resize_row()
        self.setMouseTracking(True)
        self._init_database()
        self.reload_all()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Hide the overlay instead of destroying it.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        event.ignore()
        self.hide()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Start window drag from the title.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
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
        return super().eventFilter(watched, event)
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

Move the overlay while dragging from the background.

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

Start dragging from empty chrome.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
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

### ⚙️ Method `present`

```python
def present(self) -> None
```

Show and focus the overlay.

<details>
<summary>Code:</summary>

```python
def present(self) -> None:
        self.reload_all()
        self.show()
        self.raise_()
        self.activateWindow()
        self._phrases.focus_filter()
```

</details>

### ⚙️ Method `reload_all`

```python
def reload_all(self) -> None
```

Reload every zone from the database.

<details>
<summary>Code:</summary>

```python
def reload_all(self) -> None:
        if self.db_manager is None:
            return
        for zone, panel in self._panels.items():
            self._reload_zone(zone, panel)
```

</details>

### ⚙️ Method `toggle (classmethod)`

```python
def toggle(cls, parent: QWidget | None = None) -> None
```

Show or hide the singleton overlay.

<details>
<summary>Code:</summary>

```python
def toggle(cls, parent: QWidget | None = None) -> None:
        if cls._instance is not None and isValid(cls._instance):
            if cls._instance.isVisible():
                cls._instance.hide()
                return
            cls._instance.present()
            return
        dialog = cls(parent)
        cls._instance = dialog
        dialog.present()
```

</details>
