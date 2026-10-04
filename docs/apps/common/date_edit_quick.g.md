---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `date_edit_quick.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `attach_date_edit_quick_controls`](#-function-attach_date_edit_quick_controls)
- [🔧 Function `match_control_heights`](#-function-match_control_heights)
- [🔧 Function `match_layout_control_heights`](#-function-match_layout_control_heights)
- [🔧 Function `match_layout_control_heights_many`](#-function-match_layout_control_heights_many)

</details>

## 🔧 Function `attach_date_edit_quick_controls`

```python
def attach_date_edit_quick_controls(date_edit: QDateEdit) -> None
```

Apply calendar popup, leading calendar icon, and toolbar field height.

Quick presets (Yesterday, Today, ±1 day) live in the calendar footer, not
next to the field. The date field itself gets a Lucide calendar glyph on
the left and a height close to the former quick-button row.

Args:

- `date_edit` (`QDateEdit`): Existing date field from the UI.

<details>
<summary>Code:</summary>

```python
def attach_date_edit_quick_controls(date_edit: QDateEdit) -> None:
    apply_date_calendar_popup(date_edit)
    _apply_date_edit_field_chrome(date_edit)
```

</details>

## 🔧 Function `match_control_heights`

```python
def match_control_heights(*widgets: QWidget | None) -> int
```

Make every widget share the tallest size-hint height in the group.

Labels are vertically centered so text sits on the same baseline row as
buttons and date fields.

Args:

- `widgets` (`QWidget | None`): Controls in one toolbar/filter row.

Returns:

- `int`: Applied height, or `0` when no widgets were given.

<details>
<summary>Code:</summary>

```python
def match_control_heights(*widgets: QWidget | None) -> int:
    visible = [widget for widget in widgets if widget is not None]
    if not visible:
        return 0
    height = max(
        _MIN_CONTROL_HEIGHT,
        *(max(widget.sizeHint().height(), widget.minimumHeight()) for widget in visible),
    )
    for widget in visible:
        widget.setMinimumHeight(height)
        widget.setMaximumHeight(height)
        if isinstance(widget, QLabel):
            widget.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    return height
```

</details>

## 🔧 Function `match_layout_control_heights`

```python
def match_layout_control_heights(layout: QLayout | None) -> int
```

Match heights of every widget inside a horizontal toolbar layout.

<details>
<summary>Code:</summary>

```python
def match_layout_control_heights(layout: QLayout | None) -> int:
    if layout is None:
        return 0
    widgets: list[QWidget] = []
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if item is None:
            continue
        widget = item.widget()
        if isinstance(widget, QWidget):
            widgets.append(widget)
    return match_control_heights(*widgets)
```

</details>

## 🔧 Function `match_layout_control_heights_many`

```python
def match_layout_control_heights_many(layouts: Iterable[QLayout | None]) -> None
```

Apply [`match_layout_control_heights`](#-function-match_layout_control_heights) to each layout.

<details>
<summary>Code:</summary>

```python
def match_layout_control_heights_many(layouts: Iterable[QLayout | None]) -> None:
    for layout in layouts:
        match_layout_control_heights(layout)
```

</details>
