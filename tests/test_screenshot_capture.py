"""Tests for screenshot capture restore and preview focus."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.actions.images.screenshot_region_clipboard import OnScreenshotRegionClipboard
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

    fake_window = MagicMock()
    monkeypatch.setattr(capture, "show_screenshot_preview", lambda _image: fake_window)

    result = capture.capture_region(show_preview=True, show_shutter_button=False)

    assert result is image
    assert restore_kwargs == [False]
    assert brought == [fake_window]


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
    monkeypatch.setattr(capture, "show_screenshot_preview", MagicMock)

    result = capture.capture_region(show_preview=False, show_shutter_button=False)

    assert result is image
    assert restore_kwargs == [True]


def test_hide_session_toggles_keep_windows(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hides: list[int] = []
    restores: list[bool] = []

    monkeypatch.setattr(capture, "hide_app_windows", lambda: hides.append(1) or ["hidden"])
    monkeypatch.setattr(
        capture,
        "restore_app_windows",
        lambda _widgets, *, activate=True: restores.append(activate),
    )
    monkeypatch.setattr(capture, "_wait_ms", lambda _ms: None)

    session = capture._HideSession(hide_app=True, hidden=["hidden"])
    session.apply_keep_windows(keep=True)
    assert session.hide_app is False
    assert session.hidden == []
    assert restores == [False]

    session.apply_keep_windows(keep=False)
    assert session.hide_app is True
    assert hides == [1]
    assert session.hidden == ["hidden"]


def test_capture_region_keeps_windows_when_modal_is_visible(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = _sample_image()
    hide_calls: list[int] = []

    dialog = QDialog()
    dialog.setModal(True)
    dialog.show()
    QApplication.processEvents()

    monkeypatch.setattr(capture, "hide_app_windows", lambda: hide_calls.append(1) or [])
    monkeypatch.setattr(capture, "_wait_ms", lambda _ms: None)
    monkeypatch.setattr(capture, "_capture_loop", lambda **_kwargs: image)
    monkeypatch.setattr(capture, "restore_app_windows", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(capture, "bring_window_to_foreground", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(capture, "show_screenshot_preview", MagicMock)

    try:
        result = capture.capture_region(show_preview=False, show_shutter_button=False)
        assert result is image
        assert hide_calls == []
    finally:
        dialog.close()


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
    monkeypatch.setattr(capture, "show_screenshot_preview", MagicMock)

    result = capture.capture_region(show_preview=False, show_shutter_button=False, hide_app=False)

    assert result is image
    assert hide_calls == []
    assert restore_calls == []


def test_example_config_does_not_bind_removed_keep_windows_actions() -> None:
    data = json.loads(_EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    actions = {entry.get("action") for entry in data["hotkeys"]}
    assert "OnScreenshotRegionKeepWindows" not in actions
    assert "OnScreenshotRegionClipboardKeepWindows" not in actions


def test_example_config_binds_clipboard_screenshot_hotkeys() -> None:
    data = json.loads(_EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    by_action = {entry["action"]: entry["hotkeys"] for entry in data["hotkeys"]}
    assert "Ctrl+Shift+5" in by_action["OnScreenshotRegionClipboard"]
    assert OnScreenshotRegionClipboard.quick_launcher is True


def test_clipboard_action_skips_preview(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: ARG001
    image = _sample_image()
    calls: list[dict[str, object]] = []

    def fake_capture_region(**kwargs: object) -> QImage:
        calls.append(kwargs)
        return image

    monkeypatch.setattr(
        "harrix_swiss_knife.actions.images.screenshot_region_clipboard.capture_region",
        fake_capture_region,
    )

    def _silent_toast(self: object, message: str = "", duration: int = 2000) -> None:  # noqa: ARG001
        return None

    monkeypatch.setattr(OnScreenshotRegionClipboard, "show_toast", _silent_toast)
    OnScreenshotRegionClipboard()()
    assert calls == [
        {"show_preview": False, "show_shutter_button": True},
    ]
