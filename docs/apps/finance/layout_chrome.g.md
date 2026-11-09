---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `layout_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `install_finance_layout_chrome`](#-function-install_finance_layout_chrome)
- [🔧 Function `persist_finance_tabs_splitter_sizes`](#-function-persist_finance_tabs_splitter_sizes)

</details>

## 🔧 Function `install_finance_layout_chrome`

```python
def install_finance_layout_chrome(host: Any) -> None
```

Polish Accounts / Exchange / Rates / Charts / Reports like Transactions.

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
