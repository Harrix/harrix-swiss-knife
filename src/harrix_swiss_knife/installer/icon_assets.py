"""Load the app icon at full resolution and write a padded multi-size ICO."""

from __future__ import annotations

import os
import struct
import sys
import tempfile
from io import BytesIO
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_PAD_RATIO = 0.14
_ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
_ICO_256 = 256
_ICO_HEADER_SIZE = 6
_ICO_ENTRY_SIZE = 16
_WELCOME_LOGO_PX = 96
_HEADER_LOGO_PX = 48
_PNG_FORMAT = b"PNG"


def asset_candidates(*relative: str) -> list[Path]:
    """Return search paths for a file under `harrix_swiss_knife/assets/`."""
    name = Path(*relative)
    roots = [Path(__file__).resolve().parents[1] / "assets"]
    meipass = getattr(sys, "_MEIPASS", None)
    if isinstance(meipass, str):
        roots.append(Path(meipass) / "harrix_swiss_knife" / "assets")
    return [root / name for root in roots]


def find_app_ico() -> Path | None:
    """Return `app.ico` if it exists."""
    for path in asset_candidates("app.ico"):
        if path.is_file():
            return path
    return None


def find_logo_svg() -> Path | None:
    """Return `logo.svg` if it exists."""
    for path in asset_candidates("logo.svg"):
        if path.is_file():
            return path
    return None


def header_logo_pixmap(size: int = _HEADER_LOGO_PX) -> QPixmap:
    """Return a padded logo pixmap for the wizard header."""
    return welcome_logo_pixmap(size)


def largest_image_from_ico(ico_path: Path) -> QImage:
    """Decode the largest PNG (or any) frame from a multi-size ICO."""
    data = ico_path.read_bytes()
    png = _largest_png_frame(data)
    if png:
        image = QImage.fromData(png, _PNG_FORMAT)
        if not image.isNull():
            return image
    icon = QIcon(str(ico_path))
    sizes = icon.availableSizes()
    if sizes:
        best = max(sizes, key=lambda s: s.width() * s.height())
        pixmap = icon.pixmap(best)
        if not pixmap.isNull():
            return pixmap.toImage()
    image = QImage(str(ico_path))
    if image.isNull():
        msg = f"Could not decode icon: {ico_path}"
        raise RuntimeError(msg)
    return image


def make_window_icon() -> QIcon:
    """Return a QIcon with padded full-resolution pixmaps so Windows does not pick a blurry small frame."""
    source = source_logo_image()
    if source.isNull():
        ico = find_app_ico()
        return QIcon(str(ico)) if ico is not None else QIcon()
    icon = QIcon()
    for size in _ICON_SIZES:
        icon.addPixmap(QPixmap.fromImage(padded_image(source, size)))
    return icon


def padded_image(source: QImage, size: int, *, pad_ratio: float = _PAD_RATIO) -> QImage:
    """Scale `source` into a square canvas with transparent margins."""
    out = QImage(size, size, QImage.Format.Format_ARGB32)
    out.fill(Qt.GlobalColor.transparent)
    inner = max(1, int(size * (1 - 2 * pad_ratio)))
    scaled = source.scaled(
        inner,
        inner,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(x, y, scaled)
    painter.end()
    return out


def source_logo_image() -> QImage:
    """Best available logo: SVG if present, else the largest ICO frame."""
    svg = find_logo_svg()
    if svg is not None:
        image = _render_svg(svg, _ICO_256)
        if image is not None and not image.isNull():
            return image
    ico = find_app_ico()
    if ico is None:
        return QImage()
    return largest_image_from_ico(ico)


def welcome_logo_pixmap(size: int = _WELCOME_LOGO_PX) -> QPixmap:
    """Return a padded logo pixmap for the welcome page."""
    source = source_logo_image()
    if source.isNull():
        return QPixmap()
    return QPixmap.fromImage(padded_image(source, size))


def write_padded_ico(dest: Path) -> Path:
    """Write a multi-size ICO with padding, generated from the largest source frame."""
    source = source_logo_image()
    if source.isNull():
        ico = find_app_ico()
        if ico is None:
            msg = "No app.ico or logo.svg to build installer icon"
            raise FileNotFoundError(msg)
        dest.write_bytes(ico.read_bytes())
        return dest
    images = [padded_image(source, size) for size in _ICON_SIZES]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(_ico_from_png_images(images))
    return dest


def _ico_from_png_images(images: list[QImage]) -> bytes:
    entries: list[tuple[int, int, bytes]] = []
    for image in images:
        png = _qimage_png_bytes(image)
        entries.append((image.width(), image.height(), png))
    count = len(entries)
    offset = _ICO_HEADER_SIZE + _ICO_ENTRY_SIZE * count
    out = BytesIO()
    out.write(struct.pack("<HHH", 0, 1, count))
    data_blobs = []
    for width, height, png in entries:
        w = 0 if width >= _ICO_256 else width
        h = 0 if height >= _ICO_256 else height
        out.write(struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), offset))
        data_blobs.append(png)
        offset += len(png)
    for blob in data_blobs:
        out.write(blob)
    return out.getvalue()


def _largest_png_frame(data: bytes) -> bytes | None:
    if len(data) < _ICO_HEADER_SIZE:
        return None
    _reserved, itype, count = struct.unpack_from("<HHH", data, 0)
    if itype != 1 or count <= 0:
        return None
    best: bytes | None = None
    best_area = -1
    pos = _ICO_HEADER_SIZE
    for _ in range(count):
        if pos + _ICO_ENTRY_SIZE > len(data):
            break
        width, height, _colors, _res, _planes, _bpp, size, offset = struct.unpack_from("<BBBBHHII", data, pos)
        pos += _ICO_ENTRY_SIZE
        if offset < 0 or size <= 0 or offset + size > len(data):
            continue
        chunk = data[offset : offset + size]
        if not chunk.startswith(_PNG_MAGIC):
            continue
        area = (_ICO_256 if width == 0 else width) * (_ICO_256 if height == 0 else height)
        if area > best_area:
            best_area = area
            best = chunk
    return best


def _qimage_png_bytes(image: QImage) -> bytes:
    handle, raw_path = tempfile.mkstemp(suffix=".png")
    os.close(handle)
    path = Path(raw_path)
    try:
        if not image.save(str(path)):
            msg = "Could not encode PNG icon frame"
            raise RuntimeError(msg)
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)


def _render_svg(path: Path, size: int) -> QImage | None:
    try:
        from PySide6.QtSvg import QSvgRenderer  # noqa: PLC0415
    except ImportError:
        return None
    renderer = QSvgRenderer(str(path))
    if not renderer.isValid():
        return None
    image = QImage(QSize(size, size), QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image
