---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `image_bytes_and_mime`](#-function-image_bytes_and_mime)
- [🔧 Function `image_mime_from_suffix`](#-function-image_mime_from_suffix)

</details>

## 🔧 Function `image_bytes_and_mime`

```python
def image_bytes_and_mime(path: str | Path) -> tuple[bytes, str]
```

Read an image file and return its bytes and MIME type.

When `max_image_side` is set, downscale large images and return PNG bytes.

Raises:

- `ValueError`: If the file extension is not supported or the file is empty.

<details>
<summary>Code:</summary>

```python
def image_bytes_and_mime(path: str | Path, *, max_image_side: int | None = None) -> tuple[bytes, str]:
    file_path = Path(path)
    mime_type = image_mime_from_suffix(file_path.suffix)
    if mime_type is None:
        msg = f"Unsupported image format: {file_path.suffix}"
        raise ValueError(msg)

    raw = file_path.read_bytes()
    if not raw:
        msg = f"Image is empty: {file_path.name}"
        raise ValueError(msg)

    if not max_image_side or max_image_side <= 0:
        return raw, mime_type

    qimage = QImage(str(file_path))
    if qimage.isNull():
        return raw, mime_type

    scaled = _downscale_qimage(qimage, max_image_side)
    if scaled.width() == qimage.width() and scaled.height() == qimage.height():
        return raw, mime_type

    return _encode_qimage_png(scaled), "image/png"
```

</details>

## 🔧 Function `image_mime_from_suffix`

```python
def image_mime_from_suffix(suffix: str) -> str | None
```

Map a file suffix to MIME type, or `None` if unsupported.

<details>
<summary>Code:</summary>

```python
def image_mime_from_suffix(suffix: str) -> str | None:
    return _MIME_BY_SUFFIX.get(suffix.lower())
```

</details>
