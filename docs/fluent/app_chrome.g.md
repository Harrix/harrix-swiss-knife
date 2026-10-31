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
- [🔧 Function `install_fluent_dialog_chrome`](#-function-install_fluent_dialog_chrome)
- [🔧 Function `prepare_fluent_app_window`](#-function-prepare_fluent_app_window)
- [🔧 Function `refresh_fluent_app_window`](#-function-refresh_fluent_app_window)

</details>

## 🔧 Function `install_fluent_app_window`

```python
def install_fluent_app_window(window: QWidget) -> None
```

Opt `window` into Fluent theme and standardized control chrome.

Restyles the window once now and again only when the resolved theme changes.
Call it after the layout is complete; [`prepare_fluent_app_window`](#-function-prepare_fluent_app_window) alone is
enough for code that only needs [`is_fluent_themed`](theme.g.md#-function-is_fluent_themed) (for example the caption).

<details>
<summary>Code:</summary>

```python
def install_fluent_app_window(window: QWidget) -> None:
    if window.property(_PROP_BOUND):
        refresh_fluent_app_window(window)
        return
    # Mark first: the polish replay below re-enters through `install_fluent_dialog_chrome`.
    window.setProperty(_PROP_BOUND, True)  # noqa: FBT003
    prepare_fluent_app_window(window)
    if window.testAttribute(Qt.WidgetAttribute.WA_WState_Created):
        try_apply_system_backdrop(window, backdrop=SystemBackdrop.MICA)
    bind_theme(window, lambda: refresh_fluent_app_window(window))
```

</details>

## 🔧 Function `install_fluent_dialog_chrome`

```python
def install_fluent_dialog_chrome(dialog: QWidget) -> bool
```

Give `dialog` the same chrome as the app window that owns it.

Only dialogs owned by a window that ran [`install_fluent_app_window`](#-function-install_fluent_app_window) are
restyled, so Fluent widget-library dialogs keep their own controls.

Returns:

- `bool`: `True` when the chrome was installed now.

<details>
<summary>Code:</summary>

```python
def install_fluent_dialog_chrome(dialog: QWidget) -> bool:
    if dialog.property(_PROP_BOUND):
        return False
    owner = dialog.parentWidget()
    if owner is None or not owner.window().property(_PROP_BOUND):
        return False
    install_fluent_app_window(dialog)
    return True
```

</details>

## 🔧 Function `prepare_fluent_app_window`

```python
def prepare_fluent_app_window(window: QWidget) -> None
```

Mark `window` as Fluent-themed and swap in the Fluent window stylesheet.

Children are restyled later by [`install_fluent_app_window`](#-function-install_fluent_app_window). Replacing the
legacy form stylesheet before anything is polished keeps the first (and most
expensive) polish of the whole tree on the final rules.

<details>
<summary>Code:</summary>

```python
def prepare_fluent_app_window(window: QWidget) -> None:
    from harrix_swiss_knife.qt_ui_effects import suspended_polish_filters  # noqa: PLC0415

    enable_fluent_theme(window)
    palette = palette_for(window)
    with suspended_polish_filters(window):
        _set_sheet(window, _fluent_surface_qss(palette))
        window.setPalette(to_qpalette(palette, window.palette()))
    window.setAutoFillBackground(False)
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
    from harrix_swiss_knife.qt_ui_effects import suspended_polish_filters  # noqa: PLC0415

    palette = palette_for(window)
    with suspended_polish_filters(window):
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
