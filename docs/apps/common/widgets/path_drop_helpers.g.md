---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `path_drop_helpers.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `extract_date_from_filename`](#-function-extract_date_from_filename)
- [🔧 Function `extract_dates_from_paths`](#-function-extract_dates_from_paths)
- [🔧 Function `get_suggested_basename`](#-function-get_suggested_basename)
- [🔧 Function `infer_image_filename_base`](#-function-infer_image_filename_base)
- [🔧 Function `install_url_drop_handlers`](#-function-install_url_drop_handlers)
- [🔧 Function `resolve_date_from_image_batch`](#-function-resolve_date_from_image_batch)
- [🔧 Function `slugify_image_filename_base`](#-function-slugify_image_filename_base)
- [🔧 Function `unique_path_in_folder`](#-function-unique_path_in_folder)
- [🔧 Function `unique_path_numbered`](#-function-unique_path_numbered)

</details>

## 🔧 Function `extract_date_from_filename`

```python
def extract_date_from_filename(path: str) -> str | None
```

Return `yyyy-MM-dd` parsed from a filename stem, or `None` if not found.

<details>
<summary>Code:</summary>

```python
def extract_date_from_filename(path: str) -> str | None:
    stem = Path(path).stem
    if not stem:
        return None

    prefix_match = _ISO_DATE_PREFIX_RE.match(stem)
    if prefix_match:
        candidate = prefix_match.group(1)
        if _is_valid_iso_date(candidate):
            return candidate

    anywhere_match = _ISO_DATE_ANYWHERE_RE.search(stem)
    if anywhere_match:
        candidate = anywhere_match.group(1)
        if _is_valid_iso_date(candidate):
            return candidate

    dot_match = _DOT_DATE_RE.search(stem)
    if dot_match:
        candidate = f"{dot_match.group(1)}-{dot_match.group(2)}-{dot_match.group(3)}"
        if _is_valid_iso_date(candidate):
            return candidate

    compact_match = _COMPACT_DATE_RE.search(stem)
    if compact_match:
        candidate = f"{compact_match.group(1)}-{compact_match.group(2)}-{compact_match.group(3)}"
        if _is_valid_iso_date(candidate):
            return candidate

    return None
```

</details>

## 🔧 Function `extract_dates_from_paths`

```python
def extract_dates_from_paths(paths: list[str]) -> list[str]
```

Return sorted unique ISO dates extracted from `paths`.

<details>
<summary>Code:</summary>

```python
def extract_dates_from_paths(paths: list[str]) -> list[str]:
    dates: list[str] = []
    seen: set[str] = set()
    for path in paths:
        parsed = extract_date_from_filename(path)
        if parsed and parsed not in seen:
            seen.add(parsed)
            dates.append(parsed)
    return sorted(dates)
```

</details>

## 🔧 Function `get_suggested_basename`

```python
def get_suggested_basename(filename_line_edit: QLineEdit | None, fallback: str) -> str
```

Return suggested filename stem from a filename field or fallback.

<details>
<summary>Code:</summary>

```python
def get_suggested_basename(filename_line_edit: QLineEdit | None, fallback: str) -> str:
    if filename_line_edit is None:
        return fallback
    text = filename_line_edit.text().strip()
    if not text:
        return fallback
    size_limit = 200
    safe = re.sub(r'[<>:"/\\|?*]', "_", text).strip(" .") or fallback
    return safe[:size_limit] if len(safe) > size_limit else safe
```

</details>

## 🔧 Function `infer_image_filename_base`

```python
def infer_image_filename_base(paths: list[str]) -> str | None
```

Infer shared filename base from existing image paths (strips suffixes such as `_01` and `_02`).

<details>
<summary>Code:</summary>

```python
def infer_image_filename_base(paths: list[str]) -> str | None:
    bases: list[str] = []
    for path in paths:
        if not path.strip():
            continue
        stem = Path(path).stem
        match = _NUMBERED_STEM_RE.match(stem)
        bases.append(match.group(1) if match else stem)
    if not bases:
        return None
    unique_bases = set(bases)
    if len(unique_bases) == 1:
        return bases[0]
    return bases[0]
```

</details>

## 🔧 Function `install_url_drop_handlers`

```python
def install_url_drop_handlers(widget: QWidget, on_drop_paths: Callable[[list[str]], None]) -> None
```

Install drag-and-drop handlers that pass local file paths to `on_drop_paths`.

<details>
<summary>Code:</summary>

```python
def install_url_drop_handlers(
    widget: QWidget,
    on_drop_paths: Callable[[list[str]], None],
    *,
    filter_path: Callable[[str], bool] | None = None,
) -> None:

    def drag_enter_event(event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def drop_event(event: QDropEvent) -> None:
        if not event.mimeData().hasUrls():
            return
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.toLocalFile()]
        if filter_path is not None:
            paths = [path for path in paths if filter_path(path)]
        if paths:
            on_drop_paths(paths)
        event.acceptProposedAction()

    widget.setAcceptDrops(True)
    widget.dragEnterEvent = drag_enter_event  # ty: ignore[invalid-assignment]
    widget.dropEvent = drop_event  # ty: ignore[invalid-assignment]
```

</details>

## 🔧 Function `resolve_date_from_image_batch`

```python
def resolve_date_from_image_batch(extracted_dates: list[str]) -> str | None
```

Pick a date to apply from a batch of extracted filename dates.

<details>
<summary>Code:</summary>

```python
def resolve_date_from_image_batch(
    extracted_dates: list[str],
    *,
    overwrite: bool,
    current_is_empty: bool,
) -> str | None:
    if not extracted_dates:
        return None
    if overwrite:
        return extracted_dates[-1]
    if current_is_empty:
        return extracted_dates[0]
    return None
```

</details>

## 🔧 Function `slugify_image_filename_base`

```python
def slugify_image_filename_base(text: str) -> str
```

Return a lowercase slug for image filename base (spaces to underscores, specials removed).

<details>
<summary>Code:</summary>

```python
def slugify_image_filename_base(text: str) -> str:
    cleaned = text.strip().lower()
    if not cleaned:
        return ""
    slug = re.sub(r"[^\w]+", "_", cleaned, flags=re.UNICODE)
    slug = re.sub(r"_+", "_", slug).strip("_")
    size_limit = 200
    return slug[:size_limit] if len(slug) > size_limit else slug
```

</details>

## 🔧 Function `unique_path_in_folder`

```python
def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path
```

Return a path in folder that does not exist, using base_name and suffix with \_1, \_2 if needed.

<details>
<summary>Code:</summary>

```python
def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path:
    path = folder / (base_name + suffix)
    if not path.exists():
        return path
    i = 1
    while True:
        path = folder / (f"{base_name}_{i}{suffix}")
        if not path.exists():
            return path
        i += 1
```

</details>

## 🔧 Function `unique_path_numbered`

```python
def unique_path_numbered(folder: Path, base_name: str, suffix: str, width: int = 2) -> Path
```

Return unused path using `base_name_01`, `base_name_02`, and so on.

<details>
<summary>Code:</summary>

```python
def unique_path_numbered(folder: Path, base_name: str, suffix: str, width: int = 2) -> Path:
    i = 1
    while True:
        num = str(i).zfill(width)
        path = folder / (f"{base_name}_{num}{suffix}")
        if not path.exists():
            return path
        i += 1
```

</details>
