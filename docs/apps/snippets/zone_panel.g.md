---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `zone_panel.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ColorItemDelegate`](#%EF%B8%8F-class-coloritemdelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
- [🏛️ Class `ZonePanel`](#%EF%B8%8F-class-zonepanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `focus_filter`](#%EF%B8%8F-method-focus_filter)
  - [⚙️ Method `item_at`](#%EF%B8%8F-method-item_at)
  - [⚙️ Method `set_items`](#%EF%B8%8F-method-set_items)
  - [⚙️ Method `set_sort_state`](#%EF%B8%8F-method-set_sort_state)
- [🔧 Function `chip_border_color`](#-function-chip_border_color)
- [🔧 Function `color_hex_label`](#-function-color_hex_label)

</details>

## 🏛️ Class `ColorItemDelegate`

```python
class ColorItemDelegate(QStyledItemDelegate)
```

Paint a rounded color chip, then `: description`.

<details>
<summary>Code:</summary>

```python
class ColorItemDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw the selection, hex chip, and optional hint."""
        self.initStyleOption(option, index)
        painter.save()
        widget = option.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        hex_value = color_hex_label(str(index.data(_COLOR_ROLE) or ""))
        color = QColor(hex_value) if hex_value else QColor("#ffffff")
        if not color.isValid():
            color = QColor("#ffffff")
            hex_value = hex_value or "#ffffff"

        snippet = index.data(_ITEM_ROLE)
        hint = snippet.hint.strip() if snippet is not None and snippet.hint else ""
        metrics = option.fontMetrics
        chip_width = metrics.horizontalAdvance(hex_value) + _CHIP_PADDING_X * 2
        chip_height = metrics.height() + _CHIP_PADDING_Y * 2
        chip_y = option.rect.y() + (option.rect.height() - chip_height) // 2
        chip_rect = QRect(option.rect.x() + _CHIP_ROW_MARGIN, chip_y, chip_width, chip_height)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setBrush(color)
        painter.setPen(QPen(chip_border_color(color), 1))
        painter.drawRoundedRect(chip_rect.adjusted(0, 0, -1, -1), _CHIP_RADIUS, _CHIP_RADIUS)
        text_color = QColor("#122a3a") if color.lightness() > _LIGHT_TEXT_THRESHOLD else QColor("#ffffff")
        painter.setPen(text_color)
        painter.drawText(chip_rect, Qt.AlignmentFlag.AlignCenter, hex_value)

        if hint:
            desc_x = chip_rect.right() + _CHIP_GAP
            desc_rect = QRect(
                desc_x,
                option.rect.y(),
                max(0, option.rect.right() - desc_x - _CHIP_ROW_MARGIN),
                option.rect.height(),
            )
            painter.setPen(option.palette.color(option.palette.ColorRole.Text))
            painter.drawText(desc_rect, Qt.AlignmentFlag.AlignVCenter, f": {hint}")
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        """Keep color rows tall enough for the rounded chip."""
        hint = super().sizeHint(option, index)
        return QSize(hint.width(), max(hint.height(), _MIN_COLOR_ROW_HEIGHT))
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw the selection, hex chip, and optional hint.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.initStyleOption(option, index)
        painter.save()
        widget = option.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, widget)

        hex_value = color_hex_label(str(index.data(_COLOR_ROLE) or ""))
        color = QColor(hex_value) if hex_value else QColor("#ffffff")
        if not color.isValid():
            color = QColor("#ffffff")
            hex_value = hex_value or "#ffffff"

        snippet = index.data(_ITEM_ROLE)
        hint = snippet.hint.strip() if snippet is not None and snippet.hint else ""
        metrics = option.fontMetrics
        chip_width = metrics.horizontalAdvance(hex_value) + _CHIP_PADDING_X * 2
        chip_height = metrics.height() + _CHIP_PADDING_Y * 2
        chip_y = option.rect.y() + (option.rect.height() - chip_height) // 2
        chip_rect = QRect(option.rect.x() + _CHIP_ROW_MARGIN, chip_y, chip_width, chip_height)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setBrush(color)
        painter.setPen(QPen(chip_border_color(color), 1))
        painter.drawRoundedRect(chip_rect.adjusted(0, 0, -1, -1), _CHIP_RADIUS, _CHIP_RADIUS)
        text_color = QColor("#122a3a") if color.lightness() > _LIGHT_TEXT_THRESHOLD else QColor("#ffffff")
        painter.setPen(text_color)
        painter.drawText(chip_rect, Qt.AlignmentFlag.AlignCenter, hex_value)

        if hint:
            desc_x = chip_rect.right() + _CHIP_GAP
            desc_rect = QRect(
                desc_x,
                option.rect.y(),
                max(0, option.rect.right() - desc_x - _CHIP_ROW_MARGIN),
                option.rect.height(),
            )
            painter.setPen(option.palette.color(option.palette.ColorRole.Text))
            painter.drawText(desc_rect, Qt.AlignmentFlag.AlignVCenter, f": {hint}")
        painter.restore()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize
```

Keep color rows tall enough for the rounded chip.

<details>
<summary>Code:</summary>

```python
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        hint = super().sizeHint(option, index)
        return QSize(hint.width(), max(hint.height(), _MIN_COLOR_ROW_HEIGHT))
```

</details>

## 🏛️ Class `ZonePanel`

```python
class ZonePanel(QWidget)
```

List or grid of snippet items for one zone.

<details>
<summary>Code:</summary>

```python
class ZonePanel(QWidget):

    item_activated = Signal(object)
    add_requested = Signal()
    add_many_requested = Signal()
    edit_requested = Signal(object)
    edit_all_requested = Signal()
    delete_requested = Signal(object)
    sort_requested = Signal(str)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        zone: str,
        title: str,
        show_add: bool = False,
        show_filter: bool = False,
    ) -> None:
        """Build the zone header and list.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `zone` (`str`): Zone identifier.
        - `title` (`str`): Header label.
        - `show_add` (`bool`): Show the add button. Defaults to `False`.
        - `show_filter` (`bool`): Show the search field. Defaults to `False`.

        """
        super().__init__(parent)
        self.zone = zone
        self._items: list[SnippetItem] = []
        self._sort_buttons: dict[SortMode, QToolButton] = {}

        self._list = QListWidget(self)
        self._list.setFrameShape(QListWidget.Shape.NoFrame)
        if zone == ZONE_EMOJI:
            self._list.setViewMode(QListWidget.ViewMode.IconMode)
            self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
            self._list.setMovement(QListWidget.Movement.Static)
            self._list.setGridSize(_EMOJI_GRID)
            self._list.setIconSize(QSize(32, 32))
            self._list.setSpacing(4)
            self._list.setWordWrap(False)
        if zone == ZONE_COLOR:
            self._list.setItemDelegate(ColorItemDelegate(self._list))
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        if show_add:
            add_button = make_emoji_push_button(title, "➕")  # noqa: RUF001
            add_button.clicked.connect(self.add_requested.emit)
            header.addWidget(add_button)
        else:
            title_button = QPushButton(title)
            title_button.setFlat(True)
            title_button.setEnabled(False)
            header.addWidget(title_button)
        header.addStretch()
        for mode, emoji, tooltip in _SORT_BUTTONS:
            button = QToolButton(self)
            button.setIcon(create_emoji_icon(emoji, 18))
            button.setToolTip(tooltip)
            button.setAutoRaise(True)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, sort_mode=mode: self.sort_requested.emit(sort_mode))
            self._sort_buttons[mode] = button
            header.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(header)

        self._filter = None
        if show_filter:
            self._filter = QLineEdit(self)
            self._filter.setPlaceholderText("Filter and search…")
            self._filter.setClearButtonEnabled(True)
            self._filter.textChanged.connect(self._apply_filter)
            layout.addWidget(self._filter)

        layout.addWidget(self._list, stretch=1)

    def focus_filter(self) -> None:
        """Focus the search field when the zone has one."""
        if self._filter is not None:
            self._filter.setFocus()

    def item_at(self, pos: QPoint) -> SnippetItem | None:
        """Return the item under `pos` in list coordinates, if any."""
        item = self._list.itemAt(pos)
        if item is None:
            return None
        data = item.data(_ITEM_ROLE)
        return data if data is not None else None

    def set_items(self, items: list[SnippetItem]) -> None:
        """Replace the visible items."""
        self._items = items
        self._list.clear()
        for snippet in items:
            list_item = QListWidgetItem()
            list_item.setData(_ITEM_ROLE, snippet)
            label = display_text(snippet.value, snippet.hint, snippet.zone)
            if self.zone == ZONE_EMOJI:
                list_item.setIcon(create_emoji_icon(snippet.value, 32))
                list_item.setToolTip(snippet.value)
            elif self.zone == ZONE_COLOR:
                list_item.setData(_COLOR_ROLE, snippet.value)
                list_item.setToolTip(snippet.hint or snippet.value)
            else:
                list_item.setText(label)
                if snippet.hint:
                    list_item.setToolTip(snippet.hint)
            self._list.addItem(list_item)
        self._apply_filter()

    def set_sort_state(self, zone_sort: ZoneSort) -> None:
        """Mark the active sort button."""
        for mode, button in self._sort_buttons.items():
            button.setChecked(mode == zone_sort.mode)
            tooltip = next(tip for sort_mode, _emoji, tip in _SORT_BUTTONS if sort_mode == mode)
            if mode == zone_sort.mode and zone_sort.descending:
                button.setToolTip(f"{tooltip} (reversed)")
            else:
                button.setToolTip(tooltip)

    def _apply_filter(self) -> None:
        if self._filter is None:
            return
        query = self._filter.text()
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            snippet = item.data(_ITEM_ROLE)
            if snippet is None:
                item.setHidden(False)
                continue
            item.setHidden(not item_matches_search(snippet.value, snippet.hint, query))

    def _on_context_menu(self, pos: QPoint) -> None:
        widget = self.sender()
        if widget is self._list:
            global_pos = self._list.mapToGlobal(pos)
            snippet = self.item_at(pos)
        else:
            global_pos = self.mapToGlobal(pos)
            snippet = self.item_at(self._list.mapFrom(self, pos))

        menu = QMenu(self)
        add_emoji_action(menu, "Add item", "➕").triggered.connect(self.add_requested.emit)  # noqa: RUF001
        add_emoji_action(menu, "Add many items", "📥").triggered.connect(self.add_many_requested.emit)
        edit_action = add_emoji_action(menu, "Edit item", "✏️")
        edit_action.setEnabled(snippet is not None)
        if snippet is not None:
            edit_action.triggered.connect(lambda _checked=False, item=snippet: self.edit_requested.emit(item))
        add_emoji_action(menu, "Edit entire list", "📝").triggered.connect(self.edit_all_requested.emit)
        delete_action = add_emoji_action(menu, "Delete item", "🗑️")
        delete_action.setEnabled(snippet is not None)
        if snippet is not None:
            delete_action.triggered.connect(lambda _checked=False, item=snippet: self.delete_requested.emit(item))
        menu.popup(global_pos)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        snippet = item.data(_ITEM_ROLE)
        if snippet is not None:
            self.item_activated.emit(snippet)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, zone: str, title: str, show_add: bool = False, show_filter: bool = False) -> None
```

Build the zone header and list.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `zone` (`str`): Zone identifier.
- `title` (`str`): Header label.
- `show_add` (`bool`): Show the add button. Defaults to `False`.
- `show_filter` (`bool`): Show the search field. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        zone: str,
        title: str,
        show_add: bool = False,
        show_filter: bool = False,
    ) -> None:
        super().__init__(parent)
        self.zone = zone
        self._items: list[SnippetItem] = []
        self._sort_buttons: dict[SortMode, QToolButton] = {}

        self._list = QListWidget(self)
        self._list.setFrameShape(QListWidget.Shape.NoFrame)
        if zone == ZONE_EMOJI:
            self._list.setViewMode(QListWidget.ViewMode.IconMode)
            self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
            self._list.setMovement(QListWidget.Movement.Static)
            self._list.setGridSize(_EMOJI_GRID)
            self._list.setIconSize(QSize(32, 32))
            self._list.setSpacing(4)
            self._list.setWordWrap(False)
        if zone == ZONE_COLOR:
            self._list.setItemDelegate(ColorItemDelegate(self._list))
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        if show_add:
            add_button = make_emoji_push_button(title, "➕")  # noqa: RUF001
            add_button.clicked.connect(self.add_requested.emit)
            header.addWidget(add_button)
        else:
            title_button = QPushButton(title)
            title_button.setFlat(True)
            title_button.setEnabled(False)
            header.addWidget(title_button)
        header.addStretch()
        for mode, emoji, tooltip in _SORT_BUTTONS:
            button = QToolButton(self)
            button.setIcon(create_emoji_icon(emoji, 18))
            button.setToolTip(tooltip)
            button.setAutoRaise(True)
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, sort_mode=mode: self.sort_requested.emit(sort_mode))
            self._sort_buttons[mode] = button
            header.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(header)

        self._filter = None
        if show_filter:
            self._filter = QLineEdit(self)
            self._filter.setPlaceholderText("Filter and search…")
            self._filter.setClearButtonEnabled(True)
            self._filter.textChanged.connect(self._apply_filter)
            layout.addWidget(self._filter)

        layout.addWidget(self._list, stretch=1)
```

</details>

### ⚙️ Method `focus_filter`

```python
def focus_filter(self) -> None
```

Focus the search field when the zone has one.

<details>
<summary>Code:</summary>

```python
def focus_filter(self) -> None:
        if self._filter is not None:
            self._filter.setFocus()
```

</details>

### ⚙️ Method `item_at`

```python
def item_at(self, pos: QPoint) -> SnippetItem | None
```

Return the item under `pos` in list coordinates, if any.

<details>
<summary>Code:</summary>

```python
def item_at(self, pos: QPoint) -> SnippetItem | None:
        item = self._list.itemAt(pos)
        if item is None:
            return None
        data = item.data(_ITEM_ROLE)
        return data if data is not None else None
```

</details>

### ⚙️ Method `set_items`

```python
def set_items(self, items: list[SnippetItem]) -> None
```

Replace the visible items.

<details>
<summary>Code:</summary>

```python
def set_items(self, items: list[SnippetItem]) -> None:
        self._items = items
        self._list.clear()
        for snippet in items:
            list_item = QListWidgetItem()
            list_item.setData(_ITEM_ROLE, snippet)
            label = display_text(snippet.value, snippet.hint, snippet.zone)
            if self.zone == ZONE_EMOJI:
                list_item.setIcon(create_emoji_icon(snippet.value, 32))
                list_item.setToolTip(snippet.value)
            elif self.zone == ZONE_COLOR:
                list_item.setData(_COLOR_ROLE, snippet.value)
                list_item.setToolTip(snippet.hint or snippet.value)
            else:
                list_item.setText(label)
                if snippet.hint:
                    list_item.setToolTip(snippet.hint)
            self._list.addItem(list_item)
        self._apply_filter()
```

</details>

### ⚙️ Method `set_sort_state`

```python
def set_sort_state(self, zone_sort: ZoneSort) -> None
```

Mark the active sort button.

<details>
<summary>Code:</summary>

```python
def set_sort_state(self, zone_sort: ZoneSort) -> None:
        for mode, button in self._sort_buttons.items():
            button.setChecked(mode == zone_sort.mode)
            tooltip = next(tip for sort_mode, _emoji, tip in _SORT_BUTTONS if sort_mode == mode)
            if mode == zone_sort.mode and zone_sort.descending:
                button.setToolTip(f"{tooltip} (reversed)")
            else:
                button.setToolTip(tooltip)
```

</details>

## 🔧 Function `chip_border_color`

```python
def chip_border_color(color: QColor) -> QColor
```

Return a 1 px border color darker than the chip fill.

<details>
<summary>Code:</summary>

```python
def chip_border_color(color: QColor) -> QColor:
    return color.darker(_CHIP_BORDER_DARKER)
```

</details>

## 🔧 Function `color_hex_label`

```python
def color_hex_label(value: str) -> str
```

Return the hex text for a color chip, without surrounding brackets.

<details>
<summary>Code:</summary>

```python
def color_hex_label(value: str) -> str:
    text = value.strip()
    if text.startswith("[") and text.endswith("]") and len(text) >= 2:
        return text[1:-1].strip()
    return text
```

</details>
