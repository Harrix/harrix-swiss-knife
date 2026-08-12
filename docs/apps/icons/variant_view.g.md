---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `variant_view.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `GridEntry`](#%EF%B8%8F-class-gridentry)
- [🔧 Function `build_grid_entries`](#-function-build_grid_entries)
- [🔧 Function `classify_variant_kind`](#-function-classify_variant_kind)

</details>

## 🏛️ Class `GridEntry`

```python
class GridEntry
```

One tile in the main icon grid.

<details>
<summary>Code:</summary>

```python
class GridEntry:

    family: IconFamily
    svg_path: Path
    is_fallback: bool = False
```

</details>

## 🔧 Function `build_grid_entries`

```python
def build_grid_entries(families: list[IconFamily], *, repo_root: Path, mode: str) -> list[GridEntry]
```

Build main-grid tiles for the selected variant view mode.

Kind modes (`white`, `black`, …) list matching variants first; families
without that kind append their featured/ordinary tile at the end.

<details>
<summary>Code:</summary>

```python
def build_grid_entries(
    families: list[IconFamily],
    *,
    repo_root: Path,
    mode: str,
) -> list[GridEntry]:
    known = {key for key, _ in VARIANT_VIEW_MODES}
    normalized = mode if mode in known else MODE_FEATURED

    if normalized == MODE_FEATURED:
        entries: list[GridEntry] = []
        for family in families:
            featured = _featured_entry(family, repo_root)
            if featured is not None:
                entries.append(featured)
        return entries

    if normalized == MODE_ALL:
        entries = []
        for family in families:
            if family.variants:
                entries.extend(_variant_entries(family, repo_root, variants=family.variants))
            else:
                featured = _featured_entry(family, repo_root)
                if featured is not None:
                    entries.append(featured)
        return entries

    if normalized == MODE_COLOR:
        matched: list[GridEntry] = []
        fallback: list[GridEntry] = []
        for family in families:
            color_variants = [item for item in family.variants if classify_variant_kind(item.name) == MODE_COLOR]
            if color_variants:
                matched.extend(_variant_entries(family, repo_root, variants=color_variants))
            else:
                featured = _featured_entry(family, repo_root, is_fallback=True)
                if featured is not None:
                    fallback.append(featured)
        return matched + fallback

    # Specific kind: white / black / gray / line-*
    matched = []
    fallback = []
    for family in families:
        kind_variants = [item for item in family.variants if classify_variant_kind(item.name) == normalized]
        if kind_variants:
            matched.extend(_variant_entries(family, repo_root, variants=kind_variants))
        else:
            featured = _featured_entry(family, repo_root, is_fallback=True)
            if featured is not None:
                fallback.append(featured)
    return matched + fallback
```

</details>

## 🔧 Function `classify_variant_kind`

```python
def classify_variant_kind(stem: str) -> str
```

Return kind token for an SVG stem (`color`, `white`, `line-16`, …).

<details>
<summary>Code:</summary>

```python
def classify_variant_kind(stem: str) -> str:
    text = stem.casefold()
    line_match = _LINE_RE.search(text)
    if line_match is not None:
        return f"line-{line_match.group(1)}"
    color_match = _COLOR_TOKEN_RE.search(text)
    if color_match is not None:
        color_kind = color_match.group(1).casefold()
        return "gray" if color_kind == "grey" else color_kind
    return MODE_COLOR
```

</details>
