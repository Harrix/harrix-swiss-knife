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

Opt `window` into Fluent theme, Mica, and standardized control chrome.

<details>
<summary>Code:</summary>

```python
def install_fluent_app_window(window: QWidget) -> None:
    enable_fluent_theme(window)
    try_apply_system_backdrop(window, backdrop=SystemBackdrop.MICA)
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

Re-apply Fluent surfaces, controls, lists, tables, and buttons.

<details>
<summary>Code:</summary>

```python
def refresh_fluent_app_window(window: QWidget) -> None:
    palette = palette_for(window)
    _apply_fluent_surfaces(window, palette)
    _normalize_control_metrics(window)
    _restyle_inputs(window, palette)
    _restyle_tables(window, palette)
    _restyle_tabs(window, palette)
    _apply_fluent_list_selection(window, palette)
    _restyle_buttons(window, palette)
    apply_flat_scrollbars(window)
    window.update()
```

</details>
