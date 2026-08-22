"""Tests for screenshot capture restore and preview focus."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.screenshot import capture


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _sample_image() -> QImage:
    image = QImage(8, 8, QImage.Format.Format_RGB32)
    image.fill(0)
    return image


def test_capture_region_restores_without_activate_when_preview_opens(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = _sample_image()
    restore_kwargs: list[bool] = []
    brought: list[object] = []

    monkeypatch.setattr(capture, "hide_app_windows", list)
    monkeypatch.setattr(capture, "_wait_ms", lambda _ms: None)
    monkeypatch.setattr(capture, "_capture_loop", lambda **_kwargs: image)
    monkeypatch.setattr(
        capture,
        "restore_app_windows",
        lambda _widgets, *, activate=True: restore_kwargs.append(activate),
    )
    monkeypatch.setattr(capture, "bring_window_to_foreground", lambda dialog, **_kwargs: brought.append(dialog))

    fake_dialog = MagicMock()
    monkeypatch.setattr(capture, "ScreenshotPreviewDialog", lambda _image: fake_dialog)

    result = capture.capture_region(show_preview=True, show_shutter_button=False)

    assert result is image
    assert restore_kwargs == [False]
    fake_dialog.show.assert_called_once()
    assert brought == [fake_dialog]
    fake_dialog.exec.assert_called_once()


def test_capture_region_activates_restored_windows_when_preview_skipped(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = _sample_image()
    restore_kwargs: list[bool] = []

    monkeypatch.setattr(capture, "hide_app_windows", list)
    monkeypatch.setattr(capture, "_wait_ms", lambda _ms: None)
    monkeypatch.setattr(capture, "_capture_loop", lambda **_kwargs: image)
    monkeypatch.setattr(
        capture,
        "restore_app_windows",
        lambda _widgets, *, activate=True: restore_kwargs.append(activate),
    )
    monkeypatch.setattr(capture, "bring_window_to_foreground", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(capture, "ScreenshotPreviewDialog", MagicMock)

    result = capture.capture_region(show_preview=False, show_shutter_button=False)

    assert result is image
    assert restore_kwargs == [True]
