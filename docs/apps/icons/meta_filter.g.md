---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `meta_filter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MetaChrome`](#%EF%B8%8F-class-metachrome)
- [🔧 Function `build_meta_date_html`](#-function-build_meta_date_html)
- [🔧 Function `build_meta_list_html`](#-function-build_meta_list_html)
- [🔧 Function `build_variants_header_html`](#-function-build_variants_header_html)
- [🔧 Function `count_families_for_meta`](#-function-count_families_for_meta)
- [🔧 Function `family_matches_meta`](#-function-family_matches_meta)
- [🔧 Function `filter_families_by_meta`](#-function-filter_families_by_meta)
- [🔧 Function `light_meta_chrome`](#-function-light_meta_chrome)
- [🔧 Function `meta_chrome_for_palette`](#-function-meta_chrome_for_palette)
- [🔧 Function `meta_filter_label`](#-function-meta_filter_label)
- [🔧 Function `meta_link_href`](#-function-meta_link_href)
- [🔧 Function `parse_meta_link`](#-function-parse_meta_link)

</details>

## 🏛️ Class `MetaChrome`

```python
class MetaChrome
```

Inline HTML colors for the variants meta header.

<details>
<summary>Code:</summary>

```python
class MetaChrome:

    chip_bg: str
    chip_fg: str
    chip_count: str
    plain: str
    id_color: str
```

</details>

## 🔧 Function `build_meta_date_html`

```python
def build_meta_date_html(icons: Sequence[IconFamily], date: str, *, chrome: MetaChrome | None = None) -> str
```

Return HTML for a date value, with a count link when shared by other icons.

<details>
<summary>Code:</summary>

```python
def build_meta_date_html(
    icons: Sequence[IconFamily],
    date: str,
    *,
    chrome: MetaChrome | None = None,
) -> str:
    cleaned = date.strip()
    if not cleaned:
        return "—"
    return _meta_value_html(icons, META_KIND_DATE, cleaned, chrome=chrome or light_meta_chrome())
```

</details>

## 🔧 Function `build_meta_list_html`

```python
def build_meta_list_html(icons: Sequence[IconFamily], kind: str, values: Sequence[str], *, chrome: MetaChrome | None = None) -> str
```

Return HTML for category/tag lists with count links when shared.

<details>
<summary>Code:</summary>

```python
def build_meta_list_html(
    icons: Sequence[IconFamily],
    kind: str,
    values: Sequence[str],
    *,
    chrome: MetaChrome | None = None,
) -> str:
    cleaned = [item.strip() for item in values if item.strip()]
    if not cleaned:
        return "—"
    style = chrome or light_meta_chrome()
    return " ".join(_meta_value_html(icons, kind, item, chrome=style) for item in cleaned)
```

</details>

## 🔧 Function `build_variants_header_html`

```python
def build_variants_header_html(family: IconFamily, icons: Sequence[IconFamily], *, chrome: MetaChrome | None = None) -> str
```

Return rich-text header with grouped title, meta, and tags.

<details>
<summary>Code:</summary>

```python
def build_variants_header_html(
    family: IconFamily,
    icons: Sequence[IconFamily],
    *,
    chrome: MetaChrome | None = None,
) -> str:
    style = chrome or light_meta_chrome()
    label = f"color:{style.id_color};font-size:11px;font-weight:600;margin:0 0 2px 0;"
    section = "margin-top:10px;"
    lines = [
        f'<div style="font-weight:600;font-size:13px;">{html.escape(family.title)}</div>',
        f'<div style="color:{style.id_color};font-size:11px;margin-top:2px;">{html.escape(family.id)}</div>',
        f'<div style="{section}"><div style="{label}">Date</div>',
        f"<div>{build_meta_date_html(icons, family.date, chrome=style)}</div></div>",
    ]
    categories = [item.strip() for item in family.categories if item.strip()]
    categories_html = build_meta_list_html(icons, META_KIND_CATEGORY, categories, chrome=style) if categories else "—"
    lines.append(
        f'<div style="{section}"><div style="{label}">Categories</div><div>{categories_html}</div></div>',
    )
    tags = [item.strip() for item in family.tags if item.strip()]
    tags_html = build_meta_list_html(icons, META_KIND_TAG, tags, chrome=style) if tags else "—"
    lines.append(
        f'<div style="{section}"><div style="{label}">Tags</div><div style="line-height:1.55;">{tags_html}</div></div>',
    )
    return "".join(lines)
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

## 🔧 Function `light_meta_chrome`

```python
def light_meta_chrome() -> MetaChrome
```

Return chip colors for the light theme (also used as HTML defaults).

<details>
<summary>Code:</summary>

```python
def light_meta_chrome() -> MetaChrome:
    return MetaChrome(
        chip_bg=SELECTION_BG,
        chip_fg=BRAND_INK,
        chip_count="#6a6a6a",
        plain="#444444",
        id_color=MUTED_TEXT,
    )
```

</details>

## 🔧 Function `meta_chrome_for_palette`

```python
def meta_chrome_for_palette(palette: FluentPalette) -> MetaChrome
```

Return meta chip colors that stay readable on the active Fluent palette.

<details>
<summary>Code:</summary>

```python
def meta_chrome_for_palette(palette: FluentPalette) -> MetaChrome:
    if not palette.dark:
        return light_meta_chrome()
    chip_fill = mix(palette.window_bg, QColor(palette.accent.red(), palette.accent.green(), palette.accent.blue(), 72))
    return MetaChrome(
        chip_bg=css(chip_fill),
        chip_fg=css(mix(palette.window_bg, palette.accent_text)),
        chip_count=css(mix(palette.window_bg, palette.text_secondary)),
        plain=css(mix(palette.window_bg, palette.text_primary)),
        id_color=css(mix(palette.window_bg, palette.text_secondary)),
    )
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
