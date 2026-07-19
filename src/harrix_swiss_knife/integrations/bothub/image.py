"""BotHub image helpers."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage

_MIME_BY_SUFFIX: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".avif": "image/avif",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}


def image_bytes_and_mime(path: str | Path, *, max_image_side: int | None = None) -> tuple[bytes, str]:
    """Read an image file and return its bytes and MIME type.

    When `max_image_side` is set, downscale large images and return PNG bytes.

    Raises:

    - `ValueError`: If the file extension is not supported or the file is empty.

    """
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


def image_mime_from_suffix(suffix: str) -> str | None:
    """Map a file suffix to MIME type, or `None` if unsupported."""
    return _MIME_BY_SUFFIX.get(suffix.lower())


def _downscale_qimage(qimage: QImage, max_side: int | None) -> QImage:
    """Return image scaled down so neither side exceeds max_side."""
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


def _encode_qimage_png(qimage: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    # PySide6 accepts `str` format at runtime; stubs expect `bytes` for the QIODevice overload.
    if not qimage.save(buffer, "PNG"):  # ty: ignore[no-matching-overload]
        msg = "Failed to encode image"
        raise ValueError(msg)
    payload = buffer.data().data()
    if isinstance(payload, memoryview):
        return payload.tobytes()
    return bytes(payload)
