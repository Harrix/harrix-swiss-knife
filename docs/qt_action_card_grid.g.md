---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_action_card_grid.py`

## 🔧 Function `configure_action_card_grid`

```python
def configure_action_card_grid(list_widget: QListWidget) -> None
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
