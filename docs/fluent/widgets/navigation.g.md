---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `navigation.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentBreadcrumb`](#%EF%B8%8F-class-fluentbreadcrumb)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `items`](#%EF%B8%8F-method-items)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `push`](#%EF%B8%8F-method-push)
  - [⚙️ Method `set_items`](#%EF%B8%8F-method-set_items)
- [🏛️ Class `FluentExpander`](#%EF%B8%8F-class-fluentexpander)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `is_expanded`](#%EF%B8%8F-method-is_expanded)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `set_expanded`](#%EF%B8%8F-method-set_expanded)
  - [⚙️ Method `toggle`](#%EF%B8%8F-method-toggle)
- [🏛️ Class `FluentGroupBox`](#%EF%B8%8F-class-fluentgroupbox)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `add_widget`](#%EF%B8%8F-method-add_widget)
- [🏛️ Class `FluentNavigationBar`](#%EF%B8%8F-class-fluentnavigationbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `add_footer_item`](#%EF%B8%8F-method-add_footer_item)
  - [⚙️ Method `add_header`](#%EF%B8%8F-method-add_header)
  - [⚙️ Method `add_item`](#%EF%B8%8F-method-add_item)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `current`](#%EF%B8%8F-method-current)
  - [⚙️ Method `is_compact`](#%EF%B8%8F-method-is_compact)
  - [⚙️ Method `item`](#%EF%B8%8F-method-item)
  - [⚙️ Method `items`](#%EF%B8%8F-method-items-1)
  - [⚙️ Method `leaveEvent`](#%EF%B8%8F-method-leaveevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent-1)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent-1)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-2)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `set_compact`](#%EF%B8%8F-method-set_compact)
  - [⚙️ Method `set_current`](#%EF%B8%8F-method-set_current)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `toggle_compact`](#%EF%B8%8F-method-toggle_compact)
- [🏛️ Class `FluentNavigationPanel`](#%EF%B8%8F-class-fluentnavigationpanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `add_page`](#%EF%B8%8F-method-add_page)
- [🏛️ Class `FluentPagination`](#%EF%B8%8F-class-fluentpagination)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `current`](#%EF%B8%8F-method-current-1)
  - [⚙️ Method `page_count`](#%EF%B8%8F-method-page_count)
  - [⚙️ Method `set_current`](#%EF%B8%8F-method-set_current-1)
  - [⚙️ Method `set_page_count`](#%EF%B8%8F-method-set_page_count)
  - [⚙️ Method `visible_pages`](#%EF%B8%8F-method-visible_pages)
- [🏛️ Class `FluentPivot`](#%EF%B8%8F-class-fluentpivot)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
  - [⚙️ Method `add_item`](#%EF%B8%8F-method-add_item-1)
  - [⚙️ Method `current`](#%EF%B8%8F-method-current-2)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent-2)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent-2)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-3)
  - [⚙️ Method `set_current`](#%EF%B8%8F-method-set_current-2)
- [🏛️ Class `FluentSplitter`](#%EF%B8%8F-class-fluentsplitter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-7)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
- [🏛️ Class `FluentTabBar`](#%EF%B8%8F-class-fluenttabbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-8)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-1)
- [🏛️ Class `FluentTabWidget`](#%EF%B8%8F-class-fluenttabwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-9)
  - [⚙️ Method `add_tab`](#%EF%B8%8F-method-add_tab)
  - [⚙️ Method `count`](#%EF%B8%8F-method-count)
  - [⚙️ Method `current_index`](#%EF%B8%8F-method-current_index)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme-2)
  - [⚙️ Method `remove_tab`](#%EF%B8%8F-method-remove_tab)
  - [⚙️ Method `set_current_index`](#%EF%B8%8F-method-set_current_index)
- [🏛️ Class `NavigationItem`](#%EF%B8%8F-class-navigationitem)

</details>

## 🏛️ Class `FluentBreadcrumb`

```python
class FluentBreadcrumb(QWidget)
```

Path of clickable items separated by chevrons; the last item is the current page.

<details>
<summary>Code:</summary>

```python
class FluentBreadcrumb(QWidget):

    item_clicked = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        """Create a breadcrumb."""
        super().__init__(parent)
        self._items = list(items)
        self._hover = -1
        self.setMouseTracking(True)
        self.setFixedHeight(CONTROL_HEIGHT + SPACE_S)
        bind_theme(self, self.update)

    def items(self) -> list[str]:
        """Return the path items."""
        return list(self._items)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered item."""
        index = self._index_at(event.position().x())
        if index != self._hover:
            self._hover = index
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if 0 <= index < len(self._items) - 1 else Qt.CursorShape.ArrowCursor
            )
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Navigate back to the clicked item (drops the items after it)."""
        index = self._index_at(event.position().x())
        if 0 <= index < len(self._items) - 1:
            self._items = self._items[: index + 1]
            self.update()
            self.item_clicked.emit(index)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint items and separators."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        painter.setFont(font)
        for index, (text, rect, chevron) in enumerate(self._layout_items(QFontMetrics(font))):
            last = index == len(self._items) - 1
            color = palette.text_primary if last else palette.text_secondary
            if index == self._hover and not last:
                color = palette.text_primary
            painter.setPen(color)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), text)
            if chevron is not None:
                themed_icon("chevron-right", palette, palette.text_secondary, ICON_SIZE).paint(
                    painter, chevron.toRect()
                )
        painter.end()

    def push(self, text: str) -> None:
        """Append an item (a new current page)."""
        self._items.append(text)
        self.update()

    def set_items(self, items: Sequence[str]) -> None:
        """Replace the path."""
        self._items = list(items)
        self.update()

    def _index_at(self, x: float) -> int:
        font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        for index, (_text, rect, _chevron) in enumerate(self._layout_items(QFontMetrics(font))):
            if rect.left() <= x <= rect.right():
                return index
        return -1

    def _layout_items(self, metrics: QFontMetrics) -> list[tuple[str, QRectF, QRectF | None]]:
        result: list[tuple[str, QRectF, QRectF | None]] = []
        x = 0.0
        for index, text in enumerate(self._items):
            width = metrics.horizontalAdvance(text)
            rect = QRectF(x, 0, width, self.height())
            x += width
            chevron = None
            if index < len(self._items) - 1:
                chevron = QRectF(x + SPACE_S, (self.height() - ICON_SIZE) / 2, ICON_SIZE, ICON_SIZE)
                x += ICON_SIZE + 2 * SPACE_S
            result.append((text, rect, chevron))
        return result
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None
```

Create a breadcrumb.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        super().__init__(parent)
        self._items = list(items)
        self._hover = -1
        self.setMouseTracking(True)
        self.setFixedHeight(CONTROL_HEIGHT + SPACE_S)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `items`

```python
def items(self) -> list[str]
```

Return the path items.

<details>
<summary>Code:</summary>

```python
def items(self) -> list[str]:
        return list(self._items)
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Track the hovered item.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        index = self._index_at(event.position().x())
        if index != self._hover:
            self._hover = index
            self.setCursor(
                Qt.CursorShape.PointingHandCursor if 0 <= index < len(self._items) - 1 else Qt.CursorShape.ArrowCursor
            )
            self.update()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Navigate back to the clicked item (drops the items after it).

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        index = self._index_at(event.position().x())
        if 0 <= index < len(self._items) - 1:
            self._items = self._items[: index + 1]
            self.update()
            self.item_clicked.emit(index)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint items and separators.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        painter.setFont(font)
        for index, (text, rect, chevron) in enumerate(self._layout_items(QFontMetrics(font))):
            last = index == len(self._items) - 1
            color = palette.text_primary if last else palette.text_secondary
            if index == self._hover and not last:
                color = palette.text_primary
            painter.setPen(color)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), text)
            if chevron is not None:
                themed_icon("chevron-right", palette, palette.text_secondary, ICON_SIZE).paint(
                    painter, chevron.toRect()
                )
        painter.end()
```

</details>

### ⚙️ Method `push`

```python
def push(self, text: str) -> None
```

Append an item (a new current page).

<details>
<summary>Code:</summary>

```python
def push(self, text: str) -> None:
        self._items.append(text)
        self.update()
```

</details>

### ⚙️ Method `set_items`

```python
def set_items(self, items: Sequence[str]) -> None
```

Replace the path.

<details>
<summary>Code:</summary>

```python
def set_items(self, items: Sequence[str]) -> None:
        self._items = list(items)
        self.update()
```

</details>

## 🏛️ Class `FluentExpander`

```python
class FluentExpander(QWidget)
```

Card with a header row (icon, title, caption, chevron) that expands to show content.

<details>
<summary>Code:</summary>

```python
class FluentExpander(QWidget):

    expanded_changed = Signal(bool)

    def __init__(self, title: str, parent: QWidget | None = None, *, caption: str = "", icon: str = "") -> None:
        """Create an expander; put content into `content_layout`."""
        super().__init__(parent)
        self._expanded = False
        self._icon = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._header = _ExpanderHeader(title, caption, icon, self)
        self._header.clicked.connect(self.toggle)
        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(SPACE_L * 3, SPACE_M, SPACE_L, SPACE_M)
        self.content.setVisible(False)
        layout.addWidget(self._header)
        layout.addWidget(self.content)
        bind_theme(self, self.update)

    def is_expanded(self) -> bool:
        """Return whether the content is shown."""
        return self._expanded

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card behind header and content."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        if self._expanded:
            y = self._header.geometry().bottom() + 1
            painter.fillRect(QRectF(1, y, self.width() - 2, 1), palette.divider)
        painter.end()

    def set_expanded(self, *, expanded: bool) -> None:
        """Show or hide the content."""
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self.content.setVisible(expanded)
        self._header.set_expanded(expanded=expanded)
        self.update()
        self.expanded_changed.emit(expanded)

    def toggle(self) -> None:
        """Flip the expanded state."""
        self.set_expanded(expanded=not self._expanded)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None, *, caption: str = '', icon: str = '') -> None
```

Create an expander; put content into `content_layout`.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, parent: QWidget | None = None, *, caption: str = "", icon: str = "") -> None:
        super().__init__(parent)
        self._expanded = False
        self._icon = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._header = _ExpanderHeader(title, caption, icon, self)
        self._header.clicked.connect(self.toggle)
        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(SPACE_L * 3, SPACE_M, SPACE_L, SPACE_M)
        self.content.setVisible(False)
        layout.addWidget(self._header)
        layout.addWidget(self.content)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `is_expanded`

```python
def is_expanded(self) -> bool
```

Return whether the content is shown.

<details>
<summary>Code:</summary>

```python
def is_expanded(self) -> bool:
        return self._expanded
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the card behind header and content.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        if self._expanded:
            y = self._header.geometry().bottom() + 1
            painter.fillRect(QRectF(1, y, self.width() - 2, 1), palette.divider)
        painter.end()
```

</details>

### ⚙️ Method `set_expanded`

```python
def set_expanded(self, *, expanded: bool) -> None
```

Show or hide the content.

<details>
<summary>Code:</summary>

```python
def set_expanded(self, *, expanded: bool) -> None:
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self.content.setVisible(expanded)
        self._header.set_expanded(expanded=expanded)
        self.update()
        self.expanded_changed.emit(expanded)
```

</details>

### ⚙️ Method `toggle`

```python
def toggle(self) -> None
```

Flip the expanded state.

<details>
<summary>Code:</summary>

```python
def toggle(self) -> None:
        self.set_expanded(expanded=not self._expanded)
```

</details>

## 🏛️ Class `FluentGroupBox`

```python
class FluentGroupBox(QWidget)
```

Titled group of setting cards (subtitle header + stacked content).

<details>
<summary>Code:</summary>

```python
class FluentGroupBox(QWidget):

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Create a group; add cards with `add_widget`."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_S)
        self.title_label = FluentText(title, self, style=TextStyle.BODY_STRONG)
        layout.addWidget(self.title_label)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACE_XS)
        layout.addLayout(self.content_layout)

    def add_widget(self, widget: QWidget) -> None:
        """Append a widget (usually a card) to the group."""
        self.content_layout.addWidget(widget)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None) -> None
```

Create a group; add cards with [`add_widget`](#%EF%B8%8F-method-add_widget).

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_S)
        self.title_label = FluentText(title, self, style=TextStyle.BODY_STRONG)
        layout.addWidget(self.title_label)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACE_XS)
        layout.addLayout(self.content_layout)
```

</details>

### ⚙️ Method `add_widget`

```python
def add_widget(self, widget: QWidget) -> None
```

Append a widget (usually a card) to the group.

<details>
<summary>Code:</summary>

```python
def add_widget(self, widget: QWidget) -> None:
        self.content_layout.addWidget(widget)
```

</details>

## 🏛️ Class `FluentNavigationBar`

```python
class FluentNavigationBar(QWidget)
```

Side navigation: icons + text rows, section headers, accent pill, and a compact mode.

Rows are painted (no `QListWidget`), so hover, the selected fill, and the
sliding accent indicator match WinUI `NavigationView` exactly.

<details>
<summary>Code:</summary>

```python
class FluentNavigationBar(QWidget):

    current_changed = Signal(str)
    item_context_menu_requested = Signal(str, QPoint)

    def __init__(self, parent: QWidget | None = None, *, collapsible: bool = True) -> None:
        """Create an empty navigation bar."""
        super().__init__(parent)
        self._items: list[NavigationItem] = []
        self._footer: list[NavigationItem] = []
        self._current = ""
        self._hover = ""
        self._compact = False
        self._indicator_y = -1.0
        self._indicator = QVariantAnimation(self)
        self._indicator.setDuration(ANIMATION_NORMAL)
        self._indicator.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._indicator.valueChanged.connect(self._on_indicator)
        self._scroll_offset = 0
        self.setMouseTracking(True)
        self.setMinimumWidth(_NAV_COMPACT_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        layout.setSpacing(0)
        self._toggle: FluentIconButton | None = None
        if collapsible:
            self._toggle = FluentIconButton("menu", self, tooltip="Toggle navigation")
            self._toggle.clicked.connect(self.toggle_compact)
            layout.addWidget(self._toggle, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        bind_theme(self, self.update)

    def add_footer_item(self, key: str, text: str, *, icon: str = "", data: object = None) -> None:
        """Append a row pinned to the bottom (for example Settings)."""
        self._footer.append(NavigationItem(key, text, icon, data=data))
        self.update()

    def add_header(self, text: str) -> None:
        """Append a section header row."""
        self._items.append(NavigationItem(f"__header__{len(self._items)}", text, header=True))
        self.updateGeometry()
        self.update()

    def add_item(self, key: str, text: str, *, icon: str = "", data: object = None) -> None:
        """Append a navigation row."""
        self._items.append(NavigationItem(key, text, icon, data=data))
        if not self._current:
            self._current = key
        self.updateGeometry()
        self.update()

    def clear(self) -> None:
        """Remove every row."""
        self._items.clear()
        self._current = ""
        self._indicator_y = -1
        self.update()

    def current(self) -> str:
        """Return the selected key."""
        return self._current

    def is_compact(self) -> bool:
        """Return whether only icons are shown."""
        return self._compact

    def item(self, key: str) -> NavigationItem | None:
        """Return the row with `key`."""
        for entry in [*self._items, *self._footer]:
            if entry.key == key:
                return entry
        return None

    def items(self) -> list[NavigationItem]:
        """Return the main (non-footer) rows, including headers."""
        return list(self._items)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Clear the hover row."""
        self._hover = ""
        self.update()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered row."""
        key = self._key_at(event.position().y())
        if key != self._hover:
            self._hover = key
            self.update()
        entry = self.item(key) if key else None
        self.setToolTip(entry.text if entry is not None and self._compact else "")

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select the clicked row; right click requests a context menu."""
        key = self._key_at(event.position().y())
        if not key:
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.item_context_menu_requested.emit(key, event.globalPosition().toPoint())
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_current(key)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint rows, headers, selection fill, and the accent indicator."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        body = fluent_font(self.font(), TYPE_BODY)
        header_font = fluent_font(self.font(), TYPE_CAPTION, weight=QFont.Weight.DemiBold)
        for entry, rect in self._row_rects():
            if entry.header:
                if self._compact:
                    painter.fillRect(
                        QRectF(rect.left() + SPACE_S, rect.center().y(), rect.width() - 2 * SPACE_S, 1), palette.divider
                    )
                    continue
                painter.setFont(header_font)
                painter.setPen(palette.text_secondary)
                painter.drawText(
                    rect.adjusted(SPACE_M, 0, -SPACE_S, 0),
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                    entry.text,
                )
                continue
            selected = entry.key == self._current
            if selected or entry.key == self._hover:
                fill = palette.subtle_pressed if selected and entry.key == self._hover else palette.subtle_hover
                paint_surface(painter, rect.adjusted(0, 2, 0, -2), fill, None, RADIUS_CONTROL)
            x = rect.left() + SPACE_M
            if entry.icon:
                icon = themed_icon(entry.icon, palette, palette.text_primary, ICON_SIZE)
                icon.paint(painter, int(x), int(rect.center().y() - ICON_SIZE / 2), ICON_SIZE, ICON_SIZE)
                x += ICON_SIZE + SPACE_M
            if not self._compact:
                painter.setFont(body)
                painter.setPen(palette.text_primary)
                metrics = QFontMetrics(body)
                width = int(rect.right() - x - SPACE_S)
                text = metrics.elidedText(entry.text, Qt.TextElideMode.ElideRight, width)
                painter.drawText(
                    QRectF(x, rect.top(), width, rect.height()),
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                    text,
                )
        if self._indicator_y >= 0:
            pill = QRectF(
                SPACE_XS + 1,
                self._indicator_y + (NAV_ITEM_HEIGHT - NAV_INDICATOR_HEIGHT) / 2,
                NAV_INDICATOR_WIDTH,
                NAV_INDICATOR_HEIGHT,
            )
            paint_surface(painter, pill, palette.accent, None, NAV_INDICATOR_WIDTH / 2)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the indicator on the current row."""
        super().resizeEvent(event)
        self._snap_indicator()

    def set_compact(self, *, compact: bool) -> None:
        """Show icons only (`True`) or icons and text."""
        self._compact = compact
        if compact:
            self.setFixedWidth(_NAV_COMPACT_WIDTH)
        else:
            self.setMinimumWidth(_NAV_COMPACT_WIDTH)
            self.setMaximumWidth(_QWIDGETSIZE_MAX)
        self.updateGeometry()
        self.update()

    def set_current(self, key: str) -> None:
        """Select the row with `key` and animate the indicator."""
        entry = self.item(key)
        if entry is None or entry.header:
            return
        changed = key != self._current
        self._current = key
        target = self._row_top(key)
        if target is not None:
            start = self._indicator_y if self._indicator_y >= 0 else target
            self._indicator.stop()
            self._indicator.setStartValue(float(start))
            self._indicator.setEndValue(float(target))
            self._indicator.start()
        self.update()
        if changed:
            self.current_changed.emit(key)

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the expanded width and the height of all rows."""
        rows = len(self._items) + len(self._footer) + 1
        return QSize(_NAV_COMPACT_WIDTH if self._compact else _NAV_EXPANDED_WIDTH, rows * NAV_ITEM_HEIGHT)

    def toggle_compact(self) -> None:
        """Flip compact mode."""
        self.set_compact(compact=not self._compact)

    def _content_top(self) -> int:
        return SPACE_XS + (CONTROL_HEIGHT + SPACE_XS if self._toggle is not None else 0)

    def _key_at(self, y: float) -> str:
        for entry, rect in self._row_rects():
            if not entry.header and rect.top() <= y < rect.bottom():
                return entry.key
        return ""

    def _on_indicator(self, value: object) -> None:
        self._indicator_y = float(value)  # ty: ignore[invalid-argument-type]
        self.update()

    def _row_rects(self) -> list[tuple[NavigationItem, QRectF]]:
        rects: list[tuple[NavigationItem, QRectF]] = []
        y = float(self._content_top())
        width = self.width() - 2 * SPACE_XS
        for entry in self._items:
            height = NAV_ITEM_HEIGHT if not entry.header else (SPACE_L if self._compact else NAV_ITEM_HEIGHT)
            rects.append((entry, QRectF(SPACE_XS, y, width, height)))
            y += height
        bottom = float(self.height() - SPACE_XS)
        for entry in reversed(self._footer):
            bottom -= NAV_ITEM_HEIGHT
            rects.append((entry, QRectF(SPACE_XS, bottom, width, NAV_ITEM_HEIGHT)))
        return rects

    def _row_top(self, key: str) -> float | None:
        for entry, rect in self._row_rects():
            if entry.key == key:
                return rect.top()
        return None

    def _snap_indicator(self) -> None:
        target = self._row_top(self._current) if self._current else None
        self._indicator_y = target if target is not None else -1
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, collapsible: bool = True) -> None
```

Create an empty navigation bar.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, collapsible: bool = True) -> None:
        super().__init__(parent)
        self._items: list[NavigationItem] = []
        self._footer: list[NavigationItem] = []
        self._current = ""
        self._hover = ""
        self._compact = False
        self._indicator_y = -1.0
        self._indicator = QVariantAnimation(self)
        self._indicator.setDuration(ANIMATION_NORMAL)
        self._indicator.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._indicator.valueChanged.connect(self._on_indicator)
        self._scroll_offset = 0
        self.setMouseTracking(True)
        self.setMinimumWidth(_NAV_COMPACT_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        layout.setSpacing(0)
        self._toggle: FluentIconButton | None = None
        if collapsible:
            self._toggle = FluentIconButton("menu", self, tooltip="Toggle navigation")
            self._toggle.clicked.connect(self.toggle_compact)
            layout.addWidget(self._toggle, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `add_footer_item`

```python
def add_footer_item(self, key: str, text: str, *, icon: str = '', data: object = None) -> None
```

Append a row pinned to the bottom (for example Settings).

<details>
<summary>Code:</summary>

```python
def add_footer_item(self, key: str, text: str, *, icon: str = "", data: object = None) -> None:
        self._footer.append(NavigationItem(key, text, icon, data=data))
        self.update()
```

</details>

### ⚙️ Method `add_header`

```python
def add_header(self, text: str) -> None
```

Append a section header row.

<details>
<summary>Code:</summary>

```python
def add_header(self, text: str) -> None:
        self._items.append(NavigationItem(f"__header__{len(self._items)}", text, header=True))
        self.updateGeometry()
        self.update()
```

</details>

### ⚙️ Method `add_item`

```python
def add_item(self, key: str, text: str, *, icon: str = '', data: object = None) -> None
```

Append a navigation row.

<details>
<summary>Code:</summary>

```python
def add_item(self, key: str, text: str, *, icon: str = "", data: object = None) -> None:
        self._items.append(NavigationItem(key, text, icon, data=data))
        if not self._current:
            self._current = key
        self.updateGeometry()
        self.update()
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Remove every row.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        self._items.clear()
        self._current = ""
        self._indicator_y = -1
        self.update()
```

</details>

### ⚙️ Method `current`

```python
def current(self) -> str
```

Return the selected key.

<details>
<summary>Code:</summary>

```python
def current(self) -> str:
        return self._current
```

</details>

### ⚙️ Method `is_compact`

```python
def is_compact(self) -> bool
```

Return whether only icons are shown.

<details>
<summary>Code:</summary>

```python
def is_compact(self) -> bool:
        return self._compact
```

</details>

### ⚙️ Method `item`

```python
def item(self, key: str) -> NavigationItem | None
```

Return the row with `key`.

<details>
<summary>Code:</summary>

```python
def item(self, key: str) -> NavigationItem | None:
        for entry in [*self._items, *self._footer]:
            if entry.key == key:
                return entry
        return None
```

</details>

### ⚙️ Method `items`

```python
def items(self) -> list[NavigationItem]
```

Return the main (non-footer) rows, including headers.

<details>
<summary>Code:</summary>

```python
def items(self) -> list[NavigationItem]:
        return list(self._items)
```

</details>

### ⚙️ Method `leaveEvent`

```python
def leaveEvent(self, event: QEvent) -> None
```

Clear the hover row.

<details>
<summary>Code:</summary>

```python
def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self._hover = ""
        self.update()
        super().leaveEvent(event)
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Track the hovered row.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        key = self._key_at(event.position().y())
        if key != self._hover:
            self._hover = key
            self.update()
        entry = self.item(key) if key else None
        self.setToolTip(entry.text if entry is not None and self._compact else "")
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Select the clicked row; right click requests a context menu.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        key = self._key_at(event.position().y())
        if not key:
            return
        if event.button() == Qt.MouseButton.RightButton:
            self.item_context_menu_requested.emit(key, event.globalPosition().toPoint())
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_current(key)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint rows, headers, selection fill, and the accent indicator.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        body = fluent_font(self.font(), TYPE_BODY)
        header_font = fluent_font(self.font(), TYPE_CAPTION, weight=QFont.Weight.DemiBold)
        for entry, rect in self._row_rects():
            if entry.header:
                if self._compact:
                    painter.fillRect(
                        QRectF(rect.left() + SPACE_S, rect.center().y(), rect.width() - 2 * SPACE_S, 1), palette.divider
                    )
                    continue
                painter.setFont(header_font)
                painter.setPen(palette.text_secondary)
                painter.drawText(
                    rect.adjusted(SPACE_M, 0, -SPACE_S, 0),
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                    entry.text,
                )
                continue
            selected = entry.key == self._current
            if selected or entry.key == self._hover:
                fill = palette.subtle_pressed if selected and entry.key == self._hover else palette.subtle_hover
                paint_surface(painter, rect.adjusted(0, 2, 0, -2), fill, None, RADIUS_CONTROL)
            x = rect.left() + SPACE_M
            if entry.icon:
                icon = themed_icon(entry.icon, palette, palette.text_primary, ICON_SIZE)
                icon.paint(painter, int(x), int(rect.center().y() - ICON_SIZE / 2), ICON_SIZE, ICON_SIZE)
                x += ICON_SIZE + SPACE_M
            if not self._compact:
                painter.setFont(body)
                painter.setPen(palette.text_primary)
                metrics = QFontMetrics(body)
                width = int(rect.right() - x - SPACE_S)
                text = metrics.elidedText(entry.text, Qt.TextElideMode.ElideRight, width)
                painter.drawText(
                    QRectF(x, rect.top(), width, rect.height()),
                    int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                    text,
                )
        if self._indicator_y >= 0:
            pill = QRectF(
                SPACE_XS + 1,
                self._indicator_y + (NAV_ITEM_HEIGHT - NAV_INDICATOR_HEIGHT) / 2,
                NAV_INDICATOR_WIDTH,
                NAV_INDICATOR_HEIGHT,
            )
            paint_surface(painter, pill, palette.accent, None, NAV_INDICATOR_WIDTH / 2)
        painter.end()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep the indicator on the current row.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._snap_indicator()
```

</details>

### ⚙️ Method `set_compact`

```python
def set_compact(self, *, compact: bool) -> None
```

Show icons only (`True`) or icons and text.

<details>
<summary>Code:</summary>

```python
def set_compact(self, *, compact: bool) -> None:
        self._compact = compact
        if compact:
            self.setFixedWidth(_NAV_COMPACT_WIDTH)
        else:
            self.setMinimumWidth(_NAV_COMPACT_WIDTH)
            self.setMaximumWidth(_QWIDGETSIZE_MAX)
        self.updateGeometry()
        self.update()
```

</details>

### ⚙️ Method `set_current`

```python
def set_current(self, key: str) -> None
```

Select the row with `key` and animate the indicator.

<details>
<summary>Code:</summary>

```python
def set_current(self, key: str) -> None:
        entry = self.item(key)
        if entry is None or entry.header:
            return
        changed = key != self._current
        self._current = key
        target = self._row_top(key)
        if target is not None:
            start = self._indicator_y if self._indicator_y >= 0 else target
            self._indicator.stop()
            self._indicator.setStartValue(float(start))
            self._indicator.setEndValue(float(target))
            self._indicator.start()
        self.update()
        if changed:
            self.current_changed.emit(key)
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return the expanded width and the height of all rows.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        rows = len(self._items) + len(self._footer) + 1
        return QSize(_NAV_COMPACT_WIDTH if self._compact else _NAV_EXPANDED_WIDTH, rows * NAV_ITEM_HEIGHT)
```

</details>

### ⚙️ Method `toggle_compact`

```python
def toggle_compact(self) -> None
```

Flip compact mode.

<details>
<summary>Code:</summary>

```python
def toggle_compact(self) -> None:
        self.set_compact(compact=not self._compact)
```

</details>

## 🏛️ Class `FluentNavigationPanel`

```python
class FluentNavigationPanel(QWidget)
```

[`FluentNavigationBar`](#%EF%B8%8F-class-fluentnavigationbar) on the left of a stack of pages in a scroll area.

<details>
<summary>Code:</summary>

```python
class FluentNavigationPanel(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a navigation panel."""
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.navigation = FluentNavigationBar(self)
        self.navigation.setFixedWidth(_NAV_EXPANDED_WIDTH - 64)
        self.stack = QStackedWidget(self)
        row.addWidget(self.navigation)
        row.addWidget(self.stack, 1)
        self._pages: dict[str, QWidget] = {}
        self.navigation.current_changed.connect(self._show)

    def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = "") -> None:
        """Register a page and its navigation row."""
        scroll = FluentScrollArea(self.stack)
        scroll.setWidget(widget)
        self._pages[key] = scroll
        self.stack.addWidget(scroll)
        self.navigation.add_item(key, text, icon=icon)
        if len(self._pages) == 1:
            self.stack.setCurrentWidget(scroll)

    def _show(self, key: str) -> None:
        page = self._pages.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a navigation panel.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.navigation = FluentNavigationBar(self)
        self.navigation.setFixedWidth(_NAV_EXPANDED_WIDTH - 64)
        self.stack = QStackedWidget(self)
        row.addWidget(self.navigation)
        row.addWidget(self.stack, 1)
        self._pages: dict[str, QWidget] = {}
        self.navigation.current_changed.connect(self._show)
```

</details>

### ⚙️ Method `add_page`

```python
def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = '') -> None
```

Register a page and its navigation row.

<details>
<summary>Code:</summary>

```python
def add_page(self, key: str, text: str, widget: QWidget, *, icon: str = "") -> None:
        scroll = FluentScrollArea(self.stack)
        scroll.setWidget(widget)
        self._pages[key] = scroll
        self.stack.addWidget(scroll)
        self.navigation.add_item(key, text, icon=icon)
        if len(self._pages) == 1:
            self.stack.setCurrentWidget(scroll)
```

</details>

## 🏛️ Class `FluentPagination`

```python
class FluentPagination(QWidget)
```

Page selector: previous / numbered pages with ellipses / next.

<details>
<summary>Code:</summary>

```python
class FluentPagination(QWidget):

    page_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, pages: int = 1) -> None:
        """Create a pagination control (pages are 1-based)."""
        super().__init__(parent)
        self._pages = max(1, pages)
        self._current = 1
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(SPACE_XS)
        self._rebuild()

    def current(self) -> int:
        """Return the current page (1-based)."""
        return self._current

    def page_count(self) -> int:
        """Return the number of pages."""
        return self._pages

    def set_current(self, page: int) -> None:
        """Go to `page` (clamped)."""
        page = max(1, min(self._pages, page))
        if page == self._current:
            return
        self._current = page
        self._rebuild()
        self.page_changed.emit(page)

    def set_page_count(self, pages: int) -> None:
        """Change the number of pages."""
        self._pages = max(1, pages)
        self._current = min(self._current, self._pages)
        self._rebuild()

    def visible_pages(self) -> list[int]:
        """Return page numbers to show (`0` = ellipsis)."""
        pages = {1, self._pages, *range(self._current - _PAGINATION_WINDOW, self._current + _PAGINATION_WINDOW + 1)}
        ordered = sorted(page for page in pages if 1 <= page <= self._pages)
        result: list[int] = []
        for page in ordered:
            if result and page - result[-1] > 1:
                result.append(0)
            result.append(page)
        return result

    def _rebuild(self) -> None:
        while self._row.count():
            item = self._row.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        previous = FluentIconButton("chevron-left", self, tooltip="Previous")
        previous.setEnabled(self._current > 1)
        previous.clicked.connect(lambda: self.set_current(self._current - 1))
        self._row.addWidget(previous)
        for page in self.visible_pages():
            if page == 0:
                self._row.addWidget(FluentText("…", self, role=TextRole.SECONDARY))
                continue
            button = FluentTransparentButton(str(page), self)
            button.setCheckable(True)
            button.setChecked(page == self._current)
            button.setFixedWidth(CONTROL_HEIGHT + SPACE_S)
            button.clicked.connect(lambda _checked=False, target=page: self.set_current(target))
            self._row.addWidget(button)
        following = FluentIconButton("chevron-right", self, tooltip="Next")
        following.setEnabled(self._current < self._pages)
        following.clicked.connect(lambda: self.set_current(self._current + 1))
        self._row.addWidget(following)
        self._row.addStretch(1)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, pages: int = 1) -> None
```

Create a pagination control (pages are 1-based).

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, pages: int = 1) -> None:
        super().__init__(parent)
        self._pages = max(1, pages)
        self._current = 1
        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setSpacing(SPACE_XS)
        self._rebuild()
```

</details>

### ⚙️ Method `current`

```python
def current(self) -> int
```

Return the current page (1-based).

<details>
<summary>Code:</summary>

```python
def current(self) -> int:
        return self._current
```

</details>

### ⚙️ Method `page_count`

```python
def page_count(self) -> int
```

Return the number of pages.

<details>
<summary>Code:</summary>

```python
def page_count(self) -> int:
        return self._pages
```

</details>

### ⚙️ Method `set_current`

```python
def set_current(self, page: int) -> None
```

Go to `page` (clamped).

<details>
<summary>Code:</summary>

```python
def set_current(self, page: int) -> None:
        page = max(1, min(self._pages, page))
        if page == self._current:
            return
        self._current = page
        self._rebuild()
        self.page_changed.emit(page)
```

</details>

### ⚙️ Method `set_page_count`

```python
def set_page_count(self, pages: int) -> None
```

Change the number of pages.

<details>
<summary>Code:</summary>

```python
def set_page_count(self, pages: int) -> None:
        self._pages = max(1, pages)
        self._current = min(self._current, self._pages)
        self._rebuild()
```

</details>

### ⚙️ Method `visible_pages`

```python
def visible_pages(self) -> list[int]
```

Return page numbers to show (`0` = ellipsis).

<details>
<summary>Code:</summary>

```python
def visible_pages(self) -> list[int]:
        pages = {1, self._pages, *range(self._current - _PAGINATION_WINDOW, self._current + _PAGINATION_WINDOW + 1)}
        ordered = sorted(page for page in pages if 1 <= page <= self._pages)
        result: list[int] = []
        for page in ordered:
            if result and page - result[-1] > 1:
                result.append(0)
            result.append(page)
        return result
```

</details>

## 🏛️ Class `FluentPivot`

```python
class FluentPivot(QWidget)
```

Top text tabs with an accent underline that slides between items.

<details>
<summary>Code:</summary>

```python
class FluentPivot(QWidget):

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        """Create a pivot."""
        super().__init__(parent)
        self._items = list(items)
        self._current = 0
        self._hover = -1
        self._line_x = -1.0
        self._line_width = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation)
        self.setMouseTracking(True)
        self.setFixedHeight(CONTROL_HEIGHT + SPACE_M)
        bind_theme(self, self.update)

    def add_item(self, text: str) -> None:
        """Append a tab."""
        self._items.append(text)
        self.update()

    def current(self) -> int:
        """Return the selected index."""
        return self._current

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Track the hovered tab."""
        index = self._index_at(event.position().x())
        if index != self._hover:
            self._hover = index
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select the clicked tab."""
        index = self._index_at(event.position().x())
        if index >= 0:
            self.set_current(index)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint tab texts and the underline."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_BODY_LARGE)
        painter.setFont(font)
        rects = self._rects(QFontMetrics(font))
        for index, (text, rect) in enumerate(zip(self._items, rects, strict=True)):
            if index in (self._current, self._hover):
                painter.setPen(palette.text_primary)
            else:
                painter.setPen(palette.text_secondary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        if rects and 0 <= self._current < len(rects):
            if self._line_x < 0:
                self._line_x = rects[self._current].center().x()
            line = QRectF(self._line_x - 8, self.height() - 3, 16, 3)
            paint_surface(painter, line, palette.accent, None, 1.5)
        painter.end()

    def set_current(self, index: int) -> None:
        """Select a tab and slide the underline."""
        if not 0 <= index < len(self._items) or index == self._current:
            return
        rects = self._rects(QFontMetrics(fluent_font(self.font(), TYPE_BODY_LARGE)))
        self._animation.stop()
        self._animation.setStartValue(rects[self._current].center().x())
        self._animation.setEndValue(rects[index].center().x())
        self._animation.start()
        self._current = index
        self.update()
        self.current_changed.emit(index)

    def _index_at(self, x: float) -> int:
        for index, rect in enumerate(self._rects(QFontMetrics(fluent_font(self.font(), TYPE_BODY_LARGE)))):
            if rect.left() <= x <= rect.right():
                return index
        return -1

    def _on_animation(self, value: object) -> None:
        self._line_x = float(value)  # ty: ignore[invalid-argument-type]
        self.update()

    def _rects(self, metrics: QFontMetrics) -> list[QRectF]:
        rects: list[QRectF] = []
        x = 0.0
        for text in self._items:
            width = metrics.horizontalAdvance(text) + 2 * SPACE_M
            rects.append(QRectF(x, 0, width, self.height() - 3))
            x += width
        return rects
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None
```

Create a pivot.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = ()) -> None:
        super().__init__(parent)
        self._items = list(items)
        self._current = 0
        self._hover = -1
        self._line_x = -1.0
        self._line_width = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(ANIMATION_NORMAL)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation)
        self.setMouseTracking(True)
        self.setFixedHeight(CONTROL_HEIGHT + SPACE_M)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `add_item`

```python
def add_item(self, text: str) -> None
```

Append a tab.

<details>
<summary>Code:</summary>

```python
def add_item(self, text: str) -> None:
        self._items.append(text)
        self.update()
```

</details>

### ⚙️ Method `current`

```python
def current(self) -> int
```

Return the selected index.

<details>
<summary>Code:</summary>

```python
def current(self) -> int:
        return self._current
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Track the hovered tab.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        index = self._index_at(event.position().x())
        if index != self._hover:
            self._hover = index
            self.update()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Select the clicked tab.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        index = self._index_at(event.position().x())
        if index >= 0:
            self.set_current(index)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint tab texts and the underline.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_BODY_LARGE)
        painter.setFont(font)
        rects = self._rects(QFontMetrics(font))
        for index, (text, rect) in enumerate(zip(self._items, rects, strict=True)):
            if index in (self._current, self._hover):
                painter.setPen(palette.text_primary)
            else:
                painter.setPen(palette.text_secondary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        if rects and 0 <= self._current < len(rects):
            if self._line_x < 0:
                self._line_x = rects[self._current].center().x()
            line = QRectF(self._line_x - 8, self.height() - 3, 16, 3)
            paint_surface(painter, line, palette.accent, None, 1.5)
        painter.end()
```

</details>

### ⚙️ Method `set_current`

```python
def set_current(self, index: int) -> None
```

Select a tab and slide the underline.

<details>
<summary>Code:</summary>

```python
def set_current(self, index: int) -> None:
        if not 0 <= index < len(self._items) or index == self._current:
            return
        rects = self._rects(QFontMetrics(fluent_font(self.font(), TYPE_BODY_LARGE)))
        self._animation.stop()
        self._animation.setStartValue(rects[self._current].center().x())
        self._animation.setEndValue(rects[index].center().x())
        self._animation.start()
        self._current = index
        self.update()
        self.current_changed.emit(index)
```

</details>

## 🏛️ Class `FluentSplitter`

```python
class FluentSplitter(QSplitter)
```

Splitter with a thin hairline handle that turns accent on hover.

<details>
<summary>Code:</summary>

```python
class FluentSplitter(QSplitter):

    def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None) -> None:
        """Create a splitter."""
        super().__init__(orientation, parent)
        self.setHandleWidth(SPACE_XS + 1)
        self.setChildrenCollapsible(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-color the handle."""
        palette = palette_for(self)
        self.setStyleSheet(
            f"QSplitter::handle {{ background: transparent; margin: 2px; }}"
            f" QSplitter::handle:hover {{ background: {css(palette.accent)}; border-radius: 1px; }}",
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None) -> None
```

Create a splitter.

<details>
<summary>Code:</summary>

```python
def __init__(self, orientation: Qt.Orientation = Qt.Orientation.Horizontal, parent: QWidget | None = None) -> None:
        super().__init__(orientation, parent)
        self.setHandleWidth(SPACE_XS + 1)
        self.setChildrenCollapsible(False)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-color the handle.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        self.setStyleSheet(
            f"QSplitter::handle {{ background: transparent; margin: 2px; }}"
            f" QSplitter::handle:hover {{ background: {css(palette.accent)}; border-radius: 1px; }}",
        )
```

</details>

## 🏛️ Class `FluentTabBar`

```python
class FluentTabBar(QTabBar)
```

Document tabs: rounded top corners, selected tab joins the content surface.

<details>
<summary>Code:</summary>

```python
class FluentTabBar(QTabBar):

    def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None:
        """Create a tab bar."""
        super().__init__(parent)
        self.setTabsClosable(closable)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setExpanding(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setDrawBase(False)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply tab chrome."""
        palette = palette_for(self)
        close = lucide_qss_url("x", palette.text_secondary, 12)
        self.setStyleSheet(f"""
QTabBar {{ background: transparent; }}
QTabBar::tab {{
    background: transparent;
    color: {css(palette.text_secondary)};
    border: 1px solid transparent;
    border-top-left-radius: {RADIUS_CARD}px;
    border-top-right-radius: {RADIUS_CARD}px;
    padding: 0px 12px;
    min-height: {CONTROL_HEIGHT}px;
    min-width: 96px;
    max-width: 240px;
}}
QTabBar::tab:hover {{ background: {css(palette.subtle_hover)}; color: {css(palette.text_primary)}; }}
QTabBar::tab:selected {{
    background: {css(palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg)};
    color: {css(palette.text_primary)};
    border-color: {css(palette.card_stroke)};
    border-bottom-color: transparent;
}}
QTabBar::close-button {{
    image: url("{close}"); subcontrol-position: right; border-radius: {RADIUS_CONTROL}px;
    width: 16px; height: 16px; padding: 2px;
}}
QTabBar::close-button:hover {{ background: {css(palette.subtle_hover)}; }}
""")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None
```

Create a tab bar.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None:
        super().__init__(parent)
        self.setTabsClosable(closable)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setExpanding(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.setDrawBase(False)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply tab chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        close = lucide_qss_url("x", palette.text_secondary, 12)
        self.setStyleSheet(f"""
QTabBar {{ background: transparent; }}
QTabBar::tab {{
    background: transparent;
    color: {css(palette.text_secondary)};
    border: 1px solid transparent;
    border-top-left-radius: {RADIUS_CARD}px;
    border-top-right-radius: {RADIUS_CARD}px;
    padding: 0px 12px;
    min-height: {CONTROL_HEIGHT}px;
    min-width: 96px;
    max-width: 240px;
}}
QTabBar::tab:hover {{ background: {css(palette.subtle_hover)}; color: {css(palette.text_primary)}; }}
QTabBar::tab:selected {{
    background: {css(palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg)};
    color: {css(palette.text_primary)};
    border-color: {css(palette.card_stroke)};
    border-bottom-color: transparent;
}}
QTabBar::close-button {{
    image: url("{close}"); subcontrol-position: right; border-radius: {RADIUS_CONTROL}px;
    width: 16px; height: 16px; padding: 2px;
}}
QTabBar::close-button:hover {{ background: {css(palette.subtle_hover)}; }}
""")
```

</details>

## 🏛️ Class `FluentTabWidget`

```python
class FluentTabWidget(QWidget)
```

[`FluentTabBar`](#%EF%B8%8F-class-fluenttabbar) over a stacked content surface.

<details>
<summary>Code:</summary>

```python
class FluentTabWidget(QWidget):

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None:
        """Create a tab widget."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.tab_bar = FluentTabBar(self, closable=closable)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stack, 1)
        self.tab_bar.currentChanged.connect(self._on_current)
        self.tab_bar.tabCloseRequested.connect(self.remove_tab)
        self.tab_bar.tabMoved.connect(self._on_moved)
        bind_theme(self, self.refresh_theme)

    def add_tab(self, widget: QWidget, text: str, *, icon: str = "") -> int:
        """Append a page and return its index."""
        self.stack.addWidget(widget)
        index = self.tab_bar.addTab(text)
        if icon:
            self.tab_bar.setTabIcon(index, themed_icon(icon, palette_for(self)))
        return index

    def count(self) -> int:
        """Return the number of pages."""
        return self.stack.count()

    def current_index(self) -> int:
        """Return the selected page index."""
        return self.tab_bar.currentIndex()

    def refresh_theme(self) -> None:
        """Re-color the content surface."""
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self.stack.setObjectName("FluentTabStack")
        self.stack.setStyleSheet(
            f"QStackedWidget#FluentTabStack {{ background: {css(fill)}; border: 1px solid {css(palette.card_stroke)};"
            f" border-top-right-radius: {RADIUS_CARD}px; border-bottom-left-radius: {RADIUS_CARD}px;"
            f" border-bottom-right-radius: {RADIUS_CARD}px; }}",
        )

    def remove_tab(self, index: int) -> None:
        """Close the page at `index`."""
        widget = self.stack.widget(index)
        self.tab_bar.removeTab(index)
        if widget is not None:
            self.stack.removeWidget(widget)
            widget.deleteLater()

    def set_current_index(self, index: int) -> None:
        """Select a page."""
        self.tab_bar.setCurrentIndex(index)

    def _on_current(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.current_changed.emit(index)

    def _on_moved(self, source: int, target: int) -> None:
        widget = self.stack.widget(source)
        if widget is None:
            return
        self.stack.removeWidget(widget)
        self.stack.insertWidget(target, widget)
        self.stack.setCurrentIndex(self.tab_bar.currentIndex())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None
```

Create a tab widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, closable: bool = True) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.tab_bar = FluentTabBar(self, closable=closable)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.stack, 1)
        self.tab_bar.currentChanged.connect(self._on_current)
        self.tab_bar.tabCloseRequested.connect(self.remove_tab)
        self.tab_bar.tabMoved.connect(self._on_moved)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `add_tab`

```python
def add_tab(self, widget: QWidget, text: str, *, icon: str = '') -> int
```

Append a page and return its index.

<details>
<summary>Code:</summary>

```python
def add_tab(self, widget: QWidget, text: str, *, icon: str = "") -> int:
        self.stack.addWidget(widget)
        index = self.tab_bar.addTab(text)
        if icon:
            self.tab_bar.setTabIcon(index, themed_icon(icon, palette_for(self)))
        return index
```

</details>

### ⚙️ Method `count`

```python
def count(self) -> int
```

Return the number of pages.

<details>
<summary>Code:</summary>

```python
def count(self) -> int:
        return self.stack.count()
```

</details>

### ⚙️ Method `current_index`

```python
def current_index(self) -> int
```

Return the selected page index.

<details>
<summary>Code:</summary>

```python
def current_index(self) -> int:
        return self.tab_bar.currentIndex()
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-color the content surface.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self.stack.setObjectName("FluentTabStack")
        self.stack.setStyleSheet(
            f"QStackedWidget#FluentTabStack {{ background: {css(fill)}; border: 1px solid {css(palette.card_stroke)};"
            f" border-top-right-radius: {RADIUS_CARD}px; border-bottom-left-radius: {RADIUS_CARD}px;"
            f" border-bottom-right-radius: {RADIUS_CARD}px; }}",
        )
```

</details>

### ⚙️ Method `remove_tab`

```python
def remove_tab(self, index: int) -> None
```

Close the page at `index`.

<details>
<summary>Code:</summary>

```python
def remove_tab(self, index: int) -> None:
        widget = self.stack.widget(index)
        self.tab_bar.removeTab(index)
        if widget is not None:
            self.stack.removeWidget(widget)
            widget.deleteLater()
```

</details>

### ⚙️ Method `set_current_index`

```python
def set_current_index(self, index: int) -> None
```

Select a page.

<details>
<summary>Code:</summary>

```python
def set_current_index(self, index: int) -> None:
        self.tab_bar.setCurrentIndex(index)
```

</details>

## 🏛️ Class `NavigationItem`

```python
class NavigationItem
```

One entry of [`FluentNavigationBar`](#%EF%B8%8F-class-fluentnavigationbar) (or a header when `header` is set).

<details>
<summary>Code:</summary>

```python
class NavigationItem:

    key: str
    text: str
    icon: str = ""
    header: bool = False
    data: object = None
    children: list[NavigationItem] = field(default_factory=list)
```

</details>
