---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dialog_geometry.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_adaptive_dialog_size`](#-function-apply_adaptive_dialog_size)
- [🔧 Function `available_max_height`](#-function-available_max_height)
- [🔧 Function `fit_widget_height`](#-function-fit_widget_height)
- [🔧 Function `icon_grid_content_height`](#-function-icon_grid_content_height)
- [🔧 Function `list_content_height`](#-function-list_content_height)
- [🔧 Function `text_content_height`](#-function-text_content_height)
- [🔧 Function `widget_content_height`](#-function-widget_content_height)

</details>

## 🔧 Function `apply_adaptive_dialog_size`

```python
def apply_adaptive_dialog_size(dialog: QDialog, layout: QVBoxLayout) -> QSize
```

Size dialog to content: fixed width from `target`, adaptive height.

Height is clamped to `[MIN_DIALOG_HEIGHT, min(target.height(), screen)]`.
Returns the applied size.

<details>
<summary>Code:</summary>

```python
def apply_adaptive_dialog_size(
    dialog: QDialog,
    layout: QVBoxLayout,
    *,
    target: QSize,
    stretch_row: int | None = 1,
) -> QSize:
    if stretch_row is not None:
        layout.setStretch(stretch_row, 1)

    max_height = min(target.height(), available_max_height(dialog))
    min_height = min(MIN_DIALOG_HEIGHT, max_height)

    dialog.setMinimumWidth(target.width())
    dialog.setMinimumHeight(min_height)

    # Force layout to compute size hints with the target width.
    dialog.resize(target.width(), max_height)
    dialog.adjustSize()

    hint_height = dialog.sizeHint().height()
    if stretch_row is not None:
        item = layout.itemAt(stretch_row)
        stretch_widget = item.widget() if item is not None else None
        if stretch_widget is not None and stretch_widget.property("_hsk_content_clamped"):
            hint_height = max_height

    height = max(min_height, min(hint_height, max_height))
    size = QSize(target.width(), height)
    dialog.resize(size)
    return size
```

</details>

## 🔧 Function `available_max_height`

```python
def available_max_height(widget: QWidget | None = None) -> int
```

Return max usable dialog height (90% of available screen height).

<details>
<summary>Code:</summary>

```python
def available_max_height(widget: QWidget | None = None) -> int:
    screen = None
    if widget is not None:
        screen = widget.screen()
    if screen is None:
        app = QApplication.instance()
        if isinstance(app, QApplication):
            screen = app.primaryScreen()
    if screen is None:
        return 768
    return max(MIN_DIALOG_HEIGHT, int(screen.availableGeometry().height() * _SCREEN_HEIGHT_RATIO))
```

</details>

## 🔧 Function `fit_widget_height`

```python
def fit_widget_height(widget: QWidget, content_height: int) -> int
```

Set widget minimum height from content, clamped to `[minimum, maximum]`.

Returns the applied height. Stores `_hsk_content_clamped` when natural
content exceeds `maximum` so dialogs can expand to the full target height.

<details>
<summary>Code:</summary>

```python
def fit_widget_height(
    widget: QWidget,
    content_height: int,
    *,
    minimum: int = MIN_CONTENT_HEIGHT,
    maximum: int,
) -> int:
    height = max(minimum, min(content_height, maximum))
    widget.setMinimumHeight(height)
    widget.setProperty("_hsk_content_clamped", content_height > maximum)
    return height
```

</details>

## 🔧 Function `icon_grid_content_height`

```python
def icon_grid_content_height(list_widget: QListWidget) -> int
```

Return pixel height needed for all icon cards in the grid.

<details>
<summary>Code:</summary>

```python
def icon_grid_content_height(list_widget: QListWidget, *, width: int = _DEFAULT_CONTENT_WIDTH) -> int:
    if list_widget.width() < _MIN_LAID_OUT_WIDTH:
        list_widget.resize(width, max(list_widget.height(), MIN_CONTENT_HEIGHT))
    height = measure_icon_grid_height(list_widget)
    return height if height > 0 else MIN_CONTENT_HEIGHT
```

</details>

## 🔧 Function `list_content_height`

```python
def list_content_height(list_widget: QListWidget) -> int
```

Return pixel height needed to show all list rows without scrolling.

<details>
<summary>Code:</summary>

```python
def list_content_height(list_widget: QListWidget) -> int:
    count = list_widget.count()
    if count == 0:
        return MIN_CONTENT_HEIGHT

    rows_height = sum(list_widget.sizeHintForRow(index) for index in range(count))
    spacing = list_widget.spacing() * max(0, count - 1)
    frame = list_widget.frameWidth() * 2
    return rows_height + spacing + frame
```

</details>

## 🔧 Function `text_content_height`

```python
def text_content_height(edit: QPlainTextEdit | QTextEdit | QTextBrowser) -> int
```

Return pixel height needed to show text document content.

<details>
<summary>Code:</summary>

```python
def text_content_height(
    edit: QPlainTextEdit | QTextEdit | QTextBrowser,
    *,
    width: int = _DEFAULT_CONTENT_WIDTH,
) -> int:
    margins = edit.contentsMargins()
    frame = edit.frameWidth() * 2
    text_width = max(_MIN_TEXT_WIDTH, width - margins.left() - margins.right() - frame)
    document = edit.document()
    document.setTextWidth(text_width)
    document_height = int(document.size().height())
    return document_height + margins.top() + margins.bottom() + frame
```

</details>

## 🔧 Function `widget_content_height`

```python
def widget_content_height(widget: QWidget) -> int
```

Return natural height hint for a container widget.

<details>
<summary>Code:</summary>

```python
def widget_content_height(widget: QWidget) -> int:
    return max(MIN_CONTENT_HEIGHT, widget.sizeHint().height())
```

</details>
