---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_command_section.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_opaque_white`](#-function-apply_opaque_white)
- [🔧 Function `count_icon_grid_first_row`](#-function-count_icon_grid_first_row)
- [🔧 Function `create_command_section`](#-function-create_command_section)
- [🔧 Function `fit_icon_grid_height`](#-function-fit_icon_grid_height)
- [🔧 Function `grow_qfont`](#-function-grow_qfont)
- [🔧 Function `measure_icon_grid_height`](#-function-measure_icon_grid_height)
- [🔧 Function `prepare_icon_grid`](#-function-prepare_icon_grid)
- [🔧 Function `style_transparent_icon_grid`](#-function-style_transparent_icon_grid)

</details>

## 🔧 Function `apply_opaque_white`

```python
def apply_opaque_white(widget: QWidget) -> None
```

Paint an opaque white background without stylesheets (keeps native scrollbars).

<details>
<summary>Code:</summary>

```python
def apply_opaque_white(widget: QWidget) -> None:
    palette = widget.palette()
    white = QColor("#ffffff")
    palette.setColor(QPalette.ColorRole.Window, white)
    palette.setColor(QPalette.ColorRole.Base, white)
    widget.setAutoFillBackground(True)
    widget.setPalette(palette)
```

</details>

## 🔧 Function `count_icon_grid_first_row`

```python
def count_icon_grid_first_row(grid: QListWidget) -> int
```

Return how many icon cards Qt placed on the first row.

<details>
<summary>Code:</summary>

```python
def count_icon_grid_first_row(grid: QListWidget) -> int:
    if grid.count() == 0:
        return 0
    grid.doItemsLayout()
    first = grid.item(0)
    if first is None:
        return 0
    first_top = grid.visualItemRect(first).top()
    count = 0
    for index in range(grid.count()):
        item = grid.item(index)
        if item is None:
            continue
        if grid.visualItemRect(item).top() > first_top + 4:
            break
        count += 1
    return count
```

</details>

## 🔧 Function `create_command_section`

```python
def create_command_section(*, title: str | None = None) -> tuple[QFrame, QLabel | None, QVBoxLayout]
```

Create a bordered white section card for an icon command grid.

Returns:

- `(frame, label, layout)`: Add the grid with `layout.addWidget(grid)`.
  `label` is `None` when `title` is omitted.

<details>
<summary>Code:</summary>

```python
def create_command_section(*, title: str | None = None) -> tuple[QFrame, QLabel | None, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName(COMMAND_SECTION_OBJECT_NAME)
    frame.setFrameShape(QFrame.Shape.NoFrame)
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    frame.setStyleSheet(COMMAND_SECTION_STYLE)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(8, 4, 8, 8)
    layout.setSpacing(4)

    label: QLabel | None = None
    if title is not None:
        label = QLabel(title)
        font = QFont(label.font())
        font.setBold(True)
        grow_qfont(font)
        label.setFont(font)
        layout.addWidget(label)

    return frame, label, layout
```

</details>

## 🔧 Function `fit_icon_grid_height`

```python
def fit_icon_grid_height(grid: QListWidget) -> None
```

Set grid height from laid-out icon rows; clear leftover internal scroll range.

<details>
<summary>Code:</summary>

```python
def fit_icon_grid_height(grid: QListWidget) -> None:
    if not grid.isVisible():
        return
    if grid.count() == 0:
        grid.setFixedHeight(0)
        return

    height = measure_icon_grid_height(grid)
    grid.setFixedHeight(height)
    grid.verticalScrollBar().setRange(0, 0)
    grid.horizontalScrollBar().setRange(0, 0)
```

</details>

## 🔧 Function `grow_qfont`

```python
def grow_qfont(font: QFont, *, delta: int = 1, fallback_point_size: int = 10) -> QFont
```

Increase font size without calling `setPointSize` on a pixel-sized font.

Windows system fonts often have `pointSize() == -1` and a pixel size instead.
Passing that value to `QFont.setPointSize` logs
`Point size <= 0 (-1)`.

Args:

- `font` (`QFont`): Font to grow in place.
- `delta` (`int`): Size increment. Defaults to `1`.
- `fallback_point_size` (`int`): Point size used when the font has neither
  a point size nor a pixel size. Defaults to `10`.

Returns:

- `QFont`: The same `font` instance after the size change.

<details>
<summary>Code:</summary>

```python
def grow_qfont(font: QFont, *, delta: int = 1, fallback_point_size: int = 10) -> QFont:
    point_size = font.pointSize()
    if point_size > 0:
        font.setPointSize(point_size + delta)
        return font
    pixel_size = font.pixelSize()
    if pixel_size > 0:
        font.setPixelSize(pixel_size + delta)
        return font
    font.setPointSize(max(1, fallback_point_size + delta))
    return font
```

</details>

## 🔧 Function `measure_icon_grid_height`

```python
def measure_icon_grid_height(grid: QListWidget) -> int
```

Return pixel height needed for all icon cards in the grid.

<details>
<summary>Code:</summary>

```python
def measure_icon_grid_height(grid: QListWidget) -> int:
    if grid.count() == 0:
        return 0

    grid.doItemsLayout()
    item_bottoms = [
        grid.visualItemRect(grid.item(index)).bottom() for index in range(grid.count()) if grid.item(index) is not None
    ]
    return max(item_bottoms, default=CARD_GRID_CELL_HEIGHT - 1) + 1 + 4
```

</details>

## 🔧 Function `prepare_icon_grid`

```python
def prepare_icon_grid(grid: QListWidget, *, event_filter: QObject | None = None) -> None
```

Make an icon grid frameless and non-scrolling (outer scroll owns the wheel).

<details>
<summary>Code:</summary>

```python
def prepare_icon_grid(grid: QListWidget, *, event_filter: QObject | None = None) -> None:
    style_transparent_icon_grid(grid)
    grid.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    grid.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    grid.verticalScrollBar().setEnabled(False)
    grid.horizontalScrollBar().setEnabled(False)
    if event_filter is not None:
        grid.installEventFilter(event_filter)
        grid.viewport().installEventFilter(event_filter)
```

</details>

## 🔧 Function `style_transparent_icon_grid`

```python
def style_transparent_icon_grid(grid: QListWidget) -> None
```

Keep icon grids frameless so section cards own the border.

<details>
<summary>Code:</summary>

```python
def style_transparent_icon_grid(grid: QListWidget) -> None:
    grid.setAutoFillBackground(False)
    grid.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=False)
    grid.setStyleSheet(
        "QListWidget {"
        " background: transparent;"
        " border: none;"
        "}"
        "QListWidget::item {"
        " padding-top: 0px;"
        " padding-bottom: 0px;"
        " margin: 0px;"
        "}",
    )
```

</details>
