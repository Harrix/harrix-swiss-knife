---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `parse.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `display_text`](#-function-display_text)
- [🔧 Function `hint_tooltip`](#-function-hint_tooltip)
- [🔧 Function `item_matches_search`](#-function-item_matches_search)
- [🔧 Function `parse_bulk_lines`](#-function-parse_bulk_lines)
- [🔧 Function `parse_value_hint_line`](#-function-parse_value_hint_line)
- [🔧 Function `serialize_items`](#-function-serialize_items)
- [🔧 Function `strip_wrapping_brackets`](#-function-strip_wrapping_brackets)

</details>

## 🔧 Function `display_text`

```python
def display_text(value: str, hint: str, zone: str) -> str
```

Return the list label for one item.

<details>
<summary>Code:</summary>

```python
def display_text(value: str, hint: str, zone: str) -> str:
    if zone in {ZONE_SYMBOL, ZONE_COLOR} and hint:
        return f"{value} [{hint}]"
    return value
```

</details>

## 🔧 Function `hint_tooltip`

```python
def hint_tooltip(hint: str, fallback: str = '') -> str
```

Return hover text without wrapping square brackets.

<details>
<summary>Code:</summary>

```python
def hint_tooltip(hint: str, fallback: str = "") -> str:
    text = strip_wrapping_brackets(hint)
    return text or fallback
```

</details>

## 🔧 Function `item_matches_search`

```python
def item_matches_search(value: str, hint: str, query: str) -> bool
```

Return whether value or hint matches `query` (case and layout insensitive).

<details>
<summary>Code:</summary>

```python
def item_matches_search(value: str, hint: str, query: str) -> bool:
    if command_matches_search(value, query):
        return True
    return bool(hint) and command_matches_search(hint, query)
```

</details>

## 🔧 Function `parse_bulk_lines`

```python
def parse_bulk_lines(text: str, zone: str) -> list[tuple[str, str]]
```

Parse a multiline editor payload into `(value, hint)` pairs.

<details>
<summary>Code:</summary>

```python
def parse_bulk_lines(text: str, zone: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if zone in {ZONE_PHRASE, ZONE_EMOJI}:
            items.append((line, ""))
            continue
        parsed = parse_value_hint_line(line)
        if parsed is None or not parsed[0]:
            continue
        items.append(parsed)
    return items
```

</details>

## 🔧 Function `parse_value_hint_line`

```python
def parse_value_hint_line(line: str) -> tuple[str, str] | None
```

Parse one bulk-edit line into `(value, hint)`.

Empty lines are skipped (`None`). Phrases and emoji use the whole line as
the value. Symbols and colors accept `value | hint` or `value: hint`.

<details>
<summary>Code:</summary>

```python
def parse_value_hint_line(line: str) -> tuple[str, str] | None:
    text = line.strip()
    if not text:
        return None
    if " | " in text:
        value, hint = text.split(" | ", 1)
        return value.strip(), hint.strip()
    if text.startswith("#") and ":" in text:
        value, hint = text.split(":", 1)
        return value.strip(), hint.strip()
    return text, ""
```

</details>

## 🔧 Function `serialize_items`

```python
def serialize_items(items: Sequence[SnippetItem], zone: str) -> str
```

Serialize items for the edit-entire-list dialog.

<details>
<summary>Code:</summary>

```python
def serialize_items(items: Sequence[SnippetItem], zone: str) -> str:
    lines: list[str] = []
    for item in items:
        if zone in {ZONE_SYMBOL, ZONE_COLOR} and item.hint:
            lines.append(f"{item.value} | {item.hint}")
        else:
            lines.append(item.value)
    return "\n".join(lines)
```

</details>

## 🔧 Function `strip_wrapping_brackets`

```python
def strip_wrapping_brackets(text: str) -> str
```

Remove one pair of surrounding `[]`, if present.

<details>
<summary>Code:</summary>

```python
def strip_wrapping_brackets(text: str) -> str:
    value = text.strip()
    if value.startswith("[") and value.endswith("]"):
        return value[1:-1].strip()
    return value
```

</details>
