---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `status_bar_text.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `format_list_view_status`](#-function-format_list_view_status)
- [🔧 Function `format_selection_count_status`](#-function-format_selection_count_status)
- [🔧 Function `format_translate_progress_status`](#-function-format_translate_progress_status)
- [🔧 Function `is_owned_status_message`](#-function-is_owned_status_message)
- [🔧 Function `join_status_parts`](#-function-join_status_parts)

</details>

## 🔧 Function `format_list_view_status`

```python
def format_list_view_status(*, filtered: bool = False, loaded_count: int | None = None, has_more: bool = False) -> str
```

Format filter / pagination context for a list status-bar label.

Args:

- `filtered` (`bool`): Whether an active filter narrows the list.
- `loaded_count` (`int | None`): Rows currently loaded into the view.
- `has_more` (`bool`): Whether more rows can be loaded by scrolling.

Returns:

- `str`: Status text, or empty when there is nothing useful to show.

<details>
<summary>Code:</summary>

```python
def format_list_view_status(
    *,
    filtered: bool = False,
    loaded_count: int | None = None,
    has_more: bool = False,
) -> str:
    parts: list[str] = []
    if filtered:
        parts.append("Filtered")
    if loaded_count is not None and loaded_count > 0:
        parts.append(f"{loaded_count} loaded")
    if has_more:
        parts.append("more below")
    return " · ".join(parts)
```

</details>

## 🔧 Function `format_selection_count_status`

```python
def format_selection_count_status(count: int, *, unit_singular: str = 'row', unit_plural: str | None = None, detail: str = '') -> str
```

Format a selection summary for a permanent status-bar label.

Args:

- `count` (`int`): Number of selected items.
- `unit_singular` (`str`): Singular unit word (default `row`).
- `unit_plural` (`str | None`): Plural unit; defaults to `unit_singular` + `s`.
- [`detail`](../../installer/log.g.md#%EF%B8%8F-method-detail) (`str`): Optional trailing detail (e.g. sum text without leading separator).

Returns:

- `str`: Status text, or empty when `count <= 0`.

<details>
<summary>Code:</summary>

```python
def format_selection_count_status(
    count: int,
    *,
    unit_singular: str = "row",
    unit_plural: str | None = None,
    detail: str = "",
) -> str:
    if count <= 0:
        return ""
    plural = unit_plural if unit_plural is not None else f"{unit_singular}s"
    unit = unit_singular if count == 1 else plural
    base = f"{count} {unit} selected"
    cleaned = detail.strip()
    if cleaned:
        return f"{base} · {cleaned}"
    return base
```

</details>

## 🔧 Function `format_translate_progress_status`

```python
def format_translate_progress_status(base_message: str, remaining: int | None = None, *, item_label: str = 'left') -> str
```

Format a sticky background-translate status message.

Args:

- `base_message` (`str`): Base sticky text (ellipsis included).
- [`remaining`](../../fluent/widgets/display.g.md#%EF%B8%8F-method-remaining) (`int | None`): Items still missing translation; omit when unknown.
- `item_label` (`str`): Trailing label after the count (e.g. `descriptions left`).

Returns:

- `str`: Status text for `showMessage`.

<details>
<summary>Code:</summary>

```python
def format_translate_progress_status(
    base_message: str,
    remaining: int | None = None,
    *,
    item_label: str = "left",
) -> str:
    cleaned = base_message.strip()
    if remaining is None or remaining <= 0:
        return cleaned
    return f"{cleaned} ({remaining} {item_label.strip()})"
```

</details>

## 🔧 Function `is_owned_status_message`

```python
def is_owned_status_message(current: str, base_message: str) -> bool
```

Return whether `current` is the sticky message owned by `base_message`.

Matches the exact base text or the base with a remaining-count suffix.

<details>
<summary>Code:</summary>

```python
def is_owned_status_message(current: str, base_message: str) -> bool:
    cleaned_current = current.strip()
    cleaned_base = base_message.strip()
    if not cleaned_base:
        return False
    if cleaned_current == cleaned_base:
        return True
    return cleaned_current.startswith(f"{cleaned_base} (")
```

</details>

## 🔧 Function `join_status_parts`

```python
def join_status_parts(*parts: str) -> str
```

Join non-empty status fragments with a middle dot separator.

<details>
<summary>Code:</summary>

```python
def join_status_parts(*parts: str) -> str:
    return " · ".join(part.strip() for part in parts if part and part.strip())
```

</details>
