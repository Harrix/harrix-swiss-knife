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
- [🏛️ Class `HighlightItemDelegate`](#%EF%B8%8F-class-highlightitemdelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint-1)
- [🏛️ Class `IconItemDelegate`](#%EF%B8%8F-class-iconitemdelegate)
  - [⚙️ Method `paint`](#%EF%B8%8F-method-paint-2)
- [🏛️ Class `ZonePanel`](#%EF%B8%8F-class-zonepanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `activate_current_or_first`](#%EF%B8%8F-method-activate_current_or_first)
  - [⚙️ Method `clear_ai_candidates`](#%EF%B8%8F-method-clear_ai_candidates)
  - [⚙️ Method `clear_filter`](#%EF%B8%8F-method-clear_filter)
  - [⚙️ Method `current_snippet`](#%EF%B8%8F-method-current_snippet)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `filter_query`](#%EF%B8%8F-method-filter_query)
  - [⚙️ Method `item_at`](#%EF%B8%8F-method-item_at)
  - [⚙️ Method `item_matches_input`](#%EF%B8%8F-method-item_matches_input)
  - [⚙️ Method `move_visible`](#%EF%B8%8F-method-move_visible)
  - [⚙️ Method `prepare_keyboard_focus`](#%EF%B8%8F-method-prepare_keyboard_focus)
  - [⚙️ Method `refresh_ai_candidates`](#%EF%B8%8F-method-refresh_ai_candidates)
  - [⚙️ Method `reset_keyboard_session`](#%EF%B8%8F-method-reset_keyboard_session)
  - [⚙️ Method `select_row`](#%EF%B8%8F-method-select_row)
  - [⚙️ Method `set_ai_candidates`](#%EF%B8%8F-method-set_ai_candidates)
  - [⚙️ Method `set_ai_pick_enabled`](#%EF%B8%8F-method-set_ai_pick_enabled)
  - [⚙️ Method `set_ai_pick_visible`](#%EF%B8%8F-method-set_ai_pick_visible)
  - [⚙️ Method `set_filter_query`](#%EF%B8%8F-method-set_filter_query)
  - [⚙️ Method `set_input_match`](#%EF%B8%8F-method-set_input_match)
  - [⚙️ Method `set_items`](#%EF%B8%8F-method-set_items)
  - [⚙️ Method `set_sort_state`](#%EF%B8%8F-method-set_sort_state)
  - [⚙️ Method `visible_rows`](#%EF%B8%8F-method-visible_rows)
- [🔧 Function `add_sort_menu_actions`](#-function-add_sort_menu_actions)
- [🔧 Function `chip_border_color`](#-function-chip_border_color)
- [🔧 Function `color_hex_label`](#-function-color_hex_label)
- [🔧 Function `paint_snippet_highlight`](#-function-paint_snippet_highlight)

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
        matches = _item_matches_input(index, option)
        if matches or _item_is_highlighted(option):
            paint_snippet_highlight(painter, option.rect, outlined=matches)

        hex_value = strip_wrapping_brackets(str(index.data(_COLOR_ROLE) or ""))
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

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:  # noqa: N802
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
        matches = _item_matches_input(index, option)
        if matches or _item_is_highlighted(option):
            paint_snippet_highlight(painter, option.rect, outlined=matches)

        hex_value = strip_wrapping_brackets(str(index.data(_COLOR_ROLE) or ""))
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
def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:  # noqa: N802
        hint = super().sizeHint(option, index)
        return QSize(hint.width(), max(hint.height(), _MIN_COLOR_ROW_HEIGHT))
```

</details>

## 🏛️ Class `HighlightItemDelegate`

```python
class HighlightItemDelegate(QStyledItemDelegate)
```

Draw hover and selection as a flat fill so text color stays unchanged.

<details>
<summary>Code:</summary>

```python
class HighlightItemDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint a custom highlight, then the item text in the normal color."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        painter.save()
        matches = _item_matches_input(index, opt)
        if matches or _item_is_highlighted(opt):
            paint_snippet_highlight(painter, opt.rect, outlined=matches)
        opt.state &= ~_HIGHLIGHT_STATES
        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget)
            if not text_rect.isValid():
                text_rect = opt.rect.adjusted(4, 0, -4, 0)
            enabled = bool(opt.state & QStyle.StateFlag.State_Enabled)
            style.drawItemText(
                painter,
                text_rect,
                int(opt.displayAlignment),
                opt.palette,
                enabled,
                opt.text,
                QPalette.ColorRole.Text,
            )
        else:
            painter.setPen(opt.palette.color(QPalette.ColorRole.Text))
            painter.drawText(opt.rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, opt.text)
        painter.restore()
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Paint a custom highlight, then the item text in the normal color.

<details>
<summary>Code:</summary>

```python
def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        painter.save()
        matches = _item_matches_input(index, opt)
        if matches or _item_is_highlighted(opt):
            paint_snippet_highlight(painter, opt.rect, outlined=matches)
        opt.state &= ~_HIGHLIGHT_STATES
        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            text_rect = style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget)
            if not text_rect.isValid():
                text_rect = opt.rect.adjusted(4, 0, -4, 0)
            enabled = bool(opt.state & QStyle.StateFlag.State_Enabled)
            style.drawItemText(
                painter,
                text_rect,
                int(opt.displayAlignment),
                opt.palette,
                enabled,
                opt.text,
                QPalette.ColorRole.Text,
            )
        else:
            painter.setPen(opt.palette.color(QPalette.ColorRole.Text))
            painter.drawText(opt.rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, opt.text)
        painter.restore()
```

</details>

## 🏛️ Class `IconItemDelegate`

```python
class IconItemDelegate(QStyledItemDelegate)
```

Paint emoji and symbol tiles without the native Windows selection pill.

<details>
<summary>Code:</summary>

```python
class IconItemDelegate(QStyledItemDelegate):

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Draw a flat highlight and the icon, never the native selection chrome."""
        self.initStyleOption(option, index)
        painter.save()
        matches = _item_matches_input(index, option)
        if matches or _item_is_highlighted(option):
            paint_snippet_highlight(painter, option.rect, outlined=matches)
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(icon, QIcon) and not icon.isNull():
            size = (
                option.decorationSize if option.decorationSize.isValid() else QSize(_ICON_PIXEL_SIZE, _ICON_PIXEL_SIZE)
            )
            x = option.rect.x() + (option.rect.width() - size.width()) // 2
            y = option.rect.y() + (option.rect.height() - size.height()) // 2
            icon.paint(
                painter,
                QRect(x, y, size.width(), size.height()),
                Qt.AlignmentFlag.AlignCenter,
                QIcon.Mode.Normal,
            )
        painter.restore()
```

</details>

### ⚙️ Method `paint`

```python
def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None
```

Draw a flat highlight and the icon, never the native selection chrome.

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
        matches = _item_matches_input(index, option)
        if matches or _item_is_highlighted(option):
            paint_snippet_highlight(painter, option.rect, outlined=matches)
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(icon, QIcon) and not icon.isNull():
            size = (
                option.decorationSize if option.decorationSize.isValid() else QSize(_ICON_PIXEL_SIZE, _ICON_PIXEL_SIZE)
            )
            x = option.rect.x() + (option.rect.width() - size.width()) // 2
            y = option.rect.y() + (option.rect.height() - size.height()) // 2
            icon.paint(
                painter,
                QRect(x, y, size.width(), size.height()),
                Qt.AlignmentFlag.AlignCenter,
                QIcon.Mode.Normal,
            )
        painter.restore()
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
    ai_add_requested = Signal(str)
    ai_dismiss_requested = Signal()
    ai_paste_requested = Signal(str)
    ai_pick_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        zone: str,
        title: str,
    ) -> None:
        """Build the zone header and list.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `zone` (`str`): Zone identifier.
        - `title` (`str`): Header label.

        """
        super().__init__(parent)
        self.zone = zone
        self._items: list[SnippetItem] = []
        self._sort_mode: SortMode = DEFAULT_SORT_MODE
        self._sort_descending = False
        self._filter_query = ""
        self._input_match = ""
        self._remembered_id: int | None = None
        self._ai_pick_button: QToolButton | None = None
        self._ai_candidates: QWidget | None = None
        self._ai_candidates_layout: FlowLayout | None = None
        self._ai_emojis: list[str] = []

        self._list = QListWidget(self)
        self._list.setFrameShape(QListWidget.Shape.NoFrame)
        self._list.setStyleSheet(_LIST_SELECTION_STYLE)
        self._list.setMouseTracking(True)
        self._list.viewport().setMouseTracking(True)
        self._list.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        _apply_list_highlight_palette(self._list)
        self._list.installEventFilter(self)
        apply_mono_font(self._list)
        if zone in {ZONE_EMOJI, ZONE_SYMBOL}:
            self._list.setViewMode(QListWidget.ViewMode.IconMode)
            self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
            self._list.setMovement(QListWidget.Movement.Static)
            self._list.setGridSize(_ICON_GRID)
            self._list.setIconSize(QSize(_ICON_PIXEL_SIZE, _ICON_PIXEL_SIZE))
            self._list.setSpacing(_ICON_SPACING)
            self._list.setWordWrap(False)
            self._list.setItemDelegate(IconItemDelegate(self._list))
        elif zone == ZONE_COLOR:
            self._list.setItemDelegate(ColorItemDelegate(self._list))
        else:
            self._list.setItemDelegate(HighlightItemDelegate(self._list))
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel(title)
        title_label.setEnabled(False)
        header.addWidget(title_label)
        if zone == ZONE_EMOJI:
            pick = QToolButton(self)
            pick.setIcon(create_lucide_icon("bot", 18))
            pick.setIconSize(QSize(18, 18))
            pick.setFixedSize(28, 28)
            pick.setAutoRaise(True)
            pick.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            pick.setCursor(Qt.CursorShape.PointingHandCursor)
            pick.setToolTip("Pick emoji by name")
            pick.setVisible(False)
            pick.clicked.connect(self.ai_pick_requested.emit)
            self._ai_pick_button = pick
            header.addWidget(pick)
        header.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(header)
        if zone == ZONE_EMOJI:
            panel = QWidget(self)
            panel_layout = QHBoxLayout(panel)
            panel_layout.setContentsMargins(0, 0, 0, 0)
            panel_layout.setSpacing(4)
            host = QWidget(panel)
            self._ai_candidates_layout = FlowLayout(host, margin=0, h_spacing=4, v_spacing=4)
            panel_layout.addWidget(host, stretch=1)
            close = QToolButton(panel)
            close.setText("X")
            close.setFixedSize(22, 22)
            close.setAutoRaise(True)
            close.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            close.setCursor(Qt.CursorShape.PointingHandCursor)
            close.setToolTip("Close suggestions")
            close.clicked.connect(self._dismiss_ai_candidates)
            panel_layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignTop)
            panel.hide()
            self._ai_candidates = panel
            layout.addWidget(panel)
        layout.addWidget(self._list, stretch=1)

    def activate_current_or_first(self) -> None:
        """Paste the selected item, or the first visible item when none is selected."""
        snippet = self.current_snippet()
        if snippet is None:
            rows = self.visible_rows()
            if not rows:
                return
            self.select_row(rows[0])
            snippet = self.current_snippet()
        if snippet is not None:
            self.item_activated.emit(snippet)

    def clear_ai_candidates(self) -> None:
        """Remove AI suggestion chips from the emoji zone."""
        self._ai_emojis = []
        self._rebuild_ai_candidates(())

    def clear_filter(self) -> None:
        """Clear this zone's search query."""
        self._filter_query = ""
        self._apply_filter()

    def current_snippet(self) -> SnippetItem | None:
        """Return the selected visible snippet, if any."""
        item = self._list.currentItem()
        if item is None or item.isHidden():
            return None
        data = item.data(_ITEM_ROLE)
        return data if data is not None else None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Enter to paste from the list."""
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        if watched is self._list and event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            self.activate_current_or_first()
            return True
        return super().eventFilter(watched, event)

    def filter_query(self) -> str:
        """Return the current search query for this zone."""
        return self._filter_query

    def item_at(self, pos: QPoint) -> SnippetItem | None:
        """Return the item under `pos` in list coordinates, if any."""
        item = self._list.itemAt(pos)
        if item is None:
            return None
        data = item.data(_ITEM_ROLE)
        return data if data is not None else None

    def item_matches_input(self, snippet: SnippetItem | None) -> bool:
        """Return whether `snippet` is the value currently shown in the shared input."""
        return bool(self._input_match) and snippet is not None and snippet.value == self._input_match

    def move_visible(self, delta: int) -> bool:
        """Move the list highlight among currently visible items.

        Args:

        - `delta` (`int`): `1` for the next item, `-1` for the previous.

        Returns:

        - `bool`: `True` when a visible item was selected.

        """
        rows = self.visible_rows()
        if not rows:
            return False
        current = self._list.currentRow()
        if current not in rows:
            row = rows[0] if delta >= 0 else rows[-1]
        else:
            index = rows.index(current) + delta
            row = rows[max(0, min(index, len(rows) - 1))]
        self.select_row(row)
        return True

    def prepare_keyboard_focus(self) -> None:
        """Select the remembered or first visible item without taking keyboard focus."""
        if self._restore_remembered_row():
            return
        current = self._list.currentItem()
        if current is not None and not current.isHidden():
            self._remember_current()
            return
        rows = self.visible_rows()
        if rows:
            self.select_row(rows[0])

    def refresh_ai_candidates(self, existing_values: Sequence[str]) -> None:
        """Rebuild AI chips after the emoji list changes."""
        self._rebuild_ai_candidates(existing_values)

    def reset_keyboard_session(self) -> None:
        """Clear the keyboard highlight remembered for this Quick paste session."""
        self._remembered_id = None
        self._clear_list_current()

    def select_row(self, row: int) -> None:
        """Select `row` and remember it for the next keyboard session.

        Args:

        - `row` (`int`): List row index.

        """
        item = self._list.item(row)
        if item is None or item.isHidden():
            return
        self._list.setCurrentItem(item)
        item.setSelected(True)
        self._list.scrollToItem(item)
        self._remember_current()

    def set_ai_candidates(self, emojis: list[str], *, existing_values: Sequence[str]) -> None:
        """Show AI emoji suggestions; missing ones get an add button."""
        self._ai_emojis = list(emojis)
        self._rebuild_ai_candidates(existing_values)
        if self._ai_pick_button is not None:
            self._ai_pick_button.hide()

    def set_ai_pick_enabled(self, *, enabled: bool) -> None:
        """Enable or disable the pick-by-name button."""
        if self._ai_pick_button is not None:
            self._ai_pick_button.setEnabled(enabled)

    def set_ai_pick_visible(self, *, visible: bool) -> None:
        """Show the pick-by-name button when the shared input has text."""
        if self._ai_pick_button is not None:
            self._ai_pick_button.setVisible(visible and not self._ai_emojis)

    def set_filter_query(self, text: str) -> None:
        """Filter this zone by `text` and clear the current highlight."""
        self._filter_query = text
        self._remembered_id = None
        self._clear_list_current()
        self._apply_filter()

    def set_input_match(self, value: str) -> None:
        """Mark the item whose value equals `value` as the current input match."""
        if self._input_match == value:
            return
        self._input_match = value
        self._list.viewport().update()

    def set_items(self, items: list[SnippetItem]) -> None:
        """Replace the visible items."""
        self._items = items
        self._list.clear()
        for snippet in items:
            list_item = QListWidgetItem()
            list_item.setData(_ITEM_ROLE, snippet)
            label = display_text(snippet.value, snippet.hint, snippet.zone)
            if self.zone == ZONE_EMOJI:
                list_item.setIcon(create_emoji_icon(snippet.value, _ICON_PIXEL_SIZE))
                list_item.setToolTip(snippet.value)
            elif self.zone == ZONE_SYMBOL:
                list_item.setIcon(create_emoji_icon(snippet.value, _ICON_PIXEL_SIZE))
                list_item.setToolTip(hint_tooltip(snippet.hint, snippet.value))
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
        """Remember the active sort so the context menu can mark it."""
        self._sort_mode = zone_sort.mode
        self._sort_descending = zone_sort.descending

    def visible_rows(self) -> list[int]:
        """Return indexes of items that pass the current filter."""
        rows: list[int] = []
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is not None and not item.isHidden():
                rows.append(row)
        return rows

    def _apply_filter(self) -> None:
        query = self._filter_query
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is None:
                continue
            snippet = item.data(_ITEM_ROLE)
            if snippet is None:
                item.setHidden(False)
                continue
            item.setHidden(not item_matches_search(snippet.value, snippet.hint, query))
        current = self._list.currentItem()
        if current is not None and current.isHidden():
            self._clear_list_current()

    def _build_context_menu(self, snippet: SnippetItem | None) -> QMenu:
        menu = QMenu(self)
        add_lucide_action(menu, "Add item", "plus").triggered.connect(self.add_requested.emit)
        add_lucide_action(menu, "Add many items", "download").triggered.connect(self.add_many_requested.emit)
        edit_action = add_lucide_action(menu, "Edit item", "pencil")
        edit_action.setEnabled(snippet is not None)
        if snippet is not None:
            edit_action.triggered.connect(lambda _checked=False, item=snippet: self.edit_requested.emit(item))
        add_lucide_action(menu, "Edit entire list", "notebook-pen").triggered.connect(self.edit_all_requested.emit)
        delete_action = add_lucide_action(menu, "Delete item", "trash")
        delete_action.setEnabled(snippet is not None)
        if snippet is not None:
            delete_action.triggered.connect(lambda _checked=False, item=snippet: self.delete_requested.emit(item))
        menu.addSeparator()
        add_sort_menu_actions(
            menu,
            mode=self._sort_mode,
            descending=self._sort_descending,
            on_sort=self.sort_requested.emit,
        )
        return menu

    def _clear_ai_candidate_widgets(self) -> None:
        layout = self._ai_candidates_layout
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _clear_list_current(self) -> None:
        self._list.clearSelection()
        self._list.setCurrentRow(-1)

    def _dismiss_ai_candidates(self) -> None:
        self.clear_ai_candidates()
        self.ai_dismiss_requested.emit()

    def _on_context_menu(self, pos: QPoint) -> None:
        widget = self.sender()
        if widget is self._list:
            global_pos = self._list.mapToGlobal(pos)
            snippet = self.item_at(pos)
        else:
            global_pos = self.mapToGlobal(pos)
            snippet = self.item_at(self._list.mapFrom(self, pos))

        menu = self._build_context_menu(snippet)
        menu.popup(global_pos)

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None or current.isHidden():
            return
        snippet = current.data(_ITEM_ROLE)
        if snippet is not None:
            self._remembered_id = snippet.item_id

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        snippet = item.data(_ITEM_ROLE)
        if snippet is not None:
            self.item_activated.emit(snippet)

    def _rebuild_ai_candidates(self, existing_values: Sequence[str]) -> None:
        host = self._ai_candidates
        layout = self._ai_candidates_layout
        if host is None or layout is None:
            return
        self._clear_ai_candidate_widgets()
        if not self._ai_emojis:
            host.hide()
            return
        for emoji in self._ai_emojis:
            can_add = not any(item_values_equal(ZONE_EMOJI, emoji, value) for value in existing_values)
            layout.addWidget(
                _make_emoji_candidate_chip(
                    emoji,
                    can_add=can_add,
                    on_add=self.ai_add_requested.emit,
                    on_paste=self.ai_paste_requested.emit,
                ),
            )
        host.show()

    def _remember_current(self) -> None:
        snippet = self.current_snippet()
        self._remembered_id = snippet.item_id if snippet is not None else None

    def _restore_remembered_row(self) -> bool:
        if self._remembered_id is None:
            return False
        for row in self.visible_rows():
            item = self._list.item(row)
            if item is None:
                continue
            snippet = item.data(_ITEM_ROLE)
            if snippet is not None and snippet.item_id == self._remembered_id:
                self.select_row(row)
                return True
        return False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, zone: str, title: str) -> None
```

Build the zone header and list.

Args:

- `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
- `zone` (`str`): Zone identifier.
- `title` (`str`): Header label.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        zone: str,
        title: str,
    ) -> None:
        super().__init__(parent)
        self.zone = zone
        self._items: list[SnippetItem] = []
        self._sort_mode: SortMode = DEFAULT_SORT_MODE
        self._sort_descending = False
        self._filter_query = ""
        self._input_match = ""
        self._remembered_id: int | None = None
        self._ai_pick_button: QToolButton | None = None
        self._ai_candidates: QWidget | None = None
        self._ai_candidates_layout: FlowLayout | None = None
        self._ai_emojis: list[str] = []

        self._list = QListWidget(self)
        self._list.setFrameShape(QListWidget.Shape.NoFrame)
        self._list.setStyleSheet(_LIST_SELECTION_STYLE)
        self._list.setMouseTracking(True)
        self._list.viewport().setMouseTracking(True)
        self._list.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        _apply_list_highlight_palette(self._list)
        self._list.installEventFilter(self)
        apply_mono_font(self._list)
        if zone in {ZONE_EMOJI, ZONE_SYMBOL}:
            self._list.setViewMode(QListWidget.ViewMode.IconMode)
            self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
            self._list.setMovement(QListWidget.Movement.Static)
            self._list.setGridSize(_ICON_GRID)
            self._list.setIconSize(QSize(_ICON_PIXEL_SIZE, _ICON_PIXEL_SIZE))
            self._list.setSpacing(_ICON_SPACING)
            self._list.setWordWrap(False)
            self._list.setItemDelegate(IconItemDelegate(self._list))
        elif zone == ZONE_COLOR:
            self._list.setItemDelegate(ColorItemDelegate(self._list))
        else:
            self._list.setItemDelegate(HighlightItemDelegate(self._list))
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel(title)
        title_label.setEnabled(False)
        header.addWidget(title_label)
        if zone == ZONE_EMOJI:
            pick = QToolButton(self)
            pick.setIcon(create_lucide_icon("bot", 18))
            pick.setIconSize(QSize(18, 18))
            pick.setFixedSize(28, 28)
            pick.setAutoRaise(True)
            pick.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            pick.setCursor(Qt.CursorShape.PointingHandCursor)
            pick.setToolTip("Pick emoji by name")
            pick.setVisible(False)
            pick.clicked.connect(self.ai_pick_requested.emit)
            self._ai_pick_button = pick
            header.addWidget(pick)
        header.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addLayout(header)
        if zone == ZONE_EMOJI:
            panel = QWidget(self)
            panel_layout = QHBoxLayout(panel)
            panel_layout.setContentsMargins(0, 0, 0, 0)
            panel_layout.setSpacing(4)
            host = QWidget(panel)
            self._ai_candidates_layout = FlowLayout(host, margin=0, h_spacing=4, v_spacing=4)
            panel_layout.addWidget(host, stretch=1)
            close = QToolButton(panel)
            close.setText("X")
            close.setFixedSize(22, 22)
            close.setAutoRaise(True)
            close.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            close.setCursor(Qt.CursorShape.PointingHandCursor)
            close.setToolTip("Close suggestions")
            close.clicked.connect(self._dismiss_ai_candidates)
            panel_layout.addWidget(close, alignment=Qt.AlignmentFlag.AlignTop)
            panel.hide()
            self._ai_candidates = panel
            layout.addWidget(panel)
        layout.addWidget(self._list, stretch=1)
```

</details>

### ⚙️ Method `activate_current_or_first`

```python
def activate_current_or_first(self) -> None
```

Paste the selected item, or the first visible item when none is selected.

<details>
<summary>Code:</summary>

```python
def activate_current_or_first(self) -> None:
        snippet = self.current_snippet()
        if snippet is None:
            rows = self.visible_rows()
            if not rows:
                return
            self.select_row(rows[0])
            snippet = self.current_snippet()
        if snippet is not None:
            self.item_activated.emit(snippet)
```

</details>

### ⚙️ Method `clear_ai_candidates`

```python
def clear_ai_candidates(self) -> None
```

Remove AI suggestion chips from the emoji zone.

<details>
<summary>Code:</summary>

```python
def clear_ai_candidates(self) -> None:
        self._ai_emojis = []
        self._rebuild_ai_candidates(())
```

</details>

### ⚙️ Method `clear_filter`

```python
def clear_filter(self) -> None
```

Clear this zone's search query.

<details>
<summary>Code:</summary>

```python
def clear_filter(self) -> None:
        self._filter_query = ""
        self._apply_filter()
```

</details>

### ⚙️ Method `current_snippet`

```python
def current_snippet(self) -> SnippetItem | None
```

Return the selected visible snippet, if any.

<details>
<summary>Code:</summary>

```python
def current_snippet(self) -> SnippetItem | None:
        item = self._list.currentItem()
        if item is None or item.isHidden():
            return None
        data = item.data(_ITEM_ROLE)
        return data if data is not None else None
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Enter to paste from the list.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        if watched is self._list and event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            self.activate_current_or_first()
            return True
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `filter_query`

```python
def filter_query(self) -> str
```

Return the current search query for this zone.

<details>
<summary>Code:</summary>

```python
def filter_query(self) -> str:
        return self._filter_query
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

### ⚙️ Method `item_matches_input`

```python
def item_matches_input(self, snippet: SnippetItem | None) -> bool
```

Return whether `snippet` is the value currently shown in the shared input.

<details>
<summary>Code:</summary>

```python
def item_matches_input(self, snippet: SnippetItem | None) -> bool:
        return bool(self._input_match) and snippet is not None and snippet.value == self._input_match
```

</details>

### ⚙️ Method `move_visible`

```python
def move_visible(self, delta: int) -> bool
```

Move the list highlight among currently visible items.

Args:

- `delta` (`int`): `1` for the next item, `-1` for the previous.

Returns:

- `bool`: `True` when a visible item was selected.

<details>
<summary>Code:</summary>

```python
def move_visible(self, delta: int) -> bool:
        rows = self.visible_rows()
        if not rows:
            return False
        current = self._list.currentRow()
        if current not in rows:
            row = rows[0] if delta >= 0 else rows[-1]
        else:
            index = rows.index(current) + delta
            row = rows[max(0, min(index, len(rows) - 1))]
        self.select_row(row)
        return True
```

</details>

### ⚙️ Method `prepare_keyboard_focus`

```python
def prepare_keyboard_focus(self) -> None
```

Select the remembered or first visible item without taking keyboard focus.

<details>
<summary>Code:</summary>

```python
def prepare_keyboard_focus(self) -> None:
        if self._restore_remembered_row():
            return
        current = self._list.currentItem()
        if current is not None and not current.isHidden():
            self._remember_current()
            return
        rows = self.visible_rows()
        if rows:
            self.select_row(rows[0])
```

</details>

### ⚙️ Method `refresh_ai_candidates`

```python
def refresh_ai_candidates(self, existing_values: Sequence[str]) -> None
```

Rebuild AI chips after the emoji list changes.

<details>
<summary>Code:</summary>

```python
def refresh_ai_candidates(self, existing_values: Sequence[str]) -> None:
        self._rebuild_ai_candidates(existing_values)
```

</details>

### ⚙️ Method `reset_keyboard_session`

```python
def reset_keyboard_session(self) -> None
```

Clear the keyboard highlight remembered for this Quick paste session.

<details>
<summary>Code:</summary>

```python
def reset_keyboard_session(self) -> None:
        self._remembered_id = None
        self._clear_list_current()
```

</details>

### ⚙️ Method `select_row`

```python
def select_row(self, row: int) -> None
```

Select `row` and remember it for the next keyboard session.

Args:

- `row` (`int`): List row index.

<details>
<summary>Code:</summary>

```python
def select_row(self, row: int) -> None:
        item = self._list.item(row)
        if item is None or item.isHidden():
            return
        self._list.setCurrentItem(item)
        item.setSelected(True)
        self._list.scrollToItem(item)
        self._remember_current()
```

</details>

### ⚙️ Method `set_ai_candidates`

```python
def set_ai_candidates(self, emojis: list[str], *, existing_values: Sequence[str]) -> None
```

Show AI emoji suggestions; missing ones get an add button.

<details>
<summary>Code:</summary>

```python
def set_ai_candidates(self, emojis: list[str], *, existing_values: Sequence[str]) -> None:
        self._ai_emojis = list(emojis)
        self._rebuild_ai_candidates(existing_values)
        if self._ai_pick_button is not None:
            self._ai_pick_button.hide()
```

</details>

### ⚙️ Method `set_ai_pick_enabled`

```python
def set_ai_pick_enabled(self, *, enabled: bool) -> None
```

Enable or disable the pick-by-name button.

<details>
<summary>Code:</summary>

```python
def set_ai_pick_enabled(self, *, enabled: bool) -> None:
        if self._ai_pick_button is not None:
            self._ai_pick_button.setEnabled(enabled)
```

</details>

### ⚙️ Method `set_ai_pick_visible`

```python
def set_ai_pick_visible(self, *, visible: bool) -> None
```

Show the pick-by-name button when the shared input has text.

<details>
<summary>Code:</summary>

```python
def set_ai_pick_visible(self, *, visible: bool) -> None:
        if self._ai_pick_button is not None:
            self._ai_pick_button.setVisible(visible and not self._ai_emojis)
```

</details>

### ⚙️ Method `set_filter_query`

```python
def set_filter_query(self, text: str) -> None
```

Filter this zone by `text` and clear the current highlight.

<details>
<summary>Code:</summary>

```python
def set_filter_query(self, text: str) -> None:
        self._filter_query = text
        self._remembered_id = None
        self._clear_list_current()
        self._apply_filter()
```

</details>

### ⚙️ Method `set_input_match`

```python
def set_input_match(self, value: str) -> None
```

Mark the item whose value equals `value` as the current input match.

<details>
<summary>Code:</summary>

```python
def set_input_match(self, value: str) -> None:
        if self._input_match == value:
            return
        self._input_match = value
        self._list.viewport().update()
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
                list_item.setIcon(create_emoji_icon(snippet.value, _ICON_PIXEL_SIZE))
                list_item.setToolTip(snippet.value)
            elif self.zone == ZONE_SYMBOL:
                list_item.setIcon(create_emoji_icon(snippet.value, _ICON_PIXEL_SIZE))
                list_item.setToolTip(hint_tooltip(snippet.hint, snippet.value))
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

Remember the active sort so the context menu can mark it.

<details>
<summary>Code:</summary>

```python
def set_sort_state(self, zone_sort: ZoneSort) -> None:
        self._sort_mode = zone_sort.mode
        self._sort_descending = zone_sort.descending
```

</details>

### ⚙️ Method `visible_rows`

```python
def visible_rows(self) -> list[int]
```

Return indexes of items that pass the current filter.

<details>
<summary>Code:</summary>

```python
def visible_rows(self) -> list[int]:
        rows: list[int] = []
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item is not None and not item.isHidden():
                rows.append(row)
        return rows
```

</details>

## 🔧 Function `add_sort_menu_actions`

```python
def add_sort_menu_actions(menu: QMenu, *, mode: str | None, descending: bool, on_sort: Callable[[str], None]) -> None
```

Append checkable sort actions that call `on_sort` with the mode ID.

<details>
<summary>Code:</summary>

```python
def add_sort_menu_actions(
    menu: QMenu,
    *,
    mode: str | None,
    descending: bool,
    on_sort: Callable[[str], None],
) -> None:
    group = QActionGroup(menu)
    group.setExclusive(True)
    for sort_mode, icon_name, tooltip in _SORT_BUTTONS:
        action = add_lucide_action(menu, tooltip, icon_name)
        action.setCheckable(True)
        action.setChecked(mode == sort_mode)
        if mode == sort_mode and descending:
            action.setText(f"{tooltip} (reversed)")
        group.addAction(action)
        action.triggered.connect(lambda _checked=False, chosen=sort_mode: on_sort(chosen))
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
    return strip_wrapping_brackets(value)
```

</details>

## 🔧 Function `paint_snippet_highlight`

```python
def paint_snippet_highlight(painter: QPainter, rect: QRect, *, outlined: bool = False) -> None
```

Fill the item with the hover/selection color, optionally with a 1 px gray outline.

<details>
<summary>Code:</summary>

```python
def paint_snippet_highlight(painter: QPainter, rect: QRect, *, outlined: bool = False) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    painter.setBrush(QColor(_SELECTION_BG))
    if outlined:
        painter.setPen(QPen(QColor(_SELECTION_OUTLINE), 1))
        inner = rect.adjusted(1, 1, -2, -2)
    else:
        painter.setPen(Qt.PenStyle.NoPen)
        inner = rect.adjusted(1, 1, -1, -1)
    painter.drawRoundedRect(inner, _SELECTION_RADIUS, _SELECTION_RADIUS)
```

</details>
