---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_entry_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `food_item_state_text`](#-function-food_item_state_text)
- [🔧 Function `install_food_entry_chrome`](#-function-install_food_entry_chrome)
- [🔧 Function `persist_food_splitter_sizes`](#-function-persist_food_splitter_sizes)
- [🔧 Function `refresh_food_item_state_label`](#-function-refresh_food_item_state_label)

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
