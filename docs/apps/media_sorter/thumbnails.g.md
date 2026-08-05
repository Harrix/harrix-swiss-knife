---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `thumbnails.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `load_media_thumbnail`](#-function-load_media_thumbnail)
- [🔧 Function `media_thumb_cache_dir`](#-function-media_thumb_cache_dir)

</details>

## 🔧 Function `load_media_thumbnail`

```python
def load_media_thumbnail(path: str | Path, size: int = _DEFAULT_THUMB) -> QPixmap | None
```

Load a scaled thumbnail for an image or video path.

<details>
<summary>Code:</summary>

```python
def load_media_thumbnail(path: str | Path, size: int = _DEFAULT_THUMB) -> QPixmap | None:
    file_path = Path(path)
    if not file_path.is_file():
        return None
    pixmap = _load_video_thumbnail(file_path) if is_video_path(file_path) else load_image_pixmap(str(file_path))
    if pixmap is None or pixmap.isNull():
        return None
    return pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
```

</details>

## 🔧 Function `media_thumb_cache_dir`

```python
def media_thumb_cache_dir() -> Path
```

Return cache directory for extracted video thumbnails.

<details>
<summary>Code:</summary>

```python
def media_thumb_cache_dir() -> Path:
    cache = h.dev.get_project_root() / "temp" / "media_sorter_thumbs"
    cache.mkdir(parents=True, exist_ok=True)
    return cache
```

</details>
