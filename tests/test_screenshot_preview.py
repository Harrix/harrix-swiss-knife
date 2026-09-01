"""Tests for screenshot preview dated paths, canvas, and tabbed window."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QKeyEvent
from PySide6.QtWidgets import QApplication, QTabWidget

from harrix_swiss_knife.apps.common.qt_main_window import compute_app_window_geometry
from harrix_swiss_knife.screenshot import preview_dialog as preview_dialog_module
from harrix_swiss_knife.screenshot.dated_image_path import images_folder, next_dated_image_path
from harrix_swiss_knife.screenshot.preview_canvas import ScreenshotPreviewCanvas
from harrix_swiss_knife.screenshot.preview_dialog import (
    ScreenshotPreviewWindow,
    _is_ctrl_s,
    show_screenshot_preview,
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


@pytest.fixture(autouse=True)
def _reset_preview_singleton() -> Iterator[None]:
    window = preview_dialog_module._preview_holder["window"]
    preview_dialog_module._preview_holder["window"] = None
    if window is not None:
        window.close()
        window.deleteLater()
    QApplication.processEvents()
    yield
    window = preview_dialog_module._preview_holder["window"]
    preview_dialog_module._preview_holder["window"] = None
    if window is not None:
        window.close()
        window.deleteLater()
    QApplication.processEvents()


def test_images_folder_under_project_root() -> None:
    assert images_folder(Path("D:/proj")) == Path("D:/proj/temp/images")


def test_next_dated_image_path_starts_at_01(tmp_path: Path) -> None:
    path = next_dated_image_path(tmp_path, today=date(2026, 8, 29))
    assert path.name == "2026-08-29_01.png"
    assert path.parent == tmp_path.resolve()


def test_next_dated_image_path_skips_existing_indices(tmp_path: Path) -> None:
    (tmp_path / "2026-08-29_01.png").write_bytes(b"x")
    (tmp_path / "2026-08-29_02.jpg").write_bytes(b"x")
    (tmp_path / "2026-08-28_99.png").write_bytes(b"x")
    path = next_dated_image_path(tmp_path, today=date(2026, 8, 29))
    assert path.name == "2026-08-29_03.png"


def test_preview_canvas_zoom_changes_factor(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(200, 100)
    assert canvas.zoom == 1.0
    canvas.zoom_by(2.0, anchor=QPointF(100, 50))
    assert canvas.zoom == pytest.approx(2.0)
    canvas.close()


def test_preview_canvas_does_not_upscale_small_image(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    canvas = ScreenshotPreviewCanvas(image)
    canvas.resize(400, 300)
    rect = canvas._image_rect()
    assert rect.width() == pytest.approx(40.0)
    assert rect.height() == pytest.approx(20.0)
    canvas.close()


def test_is_ctrl_s_accepts_key_s_and_yeru(qapp: QApplication) -> None:  # noqa: ARG001
    event_s = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
    assert _is_ctrl_s(event_s)
    event_yeru = QKeyEvent(QKeyEvent.Type.KeyPress, 0x042B, Qt.KeyboardModifier.ControlModifier)
    assert _is_ctrl_s(event_yeru)
    event_plain = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.NoModifier)
    assert not _is_ctrl_s(event_plain)


def test_preview_window_saves_dated_png_and_updates_title(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.blue)
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.h.dev.get_project_root",
        lambda: tmp_path,
    )
    window = show_screenshot_preview(image)
    assert window.windowTitle() == "Screenshot"
    window._save_to_images()
    saved = tmp_path / "temp" / "images"
    files = list(saved.glob("*.png"))
    assert len(files) == 1
    assert files[0].stem.endswith("_01")
    assert window.windowTitle() == f"Screenshot — {files[0].name}"
    window.close()


def test_preview_window_uses_app_geometry_not_image_size(qapp: QApplication) -> None:
    image = QImage(40, 20, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.red)
    window = show_screenshot_preview(image)
    qapp.processEvents()
    qapp.processEvents()
    screen = window.screen()
    assert screen is not None
    available = screen.availableGeometry()
    target = compute_app_window_geometry(available)
    if target is None:
        assert bool(window.windowState() & Qt.WindowState.WindowMaximized)
    else:
        assert window.width() >= target.width() - 80
        assert window.height() >= target.height() - 80
    window.close()


def test_show_screenshot_preview_adds_tabs(qapp: QApplication) -> None:  # noqa: ARG001
    first = QImage(8, 8, QImage.Format.Format_RGB32)
    first.fill(Qt.GlobalColor.red)
    second = QImage(10, 10, QImage.Format.Format_RGB32)
    second.fill(Qt.GlobalColor.green)
    window = show_screenshot_preview(first)
    show_screenshot_preview(second)
    tabs = window.findChild(QTabWidget)
    assert tabs is not None
    assert tabs.count() == 2
    assert tabs.tabBar().isVisible()
    window.close()


def test_preview_window_title_follows_tab_saved_name(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.h.dev.get_project_root",
        lambda: tmp_path,
    )
    first = QImage(8, 8, QImage.Format.Format_RGB32)
    first.fill(Qt.GlobalColor.red)
    second = QImage(8, 8, QImage.Format.Format_RGB32)
    second.fill(Qt.GlobalColor.blue)
    window = show_screenshot_preview(first)
    window._save_to_images()
    saved_title = window.windowTitle()
    assert saved_title.startswith("Screenshot — ")
    show_screenshot_preview(second)
    assert window.windowTitle() == "Screenshot"
    tabs = window.findChild(QTabWidget)
    assert tabs is not None
    tabs.setCurrentIndex(0)
    assert window.windowTitle() == saved_title
    window.close()


def test_screenshot_preview_dialog_alias() -> None:
    assert ScreenshotPreviewWindow is preview_dialog_module.ScreenshotPreviewDialog
