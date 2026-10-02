---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ui_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `action_card_selection_qss`](#-function-action_card_selection_qss)
- [🔧 Function `apply_readable_selection_palette`](#-function-apply_readable_selection_palette)
- [🔧 Function `apply_soft_item_selection`](#-function-apply_soft_item_selection)
- [🔧 Function `apply_soft_list_selection_chrome`](#-function-apply_soft_list_selection_chrome)
- [🔧 Function `list_view_item_selection_qss`](#-function-list_view_item_selection_qss)
- [🔧 Function `list_view_panel_qss`](#-function-list_view_panel_qss)
- [🔧 Function `snippet_list_selection_qss`](#-function-snippet_list_selection_qss)

</details>

## 🔧 Function `action_card_selection_qss`

```python
def action_card_selection_qss() -> str
```

Return selection / hover QSS for Quick launcher action cards.

<details>
<summary>Code:</summary>

```python
def action_card_selection_qss() -> str:
    return f"""
QListWidget {{
    outline: none;
    background: transparent;
    border: none;
}}
QListWidget::item {{
    margin: 4px;
    padding: 0px;
    border-radius: 8px;
    border: 1px solid transparent;
    background: transparent;
    color: {SELECTION_TEXT};
}}
QListWidget::item:hover:!selected {{
    background: {SELECTION_HOVER};
    border-color: {CHIP_BORDER};
}}
QListWidget::item:selected {{
    background: {SELECTION_BG};
    border: 1px solid {SELECTION_BORDER};
    color: {SELECTION_TEXT};
}}
""".strip()
```

</details>

## 🔧 Function `apply_readable_selection_palette`

```python
def apply_readable_selection_palette(view: QAbstractItemView) -> None
```

Keep selected-item text dark on soft blue highlights (not system white).

<details>
<summary>Code:</summary>

```python
def apply_readable_selection_palette(view: QAbstractItemView) -> None:
    palette = view.palette()
    text = QColor(SELECTION_TEXT)
    highlight = QColor(SELECTION_BG)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        palette.setColor(group, QPalette.ColorRole.Highlight, highlight)
        palette.setColor(group, QPalette.ColorRole.HighlightedText, text)
    view.setPalette(palette)
```

</details>

## 🔧 Function `apply_soft_item_selection`

```python
def apply_soft_item_selection(view: QAbstractItemView) -> None
```

Append soft blue selected / hover rules to a list view or list widget.

<details>
<summary>Code:</summary>

```python
def apply_soft_item_selection(view: QAbstractItemView) -> None:
    existing = (view.styleSheet() or "").rstrip()
    fragment = _LIST_WIDGET_ITEM_SELECTION_QSS if isinstance(view, QListWidget) else _LIST_ITEM_SELECTION_QSS
    view.setStyleSheet(f"{existing}\n{fragment}" if existing else fragment)
    apply_readable_selection_palette(view)
```

</details>

## 🔧 Function `apply_soft_list_selection_chrome`

```python
def apply_soft_list_selection_chrome(root: QWidget) -> None
```

Apply soft selection chrome to every `QListView` under [`root`](../habits/habit_comments.g.md#%EF%B8%8F-method-root).

<details>
<summary>Code:</summary>

```python
def apply_soft_list_selection_chrome(root: QWidget) -> None:
    for view in root.findChildren(QListView):
        apply_soft_item_selection(view)
```

</details>

## 🔧 Function `list_view_item_selection_qss`

```python
def list_view_item_selection_qss(*, with_row_separators: bool = False) -> str
```

Return QSS for `QListView::item` selected / hover states.

Args:

- `with_row_separators` (`bool`): When `True`, keep a light bottom border
  between rows (finance / food / fitness filter lists).

Returns:

- `str`: Stylesheet fragment for list items (does not set the outer list border).

<details>
<summary>Code:</summary>

```python
def list_view_item_selection_qss(*, with_row_separators: bool = False) -> str:
    separator = "border-bottom: 1px solid #e0e0e0;" if with_row_separators else ""
    return f"""
QListView::item {{
    padding: 4px 6px;
    border-radius: 6px;
    {separator}
}}
QListView::item:selected {{
    background-color: {SELECTION_BG};
    color: {SELECTION_TEXT};
    border: 1px solid {SELECTION_BORDER};
}}
QListView::item:hover:!selected {{
    background-color: {SELECTION_HOVER};
}}
""".strip()
```

</details>

## 🔧 Function `list_view_panel_qss`

```python
def list_view_panel_qss(*, border_color: str, with_row_separators: bool = True) -> str
```

Return a full `QListView` stylesheet with branded border and soft selection.

Args:

- `border_color` (`str`): Outer list border color (app accent).
- `with_row_separators` (`bool`): Whether items draw a bottom hairline.

Returns:

- `str`: Complete stylesheet string for a filter / option list.

<details>
<summary>Code:</summary>

```python
def list_view_panel_qss(*, border_color: str, with_row_separators: bool = True) -> str:
    return f"""
QListView {{
    border: 2px solid {border_color};
    border-radius: 4px;
    background-color: white;
    outline: none;
}}
{list_view_item_selection_qss(with_row_separators=with_row_separators)}
""".strip()
```

</details>

## 🔧 Function `snippet_list_selection_qss`

```python
def snippet_list_selection_qss() -> str
```

Return selection QSS for Quick paste snippet list.

<details>
<summary>Code:</summary>

```python
def snippet_list_selection_qss() -> str:
    return f"""
QListWidget {{
    outline: none;
    show-decoration-selected: 0;
}}
QListWidget::item {{
    border: none;
    border-radius: 6px;
    color: palette(text);
}}
QListWidget::item:hover,
QListWidget::item:selected,
QListWidget::item:selected:active,
QListWidget::item:selected:!active,
QListWidget::item:selected:hover {{
    background-color: {SELECTION_BG};
    color: {SELECTION_TEXT};
    border: 1px solid {SELECTION_BORDER};
    border-radius: 6px;
}}
""".strip()
```

</details>
