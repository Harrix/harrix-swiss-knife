"""Tests for screenshot preview dated paths and canvas helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QImage, QKeyEvent
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.screenshot.dated_image_path import images_folder, next_dated_image_path
from harrix_swiss_knife.screenshot.preview_canvas import ScreenshotPreviewCanvas
from harrix_swiss_knife.screenshot.preview_dialog import ScreenshotPreviewDialog, _is_ctrl_s


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


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


def test_is_ctrl_s_accepts_key_s_and_yeru(qapp: QApplication) -> None:  # noqa: ARG001
    event_s = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
    assert _is_ctrl_s(event_s)
    event_yeru = QKeyEvent(QKeyEvent.Type.KeyPress, 0x042B, Qt.KeyboardModifier.ControlModifier)
    assert _is_ctrl_s(event_yeru)
    event_plain = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_S, Qt.KeyboardModifier.NoModifier)
    assert not _is_ctrl_s(event_plain)


def test_preview_dialog_saves_dated_png(
    qapp: QApplication,  # noqa: ARG001
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(Qt.GlobalColor.blue)
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.apply_app_window_size_and_position",
        lambda _widget: None,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.screenshot.preview_dialog.h.dev.get_project_root",
        lambda: tmp_path,
    )
    dialog = ScreenshotPreviewDialog(image)
    dialog._save_to_images()
    saved = tmp_path / "temp" / "images"
    files = list(saved.glob("*.png"))
    assert len(files) == 1
    assert files[0].stem.endswith("_01")
    dialog.close()
    dialog.deleteLater()
    QApplication.processEvents()
