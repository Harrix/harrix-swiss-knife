---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_action_card_grid.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `CARD_ICON_SIZE`](#-constant-card_icon_size)
- [📎 Constant `CARD_SPACING`](#-constant-card_spacing)
- [📎 Constant `CARD_GRID_CELL_WIDTH`](#-constant-card_grid_cell_width)
- [📎 Constant `CARD_TEXT_AREA_HEIGHT`](#-constant-card_text_area_height)
- [📎 Constant `CARD_GRID_CELL_HEIGHT`](#-constant-card_grid_cell_height)
- [🔧 Function `configure_action_card_grid`](#-function-configure_action_card_grid)

</details>

## 📎 Constant `CARD_ICON_SIZE`

```python
CARD_ICON_SIZE = 64
```

_No docstring provided._

## 📎 Constant `CARD_SPACING`

```python
CARD_SPACING = 8
```

_No docstring provided._

## 📎 Constant `CARD_GRID_CELL_WIDTH`

```python
CARD_GRID_CELL_WIDTH = 140
```

_No docstring provided._

## 📎 Constant `CARD_TEXT_AREA_HEIGHT`

```python
CARD_TEXT_AREA_HEIGHT = 36
```

_No docstring provided._

## 📎 Constant `CARD_GRID_CELL_HEIGHT`

```python
CARD_GRID_CELL_HEIGHT = CARD_ICON_SIZE + CARD_TEXT_AREA_HEIGHT
```

_No docstring provided._

## 🔧 Function `configure_action_card_grid`

```python
def configure_action_card_grid(list_widget: QListWidget, *, min_height: int | None = None) -> None
```

Apply the same icon-card layout used by New Markdown command picker.

<details>
<summary>Code:</summary>

```python
def configure_action_card_grid(list_widget: QListWidget, *, min_height: int | None = None) -> None:
    list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    if min_height is not None:
        list_widget.setMinimumHeight(min_height)
    list_widget.setViewMode(QListWidget.ViewMode.IconMode)
    list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
    list_widget.setMovement(QListWidget.Movement.Static)
    list_widget.setSpacing(CARD_SPACING)
    list_widget.setIconSize(QSize(CARD_ICON_SIZE, CARD_ICON_SIZE))
    list_widget.setGridSize(QSize(CARD_GRID_CELL_WIDTH, CARD_GRID_CELL_HEIGHT))
    list_widget.setWordWrap(True)
    list_widget.setUniformItemSizes(False)
    list_widget.setStyleSheet(
        "QListWidget::item { padding-top: 0px; padding-bottom: 0px; margin: 0px; }",
    )
    list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    list_widget.setFrameShape(QListWidget.Shape.NoFrame)
```

</details>
