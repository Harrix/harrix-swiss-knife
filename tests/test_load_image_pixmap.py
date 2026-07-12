"""Tests for load_image_pixmap AVIF fallback."""

from __future__ import annotations

from pathlib import Path

import pillow_avif  # noqa: F401
import pytest
from PIL import Image
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.avif_manager import load_image_pixmap


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _write_test_avif(path: Path) -> None:
    Image.new("RGB", (64, 48), (120, 80, 40)).save(path, format="AVIF")


def _write_test_png(path: Path) -> None:
    Image.new("RGB", (64, 48), (120, 80, 40)).save(path, format="PNG")


def test_load_image_pixmap_avif(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    avif_path = tmp_path / "photo.avif"
    _write_test_avif(avif_path)

    pixmap = load_image_pixmap(avif_path)

    assert pixmap is not None
    assert not pixmap.isNull()
    assert pixmap.width() == 64
    assert pixmap.height() == 48


def test_load_image_pixmap_png(tmp_path: Path, qapp: QApplication) -> None:  # noqa: ARG001
    png_path = tmp_path / "photo.png"
    _write_test_png(png_path)

    pixmap = load_image_pixmap(png_path)

    assert pixmap is not None
    assert not pixmap.isNull()
    assert pixmap.width() == 64
    assert pixmap.height() == 48
