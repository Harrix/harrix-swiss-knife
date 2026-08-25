"""Tests for screenshot capture restore and preview focus."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.images.screenshot_region_keep_windows import OnScreenshotRegionKeepWindows
from harrix_swiss_knife.screenshot import capture

_EXAMPLE_CONFIG = Path(__file__).resolve().parents[1] / "config" / "config.example.json"


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


def test_capture_region_keeps_app_windows_visible(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = _sample_image()
    hide_calls: list[int] = []
    restore_calls: list[int] = []

    monkeypatch.setattr(capture, "hide_app_windows", lambda: hide_calls.append(1) or [])
    monkeypatch.setattr(capture, "_wait_ms", lambda _ms: None)
    monkeypatch.setattr(capture, "_capture_loop", lambda **_kwargs: image)
    monkeypatch.setattr(capture, "restore_app_windows", lambda *_args, **_kwargs: restore_calls.append(1))
    monkeypatch.setattr(capture, "bring_window_to_foreground", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(capture, "ScreenshotPreviewDialog", MagicMock)

    result = capture.capture_region(show_preview=False, show_shutter_button=False, hide_app=False)

    assert result is image
    assert hide_calls == []
    assert restore_calls == []


def test_example_config_binds_keep_windows_screenshot() -> None:
    data = json.loads(_EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    matching = [entry for entry in data["hotkeys"] if entry.get("action") == "OnScreenshotRegionKeepWindows"]
    assert matching
    assert "Ctrl+Shift+F4" in matching[0]["hotkeys"]
    assert OnScreenshotRegionKeepWindows.title == "Screenshot region (keep Windows)"
    assert OnScreenshotRegionKeepWindows.quick_launcher is True
