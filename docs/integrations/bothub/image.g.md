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
- [🔧 Function `_downscale_qimage`](#-function-_downscale_qimage)
- [🔧 Function `_encode_qimage_png`](#-function-_encode_qimage_png)

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

Map a file suffix to MIME type, or None if unsupported.

<details>
<summary>Code:</summary>

```python
def image_mime_from_suffix(suffix: str) -> str | None:
    return _MIME_BY_SUFFIX.get(suffix.lower())
```

</details>

## 🔧 Function `_downscale_qimage`

```python
def _downscale_qimage(qimage: QImage, max_side: int | None) -> QImage
```

Return image scaled down so neither side exceeds max_side.

<details>
<summary>Code:</summary>

```python
def _downscale_qimage(qimage: QImage, max_side: int | None) -> QImage:
    if qimage.isNull() or not max_side or max_side <= 0:
        return qimage
    if qimage.width() <= max_side and qimage.height() <= max_side:
        return qimage
    return qimage.scaled(
        max_side,
        max_side,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
```

</details>

## 🔧 Function `_encode_qimage_png`

```python
def _encode_qimage_png(qimage: QImage) -> bytes
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _encode_qimage_png(qimage: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    # PySide6 accepts ``str`` format at runtime; stubs expect ``bytes`` for the QIODevice overload.
    if not qimage.save(buffer, "PNG"):  # ty: ignore[no-matching-overload]
        msg = "Failed to encode image"
        raise ValueError(msg)
    payload = buffer.data().data()
    if isinstance(payload, memoryview):
        return payload.tobytes()
    return bytes(payload)
```

</details>
