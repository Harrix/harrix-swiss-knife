---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dated_image_path.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `images_folder`](#-function-images_folder)
- [🔧 Function `next_dated_image_path`](#-function-next_dated_image_path)

</details>

## 🔧 Function `images_folder`

```python
def images_folder(project_root: Path) -> Path
```

Return the OnOpenImages folder (`temp/images`) under `project_root`.

<details>
<summary>Code:</summary>

```python
def images_folder(project_root: Path) -> Path:
    return project_root / "temp" / "images"
```

</details>

## 🔧 Function `next_dated_image_path`

```python
def next_dated_image_path(folder: Path, *, today: date | None = None, extension: str = '.png') -> Path
```

Return the next free `YYYY-MM-DD_NN` path in `folder`.

Existing files with the same date stem (any extension) reserve their index
numbers so saves never overwrite.

Args:

- `folder` (`Path`): Destination directory (created if missing).
- `today` (`date | None`): Calendar day for the stem; defaults to local today.
- `extension` (`str`): File suffix including the leading dot. Defaults to `.png`.

Returns:

- `Path`: Absolute path such as `…/2026-08-29_01.png`.

<details>
<summary>Code:</summary>

```python
def next_dated_image_path(
    folder: Path,
    *,
    today: date | None = None,
    extension: str = ".png",
) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    day = (today or datetime.now(UTC).astimezone().date()).isoformat()
    used: set[int] = set()
    for path in folder.iterdir():
        if not path.is_file():
            continue
        match = _DATED_STEM.match(path.stem)
        if match is None or match.group(1) != day:
            continue
        used.add(int(match.group(2)))
    index = 1
    while index in used:
        index += 1
    suffix = extension if extension.startswith(".") else f".{extension}"
    return (folder / f"{day}_{index:02d}{suffix}").resolve()
```

</details>
