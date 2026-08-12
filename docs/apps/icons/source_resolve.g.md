---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `source_resolve.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `candidate_source_stems`](#-function-candidate_source_stems)
- [🔧 Function `find_icon_source_file`](#-function-find_icon_source_file)
- [🔧 Function `resolve_external_ai_root`](#-function-resolve_external_ai_root)
- [🔧 Function `source_search_directories`](#-function-source_search_directories)

</details>

## 🔧 Function `candidate_source_stems`

```python
def candidate_source_stems(family_id: str, svg_path: Path | None = None) -> list[str]
```

Return ordered stem candidates for looking up a source master file.

Prefers the SVG stem, then the same stem without color/line tokens
(e.g. `fiction__alien_white_02` → `fiction__alien_02`), then family ID.

<details>
<summary>Code:</summary>

```python
def candidate_source_stems(family_id: str, svg_path: Path | None = None) -> list[str]:
    stems: list[str] = []

    def add(stem: str) -> None:
        cleaned = stem.strip()
        if cleaned and cleaned not in stems:
            stems.append(cleaned)

    if svg_path is not None:
        stem = svg_path.stem
        if stem.casefold() != "featured-image":
            add(stem)
            add(_VARIANT_TOKEN_RE.sub("", stem))
    add(family_id)
    return stems
```

</details>

## 🔧 Function `find_icon_source_file`

```python
def find_icon_source_file(*, family_id: str, note_dir: Path, svg_path: Path | None = None, external_ai_root: Path | None = None) -> Path | None
```

Find a vector source file for an icon family / selected SVG.

Search order:

1. Note `files/` (beautify-md destination for `.ai` / `.pdf` / …)
2. Note root
3. Note `img/`
4. External AI dump (`path_vector_icons_ai`): flat files in `src/` or the root itself
   (no per-icon subfolders)

<details>
<summary>Code:</summary>

```python
def find_icon_source_file(
    *,
    family_id: str,
    note_dir: Path,
    svg_path: Path | None = None,
    external_ai_root: Path | None = None,
) -> Path | None:
    stems = candidate_source_stems(family_id, svg_path)
    for directory in source_search_directories(note_dir, external_ai_root):
        found = _first_matching_source(directory, stems)
        if found is not None:
            return found
    return None
```

</details>

## 🔧 Function `resolve_external_ai_root`

```python
def resolve_external_ai_root(raw: str | Path | None) -> Path | None
```

Normalize `path_vector_icons_ai` to an existing directory, or `None`.

<details>
<summary>Code:</summary>

```python
def resolve_external_ai_root(raw: str | Path | None) -> Path | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.startswith("<"):
        return None
    path = Path(text)
    return path if path.is_dir() else None
```

</details>

## 🔧 Function `source_search_directories`

```python
def source_search_directories(note_dir: Path, external_ai_root: Path | None = None) -> list[Path]
```

Return existing directories to search for source masters.

External AI sources are treated as a flat dump: either `…/src/*.ai` or
`path_vector_icons_ai/*.ai` when the config path already points at `src`.

<details>
<summary>Code:</summary>

```python
def source_search_directories(note_dir: Path, external_ai_root: Path | None = None) -> list[Path]:
    dirs: list[Path] = []

    def add(path: Path) -> None:
        if path.is_dir() and path not in dirs:
            dirs.append(path)

    add(note_dir / "files")
    add(note_dir)
    add(note_dir / "img")

    if external_ai_root is not None:
        add(external_ai_root / "src")
        add(external_ai_root)
    return dirs
```

</details>
