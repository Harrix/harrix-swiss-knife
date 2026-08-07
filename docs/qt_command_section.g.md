---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_command_section.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `COMMAND_SECTION_OBJECT_NAME`](#-constant-command_section_object_name)
- [📎 Constant `COMMAND_SECTION_STYLE`](#-constant-command_section_style)
- [🔧 Function `apply_opaque_white`](#-function-apply_opaque_white)
- [🔧 Function `create_command_section`](#-function-create_command_section)
- [🔧 Function `fit_icon_grid_height`](#-function-fit_icon_grid_height)
- [🔧 Function `measure_icon_grid_height`](#-function-measure_icon_grid_height)
- [🔧 Function `prepare_icon_grid`](#-function-prepare_icon_grid)
- [🔧 Function `style_transparent_icon_grid`](#-function-style_transparent_icon_grid)

</details>

## 📎 Constant `COMMAND_SECTION_OBJECT_NAME`

```python
COMMAND_SECTION_OBJECT_NAME = 'commandSection'
```

_No docstring provided._

## 📎 Constant `COMMAND_SECTION_STYLE`

```python
COMMAND_SECTION_STYLE = f'#{COMMAND_SECTION_OBJECT_NAME} {{ background-color: #ffffff; border: 1px solid #c0c0c0; border-radius: 8px;}}#{COMMAND_SECTION_OBJECT_NAME} > QLabel {{ background: transparent; padding: 4px 8px 0px 8px;}}'
```

_No docstring provided._

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
        font.setPointSize(font.pointSize() + 1)
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
