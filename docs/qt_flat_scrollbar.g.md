---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_flat_scrollbar.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_flat_scrollbars`](#-function-apply_flat_scrollbars)
- [🔧 Function `apply_flat_scrollbars_to_styled_item_views`](#-function-apply_flat_scrollbars_to_styled_item_views)
- [🔧 Function `with_flat_scrollbars`](#-function-with_flat_scrollbars)

</details>

## 🔧 Function `apply_flat_scrollbars`

```python
def apply_flat_scrollbars(root: QWidget) -> None
```

Append flat scrollbar rules to every scroll area under [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root).

Covers item views, `QScrollArea`, and text edits — including widgets with
no stylesheet yet, so parent window stylesheets cannot leave classic bars.

<details>
<summary>Code:</summary>

```python
def apply_flat_scrollbars(root: QWidget) -> None:
    for widget in root.findChildren(QAbstractScrollArea):
        sheet = widget.styleSheet().strip()
        updated = with_flat_scrollbars(sheet)
        if updated != sheet:
            widget.setStyleSheet(updated)
```

</details>

## 🔧 Function `apply_flat_scrollbars_to_styled_item_views`

```python
def apply_flat_scrollbars_to_styled_item_views(root: QWidget) -> None
```

Apply flat scrollbars under [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) (alias kept for older call sites).

<details>
<summary>Code:</summary>

```python
def apply_flat_scrollbars_to_styled_item_views(root: QWidget) -> None:
    apply_flat_scrollbars(root)
```

</details>

## 🔧 Function `with_flat_scrollbars`

```python
def with_flat_scrollbars(style: str) -> str
```

Return `style` with flat scrollbar rules appended (once).

<details>
<summary>Code:</summary>

```python
def with_flat_scrollbars(style: str) -> str:
    sheet = style.strip()
    if "QScrollBar:vertical" in sheet:
        return sheet
    if not sheet:
        return FLAT_SCROLLBAR_STYLE
    return f"{sheet}\n{FLAT_SCROLLBAR_STYLE}"
```

</details>
