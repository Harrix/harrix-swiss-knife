---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_toolbar_style.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `toolbar_button_style`](#-function-toolbar_button_style)
- [🔧 Function `toolbar_toggle_style`](#-function-toolbar_toggle_style)

</details>

## 🔧 Function `toolbar_button_style`

```python
def toolbar_button_style() -> str
```

Return toolbar button QSS; checked fill follows soft selection chrome.

<details>
<summary>Code:</summary>

```python
def toolbar_button_style() -> str:
    fill, hover, border, _text = selection_chrome_colors()
    secondary_bg, secondary_hover, secondary_pressed, secondary_border = _toolbar_secondary_colors()
    return f"""
QPushButton, QToolButton {{
    background-color: {secondary_bg};
    border: 1px solid {secondary_border};
    border-radius: {TOOLBAR_BORDER_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: {secondary_hover};
    border-color: {secondary_border};
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: {secondary_pressed};
    border-color: {secondary_border};
}}
QPushButton:checked, QToolButton:checked {{
    background-color: {fill};
    border: 1px solid {border};
}}
QPushButton:checked:hover, QToolButton:checked:hover {{
    background-color: {hover};
    border-color: {border};
}}
"""
```

</details>

## 🔧 Function `toolbar_toggle_style`

```python
def toolbar_toggle_style() -> str
```

Return pill toggle QSS with themed on/off fills.

<details>
<summary>Code:</summary>

```python
def toolbar_toggle_style() -> str:
    fill, hover, border, _text = selection_chrome_colors()
    secondary_bg, secondary_hover, secondary_pressed, secondary_border = _toolbar_secondary_colors()
    return f"""
QPushButton {{
    background-color: {secondary_bg};
    border: 1px solid {secondary_border};
    border-radius: {TOOLBAR_TOGGLE_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover {{
    background-color: {secondary_hover};
    border-color: {secondary_border};
}}
QPushButton:pressed {{
    background-color: {secondary_pressed};
    border-color: {secondary_border};
}}
QPushButton:checked {{
    background-color: {fill};
    border: 1px solid {border};
}}
QPushButton:checked:hover {{
    background-color: {hover};
    border-color: {border};
}}
"""
```

</details>
