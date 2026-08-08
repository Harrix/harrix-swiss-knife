---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `naming.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `allocate_filename`](#-function-allocate_filename)
- [🔧 Function `display_name_prefers_copy`](#-function-display_name_prefers_copy)
- [🔧 Function `extension_for_mime`](#-function-extension_for_mime)
- [🔧 Function `stem_from_date_taken_ms`](#-function-stem_from_date_taken_ms)

</details>

## 🔧 Function `allocate_filename`

```python
def allocate_filename(photos_dir: Path, *, date_taken_epoch_ms: int, extension: str, force_copy: bool, reuse_filename: str | None = None) -> str
```

Choose a destination filename under `photos_dir` (not the full path).

- If `reuse_filename` is set (same MediaStore ID, content changed), keep it.
- Otherwise use `yyyy-MM-dd HH.mm.ss.ext`, or `_copy` / `_copy2` / … when needed.

<details>
<summary>Code:</summary>

```python
def allocate_filename(
    photos_dir: Path,
    *,
    date_taken_epoch_ms: int,
    extension: str,
    force_copy: bool,
    reuse_filename: str | None = None,
) -> str:
    if reuse_filename:
        return reuse_filename

    ext = extension.lstrip(".").lower() or "jpg"
    base = stem_from_date_taken_ms(date_taken_epoch_ms)
    if not force_copy:
        candidate = f"{base}.{ext}"
        if not (photos_dir / candidate).exists():
            return candidate

    # Collision or explicit copy: allocate _copy, _copy2, …
    index = 1
    while True:
        suffix = "_copy" if index == 1 else f"_copy{index}"
        candidate = f"{base}{suffix}.{ext}"
        if not (photos_dir / candidate).exists():
            return candidate
        index += 1
```

</details>

## 🔧 Function `display_name_prefers_copy`

```python
def display_name_prefers_copy(display_name: str | None) -> bool
```

Return `True` when the phone filename already looks like an edited copy.

<details>
<summary>Code:</summary>

```python
def display_name_prefers_copy(display_name: str | None) -> bool:
    if not display_name:
        return False
    stem = Path(display_name).stem
    return bool(re.search(r"_copy\d*$", stem, flags=re.IGNORECASE))
```

</details>

## 🔧 Function `extension_for_mime`

```python
def extension_for_mime(mime_type: str | None, display_name: str | None = None) -> str
```

Return a lowercase file extension without a leading dot.

<details>
<summary>Code:</summary>

```python
def extension_for_mime(mime_type: str | None, display_name: str | None = None) -> str:
    if mime_type:
        mapped = _MIME_EXTENSIONS.get(mime_type.lower().strip())
        if mapped:
            return mapped
    if display_name and "." in display_name:
        ext = display_name.rsplit(".", 1)[-1].lower()
        if ext and ext.isalnum() and len(ext) <= 8:
            return "jpg" if ext == "jpeg" else ext
    return "jpg"
```

</details>

## 🔧 Function `stem_from_date_taken_ms`

```python
def stem_from_date_taken_ms(date_taken_epoch_ms: int) -> str
```

Format capture time as `yyyy-MM-dd HH.mm.ss`.

<details>
<summary>Code:</summary>

```python
def stem_from_date_taken_ms(date_taken_epoch_ms: int) -> str:
    seconds = max(0, int(date_taken_epoch_ms)) / 1000.0
    return datetime.fromtimestamp(seconds).strftime("%Y-%m-%d %H.%M.%S")
```

</details>
