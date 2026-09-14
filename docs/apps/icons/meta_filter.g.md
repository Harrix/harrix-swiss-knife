---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `meta_filter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_variants_header_html`](#-function-build_variants_header_html)
- [🔧 Function `count_families_for_meta`](#-function-count_families_for_meta)
- [🔧 Function `family_matches_meta`](#-function-family_matches_meta)
- [🔧 Function `filter_families_by_meta`](#-function-filter_families_by_meta)
- [🔧 Function `meta_filter_label`](#-function-meta_filter_label)
- [🔧 Function `meta_link_href`](#-function-meta_link_href)
- [🔧 Function `parse_meta_link`](#-function-parse_meta_link)

</details>

## 🔧 Function `build_variants_header_html`

```python
def build_variants_header_html(family: IconFamily, icons: Sequence[IconFamily]) -> str
```

Return rich-text header with blue links when other icons share meta values.

<details>
<summary>Code:</summary>

```python
def build_variants_header_html(family: IconFamily, icons: Sequence[IconFamily]) -> str:
    lines = [
        html.escape(family.title),
        html.escape(family.id),
    ]
    if family.date.strip():
        lines.append(f"Date: {_meta_value_html(icons, META_KIND_DATE, family.date.strip())}")
    categories = [item.strip() for item in family.categories if item.strip()]
    if categories:
        parts = [_meta_value_html(icons, META_KIND_CATEGORY, item) for item in categories]
        lines.append("Categories: " + ", ".join(parts))
    else:
        lines.append("Categories: —")
    tags = [item.strip() for item in family.tags if item.strip()]
    if tags:
        parts = [_meta_value_html(icons, META_KIND_TAG, item) for item in tags]
        lines.append("Tags: " + ", ".join(parts))
    else:
        lines.append("Tags: —")
    return "<br/>".join(lines)
```

</details>

## 🔧 Function `count_families_for_meta`

```python
def count_families_for_meta(icons: Sequence[IconFamily], kind: str, value: str) -> int
```

Return how many families match the meta filter.

<details>
<summary>Code:</summary>

```python
def count_families_for_meta(icons: Sequence[IconFamily], kind: str, value: str) -> int:
    needle = value.strip()
    if not needle or kind not in _META_KINDS:
        return 0
    return sum(1 for family in icons if family_matches_meta(family, kind, needle))
```

</details>

## 🔧 Function `family_matches_meta`

```python
def family_matches_meta(family: IconFamily, kind: str, value: str) -> bool
```

Return whether `family` matches a category, tag, or date filter.

<details>
<summary>Code:</summary>

```python
def family_matches_meta(family: IconFamily, kind: str, value: str) -> bool:
    needle = value.strip()
    if not needle:
        return False
    if kind == META_KIND_CATEGORY:
        return any(item.strip().casefold() == needle.casefold() for item in family.categories)
    if kind == META_KIND_TAG:
        return any(item.strip().casefold() == needle.casefold() for item in family.tags)
    if kind == META_KIND_DATE:
        return family.date.strip() == needle
    return False
```

</details>

## 🔧 Function `filter_families_by_meta`

```python
def filter_families_by_meta(icons: Sequence[IconFamily], kind: str, value: str) -> list[IconFamily]
```

Return families matching the meta filter, preserving input order.

<details>
<summary>Code:</summary>

```python
def filter_families_by_meta(icons: Sequence[IconFamily], kind: str, value: str) -> list[IconFamily]:
    return [family for family in icons if family_matches_meta(family, kind, value)]
```

</details>

## 🔧 Function `meta_filter_label`

```python
def meta_filter_label(kind: str, value: str) -> str
```

Return a short human-readable label for the active meta filter bar.

<details>
<summary>Code:</summary>

```python
def meta_filter_label(kind: str, value: str) -> str:
    cleaned = value.strip()
    if kind == META_KIND_CATEGORY:
        return f"Category: {cleaned}"
    if kind == META_KIND_TAG:
        return f"Tag: {cleaned}"
    if kind == META_KIND_DATE:
        return f"Date: {cleaned}"
    return cleaned
```

</details>

## 🔧 Function `meta_link_href`

```python
def meta_link_href(kind: str, value: str) -> str
```

Return a custom URL for a variants-header meta link.

<details>
<summary>Code:</summary>

```python
def meta_link_href(kind: str, value: str) -> str:
    return f"{META_LINK_SCHEME}:{kind}/{quote(value.strip(), safe='')}"
```

</details>

## 🔧 Function `parse_meta_link`

```python
def parse_meta_link(href: str) -> tuple[str, str] | None
```

Parse `hsk-meta:kind/value` from a QLabel link activation.

<details>
<summary>Code:</summary>

```python
def parse_meta_link(href: str) -> tuple[str, str] | None:
    text = href.strip()
    prefix = f"{META_LINK_SCHEME}:"
    if not text.startswith(prefix):
        return None
    rest = text[len(prefix) :]
    kind, sep, raw_value = rest.partition("/")
    if not sep or kind not in _META_KINDS:
        return None
    value = unquote(raw_value).strip()
    if not value:
        return None
    return kind, value
```

</details>
