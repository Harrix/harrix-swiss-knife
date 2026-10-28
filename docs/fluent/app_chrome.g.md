---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `install_fluent_app_window`](#-function-install_fluent_app_window)
- [🔧 Function `refresh_fluent_app_window`](#-function-refresh_fluent_app_window)

</details>

## 🔧 Function `install_fluent_app_window`

```python
def install_fluent_app_window(window: QWidget) -> None
```

Opt `window` into Fluent theme and restyle legacy Harrix chrome under it.

<details>
<summary>Code:</summary>

```python
def install_fluent_app_window(window: QWidget) -> None:
    enable_fluent_theme(window)
    if not window.property(_PROP_BOUND):
        bind_theme(window, lambda: refresh_fluent_app_window(window))
        window.setProperty(_PROP_BOUND, True)  # noqa: FBT003
    refresh_fluent_app_window(window)
```

</details>

## 🔧 Function `refresh_fluent_app_window`

```python
def refresh_fluent_app_window(window: QWidget) -> None
```

Re-apply Fluent surfaces, lists, menus, and CTA buttons for the current theme.

<details>
<summary>Code:</summary>

```python
def refresh_fluent_app_window(window: QWidget) -> None:
    palette = palette_for(window)
    _apply_fluent_surfaces(window, palette)
    _apply_fluent_list_selection(window, palette)
    _restyle_buttons(window, palette)
    apply_flat_scrollbars(window)
    window.update()
```

</details>
