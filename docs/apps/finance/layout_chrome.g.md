---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_exchange_rates_table_column_widths`](#-function-apply_exchange_rates_table_column_widths)
- [🔧 Function `install_finance_layout_chrome`](#-function-install_finance_layout_chrome)
- [🔧 Function `persist_finance_tabs_splitter_sizes`](#-function-persist_finance_tabs_splitter_sizes)

</details>

## 🔧 Function `apply_exchange_rates_table_column_widths`

```python
def apply_exchange_rates_table_column_widths(table: QTableView, *, force: bool = False) -> None
```

Give Rate the leftover width; keep From/To/Date compact so values fit.

<details>
<summary>Code:</summary>

```python
def apply_exchange_rates_table_column_widths(table: QTableView, *, force: bool = False) -> None:
    bind_column_fill_on_resize(table, apply_exchange_rates_table_column_widths)
    if not table.isVisible() or user_resized_columns(table):
        return
    header = table.horizontalHeader()
    if header.count() < _RATES_COLUMN_COUNT or table.property("hskColumnFillGuard"):
        return
    viewport_w = table.viewport().width()
    if viewport_w <= 0:
        return
    if not force and columns_fill_viewport(table):
        return

    rate_w = max(
        viewport_w - _RATES_FROM_WIDTH - _RATES_TO_WIDTH - _RATES_DATE_WIDTH,
        _RATES_RATE_MIN_WIDTH,
    )
    widths = {
        _RATES_COL_FROM: _RATES_FROM_WIDTH,
        _RATES_COL_TO: _RATES_TO_WIDTH,
        _RATES_COL_RATE: rate_w,
        _RATES_COL_DATE: _RATES_DATE_WIDTH,
    }
    header.setStretchLastSection(False)
    table.setProperty("hskColumnFillGuard", 1)
    try:
        for column, width in widths.items():
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            table.setColumnWidth(column, width)
    finally:
        table.setProperty("hskColumnFillGuard", 0)
```

</details>

## 🔧 Function `install_finance_layout_chrome`

```python
def install_finance_layout_chrome(host: Any) -> None
```

Polish Accounts / Exchange / Rates / Charts / Reports with flat panes.

<details>
<summary>Code:</summary>

```python
def install_finance_layout_chrome(host: Any) -> None:
    _polish_all_tabs(host)
    _configure_all_splitters(host)
    if not getattr(host, "_finance_tabs_theme_bound", False):
        bind_theme(host, lambda: _polish_all_tabs(host))
        host._finance_tabs_theme_bound = True  # noqa: SLF001
```

</details>

## 🔧 Function `persist_finance_tabs_splitter_sizes`

```python
def persist_finance_tabs_splitter_sizes(host: Any) -> None
```

Save splitter sizes for every non-Transactions Finance tab.

<details>
<summary>Code:</summary>

```python
def persist_finance_tabs_splitter_sizes(host: Any) -> None:
    if getattr(host, "_is_closing", False):
        return
    _persist_named_splitter(host, "splitter_2", save_accounts_splitter_sizes)
    _persist_named_splitter(host, "splitter_4", save_exchange_splitter_sizes)
    _persist_named_splitter(host, "splitter_6", save_rates_splitter_sizes)
    _persist_named_splitter(host, "splitter_7", save_charts_splitter_sizes)
    _persist_named_splitter(host, "splitter_5", save_reports_splitter_sizes)
```

</details>
