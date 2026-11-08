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
- [🔧 Function `category_state_text`](#-function-category_state_text)
- [🔧 Function `install_transactions_entry_chrome`](#-function-install_transactions_entry_chrome)
- [🔧 Function `persist_transactions_splitter_sizes`](#-function-persist_transactions_splitter_sizes)
- [🔧 Function `refresh_category_state_label`](#-function-refresh_category_state_label)

</details>

## 🔧 Function `apply_transactions_column_visibility`

```python
def apply_transactions_column_visibility(host: Any) -> None
```

Re-apply persisted English/ID visibility after the table model is ready.

<details>
<summary>Code:</summary>

```python
def apply_transactions_column_visibility(host: Any) -> None:
    table = host.tableView_transactions
    flags = load_column_visibility()
    _set_english_visible(table, visible=flags.get(_VIS_KEY_ENGLISH, True), persist=False)
    _set_record_id_visible(table, visible=flags.get(_VIS_KEY_RECORD_ID, True), persist=False)
```

</details>

## 🔧 Function `category_state_text`

```python
def category_state_text(display_name: str | None) -> str
```

Return the form category indicator text.

<details>
<summary>Code:</summary>

```python
def category_state_text(display_name: str | None) -> str:
    name = (display_name or "").strip()
    if not name:
        return _NO_CATEGORY
    lowered = name.casefold()
    if lowered.startswith("category:"):
        return name
    if lowered == _NO_CATEGORY.casefold():
        return _NO_CATEGORY
    return f"Category: {name}"
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

## 🔧 Function `refresh_category_state_label`

```python
def refresh_category_state_label(host: Any, display_name: str | None = None) -> None
```

Update `label_category_now` with a Fluent status string.

<details>
<summary>Code:</summary>

```python
def refresh_category_state_label(host: Any, display_name: str | None = None) -> None:
    host.label_category_now.setText(category_state_text(display_name))
    host.label_category_now.setProperty("hskCategorySelected", bool((display_name or "").strip()))
    host.label_category_now.style().unpolish(host.label_category_now)
    host.label_category_now.style().polish(host.label_category_now)
```

</details>
