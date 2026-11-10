"""Tests for Vector Icons rasterization that keeps SVG aspect ratio."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.vector_render import (
    PREVIEW_BACKGROUND,
    ensure_dark_theme_contrast_plate,
    fitted_content_rect,
    pixmap_content_is_dark,
    render_svg_to_image,
)

_WIDE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="50" viewBox="0 0 200 50">'
    '<rect width="200" height="50" fill="#336699"/>'
    "</svg>"
)
_TALL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="200" viewBox="0 0 50 200">'
    '<rect width="50" height="200" fill="#336699"/>'
    "</svg>"
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _alpha(image: QImage, x: int, y: int) -> int:
    return image.pixelColor(x, y).alpha()


def test_fitted_content_rect_centers_wide_svg(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    path = tmp_path / "wide.svg"
    path.write_text(_WIDE_SVG, encoding="utf-8")
    renderer = QSvgRenderer(str(path))
    assert renderer.isValid()
    rect = fitted_content_rect(renderer, QRectF(0, 0, 100, 100))
    assert rect.width() == pytest.approx(100)
    assert rect.height() == pytest.approx(25)
    assert rect.x() == pytest.approx(0)
    assert rect.y() == pytest.approx(37.5)


def test_fitted_content_rect_centers_tall_svg(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    path = tmp_path / "tall.svg"
    path.write_text(_TALL_SVG, encoding="utf-8")
    renderer = QSvgRenderer(str(path))
    assert renderer.isValid()
    rect = fitted_content_rect(renderer, QRectF(0, 0, 100, 100))
    assert rect.width() == pytest.approx(25)
    assert rect.height() == pytest.approx(100)
    assert rect.x() == pytest.approx(37.5)
    assert rect.y() == pytest.approx(0)


def test_wide_svg_thumbnail_is_not_stretched(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    path = tmp_path / "wide.svg"
    path.write_text(_WIDE_SVG, encoding="utf-8")
    image = render_svg_to_image(path, 100)
    assert image is not None
    assert image.width() == 100
    assert image.height() == 100
    fill = QColor("#336699")
    assert _alpha(image, 50, 0) == 0
    assert _alpha(image, 50, 99) == 0
    center = image.pixelColor(50, 50)
    assert center.alpha() > 200
    assert center.red() == pytest.approx(fill.red(), abs=40)
    assert center.green() == pytest.approx(fill.green(), abs=40)
    assert center.blue() == pytest.approx(fill.blue(), abs=40)


def test_tall_svg_thumbnail_is_not_stretched(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    path = tmp_path / "tall.svg"
    path.write_text(_TALL_SVG, encoding="utf-8")
    image = render_svg_to_image(path, 100)
    assert image is not None
    assert _alpha(image, 0, 50) == 0
    assert _alpha(image, 99, 50) == 0
    assert _alpha(image, 50, 50) > 200


def test_dark_theme_contrast_plate_under_dark_pixmap(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(64, 64, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.fillRect(16, 16, 32, 32, QColor(20, 20, 20))
    painter.end()
    pixmap = QPixmap.fromImage(image)
    assert pixmap_content_is_dark(pixmap)
    plated = ensure_dark_theme_contrast_plate(pixmap)
    corner = plated.toImage().pixelColor(2, 2)
    assert corner.alpha() > 200
    assert corner.red() == pytest.approx(PREVIEW_BACKGROUND.red(), abs=5)
    assert corner.green() == pytest.approx(PREVIEW_BACKGROUND.green(), abs=5)
    assert corner.blue() == pytest.approx(PREVIEW_BACKGROUND.blue(), abs=5)


def test_dark_theme_contrast_plate_skips_bright_pixmap(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(64, 64, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.fillRect(16, 16, 32, 32, QColor(240, 240, 240))
    painter.end()
    pixmap = QPixmap.fromImage(image)
    assert not pixmap_content_is_dark(pixmap)
    assert ensure_dark_theme_contrast_plate(pixmap) is pixmap
