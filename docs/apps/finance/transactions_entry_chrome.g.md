---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transactions_entry_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_transactions_column_visibility`](#-function-apply_transactions_column_visibility)
- [🔧 Function `apply_transactions_table_column_widths`](#-function-apply_transactions_table_column_widths)
- [🔧 Function `category_state_text`](#-function-category_state_text)
- [🔧 Function `install_transactions_entry_chrome`](#-function-install_transactions_entry_chrome)
- [🔧 Function `persist_transactions_splitter_sizes`](#-function-persist_transactions_splitter_sizes)
- [🔧 Function `refresh_category_icons_for_theme`](#-function-refresh_category_icons_for_theme)
- [🔧 Function `refresh_category_state_label`](#-function-refresh_category_state_label)

</details>

## 🔧 Function `apply_transactions_column_visibility`

```python
def apply_transactions_column_visibility(host: Any) -> None
```

Re-apply persisted column visibility after the table model is ready.

<details>
<summary>Code:</summary>

```python
def apply_transactions_column_visibility(host: Any) -> None:
    table = host.tableView_transactions
    flags = load_column_visibility()
    for key, column, _label in TOGGLEABLE_COLUMNS:
        visible = flags.get(key, True)
        if column < 0:
            _set_record_id_visible(table, visible=visible, persist=False)
        else:
            _set_data_column_visible(table, column, visible=visible, persist=False, refill=False)
    _apply_day_header_column_policy(table)
    from harrix_swiss_knife.apps.finance.transaction_day_headers import (  # noqa: PLC0415
        TransactionDayHeaderProxy,
        apply_transaction_day_header_spans,
    )

    if isinstance(table.model(), TransactionDayHeaderProxy):
        apply_transaction_day_header_spans(table)
    else:
        table.clearSpans()
    apply_transactions_table_column_widths(table, force=True)
```

</details>

## 🔧 Function `apply_transactions_table_column_widths`

```python
def apply_transactions_table_column_widths(table_view: QTableView, *, force: bool = False) -> None
```

Fill the viewport among _visible_ columns, then keep them Interactive.

Date / Total (and any user-hidden columns) must not reserve space.
Description gets a larger share than English / Category; Amount / Currency /
Tag stay compact.

<details>
<summary>Code:</summary>

```python
def apply_transactions_table_column_widths(table_view: QTableView, *, force: bool = False) -> None:
    bind_column_fill_on_resize(table_view, apply_transactions_table_column_widths)
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
    widths = _visible_transaction_column_widths(
        viewport_w,
        count,
        visible=visible,
        min_size=min_size,
    )

    table_view.setProperty("hskColumnFillGuard", 1)
    try:
        for column in range(count):
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            # Zero hidden sections so they cannot inflate header.length().
            table_view.setColumnWidth(column, widths[column] if column in set(visible) else 0)
    finally:
        table_view.setProperty("hskColumnFillGuard", 0)
```

</details>

## 🔧 Function `category_state_text`

```python
def category_state_text(display_name: str | None) -> str
```

Return the one-line form category indicator (long hint stays in the tooltip).

<details>
<summary>Code:</summary>

```python
def category_state_text(display_name: str | None) -> str:
    name = (display_name or "").strip()
    if not name:
        return _NO_CATEGORY
    lowered = name.casefold()
    if lowered.startswith(_CATEGORY_PREFIX.casefold()):
        return name.split("\n", 1)[0].strip()
    if lowered in {_NO_CATEGORY.casefold(), "no category selected"}:
        return _NO_CATEGORY
    return f"{_CATEGORY_PREFIX}{name}"
```

</details>

## 🔧 Function `install_transactions_entry_chrome`

```python
def install_transactions_entry_chrome(host: Any) -> None
```

Polish the Transactions form, category list, splitter, and table chrome.

<details>
<summary>Code:</summary>

```python
def install_transactions_entry_chrome(host: Any) -> None:
    _polish_form_column(host)
    _polish_category_list(host)
    _polish_entry_surfaces(host)
    _polish_transactions_table(host)
    _configure_transactions_splitter(host)
    if not getattr(host, "_transactions_entry_theme_bound", False):

        def _refresh_theme() -> None:
            _polish_form_column(host)
            _polish_category_list(host)
            _polish_entry_surfaces(host)
            refresh_category_icons_for_theme(host)

        bind_theme(host, _refresh_theme)
        host._transactions_entry_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_transactions_splitter_sizes`

```python
def persist_transactions_splitter_sizes(host: Any) -> None
```

Save current Transactions-tab splitter sizes.

<details>
<summary>Code:</summary>

```python
def persist_transactions_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter"):
        return
    sizes = host.splitter.sizes()
    if len(sizes) == EXPECTED_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_splitter_sizes([int(size) for size in sizes])
```

</details>

## 🔧 Function `refresh_category_icons_for_theme`

```python
def refresh_category_icons_for_theme(host: Any) -> None
```

Repaint category Lucide icons after light/dark chrome changes.

<details>
<summary>Code:</summary>

```python
def refresh_category_icons_for_theme(host: Any) -> None:
    view = getattr(host, "listView_categories", None)
    if view is not None:
        viewport = view.viewport()
        if viewport is not None:
            viewport.update()

    table = getattr(host, "tableView_transactions", None)
    if table is None:
        return
    source = _leaf_standard_item_model(table.model())
    if source is None:
        return
    for row in range(source.rowCount()):
        item = source.item(row, TRANSACTION_COL_CATEGORY)
        if item is None:
            continue
        emoji = item.data(ICON_ROLE)
        lucide = item.data(ICON_LUCIDE_ROLE)
        emoji_text = "" if emoji is None else str(emoji)
        lucide_text = "" if lucide is None else str(lucide)
        if not emoji_text and not lucide_text:
            continue
        item.setIcon(category_lucide_icon(emoji_text, lucide_name=lucide_text))
    viewport = table.viewport()
    if viewport is not None:
        viewport.update()
```

</details>

## 🔧 Function `refresh_category_state_label`

```python
def refresh_category_state_label(host: Any, display_name: str | None = None) -> None
```

Update `label_category_now` with a Fluent status string.

<details>
<summary>Code:</summary>

```python
def refresh_category_state_label(host: Any, display_name: str | None = None) -> None:
    text = category_state_text(display_name)
    selected = bool((display_name or "").strip()) and not text.startswith(_NO_CATEGORY)
    host.label_category_now.setText(text)
    host.label_category_now.setWordWrap(True)
    host.label_category_now.setToolTip(_CATEGORY_HINT if not selected else text.split("\n", 1)[0])
    host.label_category_now.setProperty("hskCategorySelected", selected)
    host.label_category_now.style().unpolish(host.label_category_now)
    host.label_category_now.style().polish(host.label_category_now)
```

</details>
