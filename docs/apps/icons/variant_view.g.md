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
- [🔧 Function `available_variant_view_modes`](#-function-available_variant_view_modes)
- [🔧 Function `build_grid_entries`](#-function-build_grid_entries)
- [🔧 Function `classify_variant_kind`](#-function-classify_variant_kind)
- [🔧 Function `collect_icon_detail_preview_paths`](#-function-collect_icon_detail_preview_paths)

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

## 🔧 Function `available_variant_view_modes`

```python
def available_variant_view_modes(families: list[IconFamily]) -> tuple[str, ...]
```

Return View modes that exist among `families`, always including Featured.

Kind modes appear only when at least one variant has that kind. `All variants`
appears when any family has variant files.

<details>
<summary>Code:</summary>

```python
def available_variant_view_modes(families: list[IconFamily]) -> tuple[str, ...]:
    kinds: set[str] = set()
    has_variants = False
    for family in families:
        if family.variants:
            has_variants = True
        for variant in family.variants:
            kinds.add(classify_variant_kind(variant.name))
    result: list[str] = []
    for mode_id, _label in VARIANT_VIEW_MODES:
        if mode_id == MODE_FEATURED:
            result.append(MODE_FEATURED)
            continue
        if mode_id == MODE_ALL:
            if has_variants:
                result.append(MODE_ALL)
            continue
        if mode_id in kinds:
            result.append(mode_id)
    return tuple(result)
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

## 🔧 Function `collect_icon_detail_preview_paths`

```python
def collect_icon_detail_preview_paths(family: IconFamily, repo_root: Path | None, selected_path: str) -> list[tuple[str, Path]]
```

Return `(label, path)` pairs for Icon details thumbnails.

Includes featured, each variant, and the selected file when it exists.
Duplicate paths (same resolved file) are omitted.

<details>
<summary>Code:</summary>

```python
def collect_icon_detail_preview_paths(
    family: IconFamily,
    repo_root: Path | None,
    selected_path: str,
) -> list[tuple[str, Path]]:
    seen: set[str] = set()
    result: list[tuple[str, Path]] = []

    def add(label: str, path: Path | None) -> None:
        if path is None or not path.is_file():
            return
        try:
            key = str(path.resolve())
        except OSError:
            key = str(path)
        if key in seen:
            return
        seen.add(key)
        result.append((label, path))

    if repo_root is not None:
        add("Featured", family.featured_path(repo_root))
        for variant in family.variants:
            add(variant.name, variant.absolute_path(repo_root, family.folder))
    selected = Path(selected_path)
    add(selected.name, selected if selected.is_file() else None)
    return result
```

</details>
