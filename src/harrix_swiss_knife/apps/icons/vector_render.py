"""Rasterize SVG / AI / PDF / EPS previews for the Vector Icons browser."""

from __future__ import annotations

import io
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import pymupdf
from PIL import Image
from pypdf import PdfReader
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath
from PySide6.QtSvg import QSvgRenderer

logger = logging.getLogger(__name__)

PREVIEW_BACKGROUND = QColor(180, 180, 180)
PREVIEW_CORNER_RADIUS_RATIO = 0.12
PREVIEW_ICON_INSET_RATIO = 0.1

_VECTOR_SUFFIXES = frozenset({".ai", ".pdf", ".eps"})
_SVG_SUFFIXES = frozenset({".svg"})


def fitted_content_rect(renderer: QSvgRenderer, bounds: QRectF) -> QRectF:
    """Return a centered rect inside `bounds` that keeps the SVG aspect ratio."""
    view = renderer.viewBoxF()
    if view.width() > 0 and view.height() > 0:
        content_w, content_h = view.width(), view.height()
    else:
        default = renderer.defaultSize()
        content_w, content_h = float(default.width()), float(default.height())
    if content_w <= 0 or content_h <= 0:
        return QRectF(bounds)
    scale = min(bounds.width() / content_w, bounds.height() / content_h)
    draw_w = content_w * scale
    draw_h = content_h * scale
    x = bounds.x() + (bounds.width() - draw_w) / 2
    y = bounds.y() + (bounds.height() - draw_h) / 2
    return QRectF(x, y, draw_w, draw_h)


def render_icon_to_image(path: Path, size: int) -> QImage | None:
    """Rasterize an icon file into a square ARGB image.

    Dispatch:

    - `.svg` → Qt SVG renderer
    - `.ai` / `.pdf` / `.eps` → PyMuPDF, then pypdf `/Thumb`, then Ghostscript

    """
    if not path.is_file() or size <= 0:
        return None
    suffix = path.suffix.casefold()
    if suffix in _SVG_SUFFIXES:
        return render_svg_to_image(path, size)
    if suffix in _VECTOR_SUFFIXES:
        return render_vector_document_to_image(path, size)
    return None


def render_svg_to_image(svg_path: Path, size: int) -> QImage | None:
    """Rasterize an SVG into a square image.

    Non-square SVGs keep their aspect ratio and are centered (letterboxed).
    White variants (`*_white_*`) get a rounded gray backdrop so they stay visible.
    The icon itself is inset so it does not touch the gray tile edges.

    """
    if not svg_path.is_file():
        return None
    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        return None
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    if svg_needs_contrast_background(svg_path):
        _paint_rounded_preview_background(painter, size)
        inset = max(2.0, size * PREVIEW_ICON_INSET_RATIO)
        bounds = QRectF(inset, inset, size - 2 * inset, size - 2 * inset)
    else:
        bounds = QRectF(0, 0, size, size)
    renderer.render(painter, fitted_content_rect(renderer, bounds))
    painter.end()
    return image


def render_vector_document_to_image(path: Path, size: int) -> QImage | None:
    """Render AI/PDF/EPS via PyMuPDF, embedded thumb, or Ghostscript."""
    image = _render_with_pymupdf(path, size)
    if image is not None:
        return image
    image = _render_with_pypdf_thumb(path, size)
    if image is not None:
        return image
    return _render_with_ghostscript(path, size)


def svg_needs_contrast_background(svg_path: Path) -> bool:
    """Return whether the SVG is a white-fill variant that needs a gray tile."""
    return "_white" in svg_path.stem.casefold()


def _fit_image_to_square(source: QImage, size: int) -> QImage:
    if source.isNull():
        return source
    scaled = source.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawImage(x, y, scaled)
    painter.end()
    return image


def _ghostscript_executable() -> str | None:
    for name in ("gswin64c", "gswin32c", "gs"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _paint_rounded_preview_background(painter: QPainter, size: int) -> None:
    """Fill a rounded rectangle used behind white icons."""
    radius = max(4.0, size * PREVIEW_CORNER_RADIUS_RATIO)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), radius, radius)
    painter.fillPath(path, PREVIEW_BACKGROUND)


def _pil_to_qimage(image: Image.Image) -> QImage:
    rgba = image.convert("RGBA")
    data = rgba.tobytes("raw", "RGBA")
    qimage = QImage(data, rgba.width, rgba.height, QImage.Format.Format_RGBA8888)
    return qimage.copy()


def _render_with_ghostscript(path: Path, size: int) -> QImage | None:
    exe = _ghostscript_executable()
    if exe is None:
        return None
    try:
        with tempfile.TemporaryDirectory(prefix="hsk-gs-thumb-") as tmp:
            out = Path(tmp) / "thumb.png"
            command = [
                exe,
                "-dSAFER",
                "-dBATCH",
                "-dNOPAUSE",
                "-dQUIET",
                f"-dDEVICEWIDTHPOINTS={size}",
                f"-dDEVICEHEIGHTPOINTS={size}",
                "-dPDFFitPage",
                "-sDEVICE=pngalpha",
                f"-r{max(72, size)}",
                f"-sOutputFile={out}",
                str(path),
            ]
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if completed.returncode != 0 or not out.is_file():
                logger.debug("Ghostscript failed for %s: %s", path, completed.stderr)
                return None
            image = QImage(str(out))
            if image.isNull():
                return None
            return _fit_image_to_square(image, size)
    except (OSError, subprocess.SubprocessError) as exc:
        logger.debug("Ghostscript error for %s: %s", path, exc)
        return None


def _render_with_pymupdf(path: Path, size: int) -> QImage | None:
    try:
        document = pymupdf.open(path)
    except Exception:
        logger.debug("PyMuPDF could not open %s", path, exc_info=True)
        return None
    try:
        if document.page_count < 1:
            return None
        page = document.load_page(0)
        rect = page.rect
        if rect.width <= 0 or rect.height <= 0:
            return None
        zoom = size / max(rect.width, rect.height)
        matrix = pymupdf.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=True)
        if pixmap.width <= 0 or pixmap.height <= 0:
            return None
        fmt = QImage.Format.Format_RGBA8888 if pixmap.alpha else QImage.Format.Format_RGB888
        image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, fmt)
        if image.isNull():
            return None
        return _fit_image_to_square(image.copy(), size)
    except Exception:
        logger.debug("PyMuPDF render failed for %s", path, exc_info=True)
        return None
    finally:
        document.close()


def _render_with_pypdf_thumb(path: Path, size: int) -> QImage | None:
    try:
        reader = PdfReader(str(path), strict=False)
    except Exception:
        logger.debug("pypdf could not open %s", path, exc_info=True)
        return None
    if not reader.pages:
        return None
    page = reader.pages[0]
    thumb = page.get("/Thumb")
    if thumb is None:
        return None
    try:
        raw = thumb.get_object()
        data = raw.get_data() if hasattr(raw, "get_data") else None
        if not data:
            return None
        pil_image = Image.open(io.BytesIO(data))
        return _fit_image_to_square(_pil_to_qimage(pil_image), size)
    except Exception:
        logger.debug("pypdf /Thumb extract failed for %s", path, exc_info=True)
        return None
