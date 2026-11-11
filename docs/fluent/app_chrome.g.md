---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_date_edit_text_fits`](#-function-ensure_date_edit_text_fits)
- [🔧 Function `install_fluent_app_window`](#-function-install_fluent_app_window)
- [🔧 Function `install_fluent_dialog_chrome`](#-function-install_fluent_dialog_chrome)
- [🔧 Function `prepare_fluent_app_window`](#-function-prepare_fluent_app_window)
- [🔧 Function `refresh_fluent_app_window`](#-function-refresh_fluent_app_window)
- [🔧 Function `style_fluent_item_view`](#-function-style_fluent_item_view)
- [🔧 Function `style_fluent_table`](#-function-style_fluent_table)

</details>

## 🔧 Function `ensure_date_edit_text_fits`

```python
def ensure_date_edit_text_fits(box: QDateEdit) -> None
```

Keep yyyy-MM-dd clear of the calendar chevron on any DPI / font size.

Do not set line-edit text margins. `QDateEdit` already insets `qt_spinbox_lineedit`
for `::drop-down`; a right text margin clips the last digit and leaves a gap.
Call again after adding a leading calendar action.

<details>
<summary>Code:</summary>

```python
def ensure_date_edit_text_fits(box: QDateEdit) -> None:
    line = box.lineEdit()
    leading = 0
    if line is not None:
        # Match the polished control font; qt_spinbox_lineedit can lag behind.
        line.setFont(box.font())
        line.setTextMargins(0, 0, 0, 0)
        metrics = line.fontMetrics()
        if line.actions():
            leading = DATE_EDIT_LEADING_ICON_WIDTH
    else:
        metrics = box.fontMetrics()
    needed = metrics.horizontalAdvance("8888-88-88") + DATE_EDIT_DROP_WIDTH + DATE_EDIT_CHROME_WIDTH + leading
    floor = max(DATE_EDIT_MIN_WIDTH, needed)
    if box.minimumWidth() < floor:
        box.setMinimumWidth(floor)
```

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
        _restyle_splitters(window)
        apply_flat_scrollbars(window)
    window.update()
```

</details>

## 🔧 Function `style_fluent_item_view`

```python
def style_fluent_item_view(view: QAbstractItemView, palette: FluentPalette | None = None) -> None
```

Apply Fluent list selection chrome and a readable text palette.

Layout chrome must call this instead of clearing the view stylesheet: an
empty sheet re-polishes the widget onto the system palette (black ink).

<details>
<summary>Code:</summary>

```python
def style_fluent_item_view(view: QAbstractItemView, palette: FluentPalette | None = None) -> None:
    _style_item_view(view, palette if palette is not None else palette_for(view))
```

</details>

## 🔧 Function `style_fluent_table`

```python
def style_fluent_table(table: QTableView, palette: FluentPalette | None = None) -> None
```

Apply Fluent table chrome, day-band header palette, and row band refresh.

Call again after replacing the horizontal header (for example with
[`WordWrapHeaderView`](../apps/common/word_wrap_header.g.md#%EF%B8%8F-class-wordwrapheaderview)): a new header starts on the system light palette.

<details>
<summary>Code:</summary>

```python
def style_fluent_table(table: QTableView, palette: FluentPalette | None = None) -> None:
    chosen = palette if palette is not None else palette_for(table)
    _style_table(table, chosen)
    refresh_day_bands(table)
```

</details>
