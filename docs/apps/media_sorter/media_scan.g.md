---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `media_scan.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_image_path`](#-function-is_image_path)
- [🔧 Function `is_media_path`](#-function-is_media_path)
- [🔧 Function `is_video_path`](#-function-is_video_path)
- [🔧 Function `iter_media_files`](#-function-iter_media_files)
- [🔧 Function `list_immediate_subdirs`](#-function-list_immediate_subdirs)
- [🔧 Function `list_media_in_folder`](#-function-list_media_in_folder)

</details>

## 🔧 Function `is_image_path`

```python
def is_image_path(path: str | Path) -> bool
```

Return whether `path` looks like an image file.

<details>
<summary>Code:</summary>

```python
def is_image_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS
```

</details>

## 🔧 Function `is_media_path`

```python
def is_media_path(path: str | Path) -> bool
```

Return whether `path` looks like a supported image or video.

<details>
<summary>Code:</summary>

```python
def is_media_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in MEDIA_EXTENSIONS
```

</details>

## 🔧 Function `is_video_path`

```python
def is_video_path(path: str | Path) -> bool
```

Return whether `path` looks like a video file.

<details>
<summary>Code:</summary>

```python
def is_video_path(path: str | Path) -> bool:
    return Path(path).suffix.lower() in VIDEO_EXTENSIONS
```

</details>

## 🔧 Function `iter_media_files`

```python
def iter_media_files(root: str | Path) -> list[Path]
```

Return sorted media files under `root` (recursive), skipping missing roots.

<details>
<summary>Code:</summary>

```python
def iter_media_files(root: str | Path) -> list[Path]:
    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        return []
    found: list[Path] = []
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in MEDIA_EXTENSIONS:
            continue
        # Skip thumbnail cache folders if present under the tree
        if any(part.startswith(".") for part in path.parts):
            continue
        found.append(path)
    found.sort(key=lambda p: str(p).lower())
    return found
```

</details>

## 🔧 Function `list_immediate_subdirs`

```python
def list_immediate_subdirs(folder: str | Path) -> list[Path]
```

Return sorted immediate child directories of `folder`.

<details>
<summary>Code:</summary>

```python
def list_immediate_subdirs(folder: str | Path) -> list[Path]:
    folder_path = Path(folder).expanduser()
    if not folder_path.is_dir():
        return []
    dirs = [p for p in folder_path.iterdir() if p.is_dir() and not p.name.startswith(".")]
    dirs.sort(key=lambda p: p.name.lower())
    return dirs
```

</details>

## 🔧 Function `list_media_in_folder`

```python
def list_media_in_folder(folder: str | Path) -> list[Path]
```

Return media files in `folder` (optionally recursive).

<details>
<summary>Code:</summary>

```python
def list_media_in_folder(folder: str | Path, *, recursive: bool = False) -> list[Path]:
    folder_path = Path(folder).expanduser()
    if not folder_path.is_dir():
        return []
    if recursive:
        return iter_media_files(folder_path)
    files = [
        p
        for p in folder_path.iterdir()
        if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS and not p.name.startswith(".")
    ]
    files.sort(key=lambda p: p.name.lower())
    return files
```

</details>
