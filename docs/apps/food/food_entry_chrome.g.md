---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_entry_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_food_log_column_visibility`](#-function-apply_food_log_column_visibility)
- [🔧 Function `apply_food_log_table_column_widths`](#-function-apply_food_log_table_column_widths)
- [🔧 Function `food_item_state_text`](#-function-food_item_state_text)
- [🔧 Function `install_food_entry_chrome`](#-function-install_food_entry_chrome)
- [🔧 Function `persist_food_splitter_sizes`](#-function-persist_food_splitter_sizes)
- [🔧 Function `refresh_food_item_state_label`](#-function-refresh_food_item_state_label)
- [🔧 Function `set_food_log_empty_visible`](#-function-set_food_log_empty_visible)

</details>

## 🔧 Function `apply_food_log_column_visibility`

```python
def apply_food_log_column_visibility(host: Any) -> None
```

Re-apply persisted column visibility after the food log model is ready.

<details>
<summary>Code:</summary>

```python
def apply_food_log_column_visibility(host: Any) -> None:
    table = host.tableView_food_log
    flags = load_column_visibility()
    for key, column, _label in TOGGLEABLE_COLUMNS:
        visible = flags.get(key, True)
        if column < 0:
            _set_record_id_visible(table, visible=visible, persist=False)
        else:
            _set_data_column_visible(table, column, visible=visible, persist=False, refill=False)
    _apply_day_header_column_policy(table)
    from harrix_swiss_knife.apps.food.food_day_headers import (  # noqa: PLC0415
        FoodDayHeaderProxy,
        apply_food_day_header_spans,
    )

    if isinstance(table.model(), FoodDayHeaderProxy):
        apply_food_day_header_spans(table)
    else:
        table.clearSpans()
    apply_food_log_table_column_widths(table, force=True)
```

</details>

## 🔧 Function `apply_food_log_table_column_widths`

```python
def apply_food_log_table_column_widths(table_view: QTableView, *, force: bool = False) -> None
```

Fill the viewport among visible food-log columns, then keep them Interactive.

<details>
<summary>Code:</summary>

```python
def apply_food_log_table_column_widths(table_view: QTableView, *, force: bool = False) -> None:
    bind_column_fill_on_resize(table_view, apply_food_log_table_column_widths)
    if not table_view.isVisible() or user_resized_columns(table_view):
        return
    header = table_view.horizontalHeader()
    count = header.count()
    if count <= 0 or table_view.property("hskColumnFillGuard"):
        return
    viewport_w = table_view.viewport().width()
    if viewport_w <= 0:
        return
    if not force and columns_fill_viewport(table_view):
        return

    visible = [i for i in range(count) if not table_view.isColumnHidden(i)]
    if not visible:
        return

    header.setStretchLastSection(False)
    header.setMinimumSectionSize(min(header.minimumSectionSize(), 24))
    min_size = header.minimumSectionSize()
    widths = _visible_food_log_column_widths(
        viewport_w,
        count,
        visible=visible,
        min_size=min_size,
    )

    table_view.setProperty("hskColumnFillGuard", 1)
    try:
        for column in range(count):
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            table_view.setColumnWidth(column, widths[column] if column in set(visible) else 0)
    finally:
        table_view.setProperty("hskColumnFillGuard", 0)
```

</details>

## 🔧 Function `food_item_state_text`

```python
def food_item_state_text(display_name: str | None) -> str
```

Return the form item indicator text (with optional hint when empty).

<details>
<summary>Code:</summary>

```python
def food_item_state_text(display_name: str | None) -> str:
    name = (display_name or "").strip()
    if not name:
        return f"{_NO_ITEM}\n{_ITEM_HINT}"
    lowered = name.casefold()
    if lowered.startswith(_ITEM_PREFIX.casefold()):
        return name
    if lowered in {_NO_ITEM.casefold(), "no item selected"}:
        return f"{_NO_ITEM}\n{_ITEM_HINT}"
    return f"{_ITEM_PREFIX}{name}"
```

</details>

## 🔧 Function `install_food_entry_chrome`

```python
def install_food_entry_chrome(host: Any) -> None
```

Polish the Food form, items list, splitter, and log table chrome.

<details>
<summary>Code:</summary>

```python
def install_food_entry_chrome(host: Any) -> None:
    _ensure_item_state_label(host)
    _ensure_catalog_search(host)
    _ensure_food_log_empty_label(host)
    _polish_form_column(host)
    _polish_items_list(host)
    _polish_item_state_label(host)
    _polish_food_log_table(host)
    _configure_food_splitter(host)
    if not getattr(host, "_food_entry_theme_bound", False):

        def _refresh_theme() -> None:
            _polish_form_column(host)
            _polish_items_list(host)
            _polish_item_state_label(host)

        bind_theme(host, _refresh_theme)
        host._food_entry_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_food_splitter_sizes`

```python
def persist_food_splitter_sizes(host: Any) -> None
```

Save current Food-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def persist_food_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter_food"):
        return
    sizes = host.splitter_food.sizes()
    if len(sizes) == EXPECTED_FOOD_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_food_splitter_sizes([int(size) for size in sizes])
```

</details>

## 🔧 Function `refresh_food_item_state_label`

```python
def refresh_food_item_state_label(host: Any, display_name: str | None = None) -> None
```

Update the form item indicator with a Fluent status string.

<details>
<summary>Code:</summary>

```python
def refresh_food_item_state_label(host: Any, display_name: str | None = None) -> None:
    label = getattr(host, "label_food_item_now", None)
    if not isinstance(label, QLabel):
        return
    text = food_item_state_text(display_name)
    selected = bool((display_name or "").strip()) and not text.startswith(_NO_ITEM)
    label.setText(text)
    label.setWordWrap(True)
    label.setToolTip(_ITEM_HINT if not selected else text.split("\n", 1)[0])
    label.setProperty("hskFoodItemSelected", selected)
    label.style().unpolish(label)
    label.style().polish(label)
```

</details>

## 🔧 Function `set_food_log_empty_visible`

```python
def set_food_log_empty_visible(host: Any, *, visible: bool) -> None
```

Show or hide the food-log empty state.

<details>
<summary>Code:</summary>

```python
def set_food_log_empty_visible(host: Any, *, visible: bool) -> None:
    label = getattr(host, "label_food_log_empty", None)
    if isinstance(label, QLabel):
        label.setVisible(visible)
    table = getattr(host, "tableView_food_log", None)
    if table is not None:
        table.setVisible(not visible)
```

</details>
