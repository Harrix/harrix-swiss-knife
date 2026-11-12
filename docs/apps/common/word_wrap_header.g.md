---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `word_wrap_header.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `WordWrapHeaderView`](#%EF%B8%8F-class-wordwrapheaderview)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `leaveEvent`](#%EF%B8%8F-method-leaveevent)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `paintSection`](#%EF%B8%8F-method-paintsection)
  - [⚙️ Method `refresh_wrapped_height`](#%EF%B8%8F-method-refresh_wrapped_height)
  - [⚙️ Method `sectionSizeFromContents`](#%EF%B8%8F-method-sectionsizefromcontents)
  - [⚙️ Method `setModel`](#%EF%B8%8F-method-setmodel)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `viewportEvent`](#%EF%B8%8F-method-viewportevent)
- [🔧 Function `install_word_wrap_header`](#-function-install_word_wrap_header)
- [🔧 Function `install_word_wrap_headers`](#-function-install_word_wrap_headers)
- [🔧 Function `wrapped_header_text_size`](#-function-wrapped_header_text_size)

</details>

## 🏛️ Class `WordWrapHeaderView`

```python
class WordWrapHeaderView(QHeaderView)
```

`QHeaderView` that paints and sizes section titles with word wrap.

<details>
<summary>Code:</summary>

```python
class WordWrapHeaderView(QHeaderView):

    def __init__(
        self,
        orientation: Qt.Orientation,
        parent: QWidget | None = None,
        *,
        wrap_width: int | None = None,
        wrap_first_section: bool = False,
    ) -> None:
        """Create a wrapping header.

        Args:

        - `orientation` (`Qt.Orientation`): Header orientation.
        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `wrap_width` (`int | None`): Preferred wrap width for compact columns. Defaults to `None`.
        - `wrap_first_section` (`bool`): Also wrap the first section. Defaults to `False`.

        """
        super().__init__(orientation, parent)
        self._wrap_width = wrap_width
        self._wrap_first_section = wrap_first_section
        self._updating_height = False
        self._hover_boundary_x: int | None = None
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.sectionResized.connect(self._on_section_resized)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Hide the column-boundary mark when the pointer leaves the header."""
        self._set_hover_boundary(None)
        super().leaveEvent(event)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Use the wrapped height as the minimum header size."""
        return self.sizeHint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Show a vertical mark and resize cursor on the boundary between columns."""
        super().mouseMoveEvent(event)
        boundary = self._boundary_x_at(int(event.position().x()))
        self._set_hover_boundary(boundary)
        if boundary is not None:
            self.setCursor(Qt.CursorShape.SplitHCursor)
        elif self.cursor().shape() == Qt.CursorShape.SplitHCursor:
            self.unsetCursor()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Paint wrapped titles, then the hovered column boundary."""
        super().paintEvent(event)
        if self._hover_boundary_x is None:
            return
        painter = QPainter(self.viewport())
        grip = MUTED_TEXT
        with contextlib.suppress(Exception):
            palette = FluentTheme.instance().palette()
            grip = css(mix(palette.window_bg, palette.text_secondary))
        painter.setPen(QPen(QColor(grip), 1))
        x = self._hover_boundary_x
        height = self.viewport().height()
        inset = min(_BOUNDARY_INSET_PX, max((height - 8) // 2, 0))
        painter.drawLine(x, inset, x, max(inset, height - inset - 1))
        painter.end()

    def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        """Paint the section from the header palette, then draw the wrapped title.

        Custom painting must not call `CE_Header`: under Fluent window QSS that
        control often fills white even when the header palette is dark.

        """
        if not rect.isValid():
            return

        option = QStyleOptionHeader()
        self.initStyleOption(option)
        self.initStyleOptionForIndex(option, logical_index)
        palette = option.palette
        fill = palette.color(QPalette.ColorRole.Button)
        ink = palette.color(QPalette.ColorRole.ButtonText)

        painter.save()
        painter.fillRect(rect, fill)
        hairline = QColor(ink)
        hairline.setAlpha(64)
        painter.setPen(QPen(hairline, 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        icon = self._section_icon(logical_index)
        text_top = 2
        if not icon.isNull():
            pixmap = icon.pixmap(_HEADER_ICON_SIZE, _HEADER_ICON_SIZE)
            icon_x = rect.x() + (rect.width() - pixmap.width()) // 2
            icon_y = rect.y() + _HEADER_ICON_TOP
            painter.drawPixmap(icon_x, icon_y, pixmap)
            text_top = _HEADER_ICON_TOP + pixmap.height() + _HEADER_ICON_GAP

        text = self._section_text(logical_index)
        if text:
            painter.setPen(ink)
            painter.drawText(
                rect.adjusted(_TEXT_INSET, text_top, -_TEXT_INSET, -2),
                int(HEADER_TEXT_FLAGS),
                text,
            )
        painter.restore()

    def refresh_wrapped_height(self) -> None:
        """Recalculate header height from the current section widths."""
        if self._updating_height:
            return
        self._updating_height = True
        try:
            self.updateGeometries()
        finally:
            self._updating_height = False

    def sectionSizeFromContents(self, logical_index: int) -> QSize:  # noqa: N802
        """Prefer a compact wrapped width when `wrap_width` is set."""
        if not self._should_wrap_section(logical_index) or self._wrap_width is None:
            return super().sectionSizeFromContents(logical_index)
        return wrapped_header_text_size(self._section_text(logical_index), self._wrap_width, self.fontMetrics())

    def setModel(self, model: QAbstractItemModel | None) -> None:  # noqa: N802
        """Refresh wrapped height after the header model is assigned."""
        super().setModel(model)
        self.refresh_wrapped_height()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Grow vertically so wrapped titles stay visible."""
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), self._max_wrapped_height()))

    def viewportEvent(self, event: QEvent) -> bool:  # noqa: N802
        """Clear the boundary mark when the pointer leaves the header viewport."""
        handled = super().viewportEvent(event)
        if event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
            self._set_hover_boundary(None)
            if self.cursor().shape() == Qt.CursorShape.SplitHCursor:
                self.unsetCursor()
        return handled

    def _boundary_x_at(self, viewport_x: int) -> int | None:
        """Return the position of an interactive section edge near the pointer."""
        last = self.count() - 1
        for logical in range(self.count()):
            if self.isSectionHidden(logical) or logical == last:
                continue
            if self.sectionResizeMode(logical) != QHeaderView.ResizeMode.Interactive:
                continue
            right = self.sectionViewportPosition(logical) + self.sectionSize(logical)
            if abs(viewport_x - right) <= _BOUNDARY_GRIP_PX:
                return right
        return None

    def _max_wrapped_height(self) -> int:
        if self.count() == 0:
            return 0
        max_height = 0
        for logical_index in range(self.count()):
            width = self.sectionSize(logical_index)
            if width <= 0 and self._wrap_width is not None and self._should_wrap_section(logical_index):
                width = self._wrap_width
            if width <= 0:
                continue
            text_height = wrapped_header_text_size(
                self._section_text(logical_index),
                width,
                self.fontMetrics(),
            ).height()
            icon_extra = 0
            if not self._section_icon(logical_index).isNull():
                icon_extra = _HEADER_ICON_TOP + _HEADER_ICON_SIZE + _HEADER_ICON_GAP
            max_height = max(max_height, text_height + icon_extra)
        return max_height

    def _on_section_resized(self, _logical_index: int, _old_size: int, _new_size: int) -> None:
        self.refresh_wrapped_height()

    def _section_icon(self, logical_index: int) -> QIcon:
        model = self.model()
        if model is None:
            return QIcon()
        value = model.headerData(logical_index, self.orientation(), Qt.ItemDataRole.DecorationRole)
        return value if isinstance(value, QIcon) else QIcon()

    def _section_text(self, logical_index: int) -> str:
        model = self.model()
        if model is None:
            return ""
        value = model.headerData(logical_index, self.orientation(), Qt.ItemDataRole.DisplayRole)
        return "" if value is None else str(value)

    def _set_hover_boundary(self, boundary_x: int | None) -> None:
        if boundary_x == self._hover_boundary_x:
            return
        self._hover_boundary_x = boundary_x
        self.viewport().update()

    def _should_wrap_section(self, logical_index: int) -> bool:
        return self._wrap_first_section or logical_index > 0
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, orientation: Qt.Orientation, parent: QWidget | None = None, *, wrap_width: int | None = None, wrap_first_section: bool = False) -> None
```

Create a wrapping header.

Args:

- `orientation` (`Qt.Orientation`): Header orientation.
- [`parent`](../finance/transaction_day_headers.g.md#%EF%B8%8F-method-parent) (`QWidget | None`): Parent widget. Defaults to `None`.
- `wrap_width` (`int | None`): Preferred wrap width for compact columns. Defaults to `None`.
- `wrap_first_section` (`bool`): Also wrap the first section. Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        orientation: Qt.Orientation,
        parent: QWidget | None = None,
        *,
        wrap_width: int | None = None,
        wrap_first_section: bool = False,
    ) -> None:
        super().__init__(orientation, parent)
        self._wrap_width = wrap_width
        self._wrap_first_section = wrap_first_section
        self._updating_height = False
        self._hover_boundary_x: int | None = None
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.sectionResized.connect(self._on_section_resized)
```

</details>

### ⚙️ Method `leaveEvent`

```python
def leaveEvent(self, event: QEvent) -> None
```

Hide the column-boundary mark when the pointer leaves the header.

<details>
<summary>Code:</summary>

```python
def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self._set_hover_boundary(None)
        super().leaveEvent(event)
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Use the wrapped height as the minimum header size.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return self.sizeHint()
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Show a vertical mark and resize cursor on the boundary between columns.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        super().mouseMoveEvent(event)
        boundary = self._boundary_x_at(int(event.position().x()))
        self._set_hover_boundary(boundary)
        if boundary is not None:
            self.setCursor(Qt.CursorShape.SplitHCursor)
        elif self.cursor().shape() == Qt.CursorShape.SplitHCursor:
            self.unsetCursor()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Paint wrapped titles, then the hovered column boundary.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        super().paintEvent(event)
        if self._hover_boundary_x is None:
            return
        painter = QPainter(self.viewport())
        grip = MUTED_TEXT
        with contextlib.suppress(Exception):
            palette = FluentTheme.instance().palette()
            grip = css(mix(palette.window_bg, palette.text_secondary))
        painter.setPen(QPen(QColor(grip), 1))
        x = self._hover_boundary_x
        height = self.viewport().height()
        inset = min(_BOUNDARY_INSET_PX, max((height - 8) // 2, 0))
        painter.drawLine(x, inset, x, max(inset, height - inset - 1))
        painter.end()
```

</details>

### ⚙️ Method `paintSection`

```python
def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None
```

Paint the section from the header palette, then draw the wrapped title.

Custom painting must not call `CE_Header`: under Fluent window QSS that
control often fills white even when the header palette is dark.

<details>
<summary>Code:</summary>

```python
def paintSection(self, painter: QPainter, rect: QRect, logical_index: int) -> None:  # noqa: N802
        if not rect.isValid():
            return

        option = QStyleOptionHeader()
        self.initStyleOption(option)
        self.initStyleOptionForIndex(option, logical_index)
        palette = option.palette
        fill = palette.color(QPalette.ColorRole.Button)
        ink = palette.color(QPalette.ColorRole.ButtonText)

        painter.save()
        painter.fillRect(rect, fill)
        hairline = QColor(ink)
        hairline.setAlpha(64)
        painter.setPen(QPen(hairline, 1))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        icon = self._section_icon(logical_index)
        text_top = 2
        if not icon.isNull():
            pixmap = icon.pixmap(_HEADER_ICON_SIZE, _HEADER_ICON_SIZE)
            icon_x = rect.x() + (rect.width() - pixmap.width()) // 2
            icon_y = rect.y() + _HEADER_ICON_TOP
            painter.drawPixmap(icon_x, icon_y, pixmap)
            text_top = _HEADER_ICON_TOP + pixmap.height() + _HEADER_ICON_GAP

        text = self._section_text(logical_index)
        if text:
            painter.setPen(ink)
            painter.drawText(
                rect.adjusted(_TEXT_INSET, text_top, -_TEXT_INSET, -2),
                int(HEADER_TEXT_FLAGS),
                text,
            )
        painter.restore()
```

</details>

### ⚙️ Method `refresh_wrapped_height`

```python
def refresh_wrapped_height(self) -> None
```

Recalculate header height from the current section widths.

<details>
<summary>Code:</summary>

```python
def refresh_wrapped_height(self) -> None:
        if self._updating_height:
            return
        self._updating_height = True
        try:
            self.updateGeometries()
        finally:
            self._updating_height = False
```

</details>

### ⚙️ Method `sectionSizeFromContents`

```python
def sectionSizeFromContents(self, logical_index: int) -> QSize
```

Prefer a compact wrapped width when `wrap_width` is set.

<details>
<summary>Code:</summary>

```python
def sectionSizeFromContents(self, logical_index: int) -> QSize:  # noqa: N802
        if not self._should_wrap_section(logical_index) or self._wrap_width is None:
            return super().sectionSizeFromContents(logical_index)
        return wrapped_header_text_size(self._section_text(logical_index), self._wrap_width, self.fontMetrics())
```

</details>

### ⚙️ Method `setModel`

```python
def setModel(self, model: QAbstractItemModel | None) -> None
```

Refresh wrapped height after the header model is assigned.

<details>
<summary>Code:</summary>

```python
def setModel(self, model: QAbstractItemModel | None) -> None:  # noqa: N802
        super().setModel(model)
        self.refresh_wrapped_height()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Grow vertically so wrapped titles stay visible.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), self._max_wrapped_height()))
```

</details>

### ⚙️ Method `viewportEvent`

```python
def viewportEvent(self, event: QEvent) -> bool
```

Clear the boundary mark when the pointer leaves the header viewport.

<details>
<summary>Code:</summary>

```python
def viewportEvent(self, event: QEvent) -> bool:  # noqa: N802
        handled = super().viewportEvent(event)
        if event.type() in {QEvent.Type.Leave, QEvent.Type.HoverLeave}:
            self._set_hover_boundary(None)
            if self.cursor().shape() == Qt.CursorShape.SplitHCursor:
                self.unsetCursor()
        return handled
```

</details>

## 🔧 Function `install_word_wrap_header`

```python
def install_word_wrap_header(table: QTableView, *, wrap_width: int | None = None, wrap_first_section: bool = True) -> WordWrapHeaderView
```

Replace a table's horizontal header with a wrapping header.

Existing clickable, stretch, and size settings are copied from the current header.

Args:

- `table` (`QTableView`): Table whose header should wrap.
- `wrap_width` (`int | None`): Preferred wrap width for compact columns. Defaults to `None`.
- `wrap_first_section` (`bool`): Also wrap the first section. Defaults to `True`.

Returns:

- [`WordWrapHeaderView`](#%EF%B8%8F-class-wordwrapheaderview): The header now used by `table`.

<details>
<summary>Code:</summary>

```python
def install_word_wrap_header(
    table: QTableView,
    *,
    wrap_width: int | None = None,
    wrap_first_section: bool = True,
) -> WordWrapHeaderView:
    current = table.horizontalHeader()
    if isinstance(current, WordWrapHeaderView):
        return current

    header = WordWrapHeaderView(
        Qt.Orientation.Horizontal,
        table,
        wrap_width=wrap_width,
        wrap_first_section=wrap_first_section,
    )
    if current is not None:
        header.setSectionsClickable(current.sectionsClickable())
        header.setHighlightSections(current.highlightSections())
        header.setStretchLastSection(current.stretchLastSection())
        header.setSortIndicatorShown(current.isSortIndicatorShown())
        header.setDefaultAlignment(current.defaultAlignment())
        header.setMinimumSectionSize(current.minimumSectionSize())
        header.setDefaultSectionSize(current.defaultSectionSize())
        header.setSectionsMovable(current.sectionsMovable())
    header.setTextElideMode(Qt.TextElideMode.ElideNone)
    table.setHorizontalHeader(header)
    # New headers start on the system light palette; restore Fluent dark chrome.
    if is_fluent_themed(table):
        from harrix_swiss_knife.fluent.app_chrome import style_fluent_table  # noqa: PLC0415

        style_fluent_table(table)
    return header
```

</details>

## 🔧 Function `install_word_wrap_headers`

```python
def install_word_wrap_headers(parent: QWidget, *, skip: set[QTableView] | frozenset[QTableView] | None = None, wrap_first_section: bool = True) -> None
```

Install wrapping headers on every `QTableView` under [`parent`](../finance/transaction_day_headers.g.md#%EF%B8%8F-method-parent).

<details>
<summary>Code:</summary>

```python
def install_word_wrap_headers(
    parent: QWidget,
    *,
    skip: set[QTableView] | frozenset[QTableView] | None = None,
    wrap_first_section: bool = True,
) -> None:
    skipped = skip or set()
    for table in parent.findChildren(QTableView):
        if table in skipped:
            continue
        install_word_wrap_header(table, wrap_first_section=wrap_first_section)
```

</details>

## 🔧 Function `wrapped_header_text_size`

```python
def wrapped_header_text_size(text: str, width: int, font_metrics: QFontMetrics, *, padding: int = _TEXT_PADDING) -> QSize
```

Return the size of `text` wrapped into `width` pixels.

<details>
<summary>Code:</summary>

```python
def wrapped_header_text_size(
    text: str,
    width: int,
    font_metrics: QFontMetrics,
    *,
    padding: int = _TEXT_PADDING,
) -> QSize:
    inner_width = max(width - padding, 1)
    bounds = font_metrics.boundingRect(0, 0, inner_width, 10_000, int(HEADER_TEXT_FLAGS), text)
    return QSize(max(width, bounds.width() + padding), bounds.height() + padding)
```

</details>
