"""Tests for Vector Icons lightbox preview cache and async loading."""

from __future__ import annotations

import time
from collections.abc import Iterator
from pathlib import Path

import pymupdf
import pytest
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons import lightbox as lightbox_module
from harrix_swiss_knife.apps.icons.lightbox import IconLightboxDialog
from harrix_swiss_knife.apps.icons.lightbox_cache import (
    PREVIEW_RENDER_SIZE,
    LightboxImageCache,
    lightbox_image_cache,
)


def _write_pdf(path: Path) -> None:
    document = pymupdf.open()
    try:
        page = document.new_page(width=100, height=100)
        page.draw_rect(page.rect, color=(0, 0, 0), fill=(0, 0, 0))
        document.save(path)
    finally:
        document.close()


def _write_svg(path: Path) -> None:
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">'
        '<rect width="24" height="24" fill="black"/></svg>\n',
        encoding="utf-8",
    )


def _wait_for_preview(dialog: IconLightboxDialog, qapp: QApplication, *, timeout_ms: int = 5000) -> None:
    elapsed = 0
    while not dialog.canvas.has_preview() and elapsed < timeout_ms:
        qapp.processEvents()
        QTest.qWait(20)
        elapsed += 20
    assert dialog.canvas.has_preview()


@pytest.fixture(autouse=True)
def _clear_lightbox_cache() -> Iterator[None]:
    lightbox_image_cache().clear()
    yield
    lightbox_image_cache().clear()


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_lightbox_image_cache_get_put_and_mtime_invalidation(tmp_path: Path) -> None:
    svg = tmp_path / "icon.svg"
    _write_svg(svg)
    cache = LightboxImageCache(max_entries=2)
    image = QImage(16, 16, QImage.Format.Format_ARGB32)
    image.fill(1)
    cache.put(svg, PREVIEW_RENDER_SIZE, image)
    assert cache.get(svg, PREVIEW_RENDER_SIZE) is image
    assert cache.size == 1

    svg.write_text(svg.read_text(encoding="utf-8") + "<!-- changed -->\n", encoding="utf-8")
    assert cache.get(svg, PREVIEW_RENDER_SIZE) is None


def test_lightbox_image_cache_evicts_oldest(tmp_path: Path) -> None:
    cache = LightboxImageCache(max_entries=2)
    paths = []
    for index in range(3):
        path = tmp_path / f"icon{index}.svg"
        _write_svg(path)
        paths.append(path)
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(index + 1)
        cache.put(path, PREVIEW_RENDER_SIZE, image)
    assert cache.get(paths[0], PREVIEW_RENDER_SIZE) is None
    assert cache.get(paths[1], PREVIEW_RENDER_SIZE) is not None
    assert cache.get(paths[2], PREVIEW_RENDER_SIZE) is not None


def test_icon_lightbox_svg_uses_live_renderer_without_raster(
    tmp_path: Path,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    svg = tmp_path / "icon.svg"
    _write_svg(svg)
    calls: list[Path] = []

    def counting_render(path: Path, size: int) -> QImage | None:
        calls.append(path)
        return QImage(size, size, QImage.Format.Format_ARGB32)

    monkeypatch.setattr(lightbox_module, "render_icon_to_image", counting_render)

    dialog = IconLightboxDialog([svg])
    qapp.processEvents()
    assert dialog.canvas.has_preview()
    assert dialog.canvas._svg_renderer is not None
    assert dialog.canvas._svg_renderer.isValid()
    assert dialog.canvas._image is None
    assert calls == []

    dialog.canvas.zoom_by(4.0)
    qapp.processEvents()
    assert dialog.canvas.zoom == 4.0
    assert calls == []
    dialog.close()


def test_icon_lightbox_reuses_cached_raster_preview(
    tmp_path: Path,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf = tmp_path / "icon.pdf"
    _write_pdf(pdf)
    calls: list[Path] = []
    original = lightbox_module.render_icon_to_image

    def counting_render(path: Path, size: int) -> QImage | None:
        calls.append(path)
        return original(path, size)

    monkeypatch.setattr(lightbox_module, "render_icon_to_image", counting_render)

    first = IconLightboxDialog([pdf])
    _wait_for_preview(first, qapp)
    assert len(calls) == 1
    first.close()
    qapp.processEvents()

    second = IconLightboxDialog([pdf])
    assert second.canvas.has_preview()
    assert second.canvas._image is not None
    assert len(calls) == 1
    second.close()


def test_icon_lightbox_shows_toast_after_one_second(
    tmp_path: Path,
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf = tmp_path / "slow.pdf"
    _write_pdf(pdf)
    original = lightbox_module.render_icon_to_image

    def slow_render(path: Path, size: int) -> QImage | None:
        time.sleep(1.2)
        return original(path, size)

    monkeypatch.setattr(lightbox_module, "render_icon_to_image", slow_render)
    monkeypatch.setattr(lightbox_module, "_LOAD_TOAST_DELAY_MS", 200)

    dialog = IconLightboxDialog([pdf])
    qapp.processEvents()
    assert dialog._load_toast is not None
    assert not dialog._load_toast.isVisible()

    QTest.qWait(250)
    qapp.processEvents()
    assert dialog._load_toast is not None
    assert dialog._load_toast.isVisible()

    _wait_for_preview(dialog, qapp, timeout_ms=5000)
    assert dialog._load_toast is None
    dialog.close()
