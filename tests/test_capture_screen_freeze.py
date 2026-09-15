"""Tests for long-press screen freeze used by the capture picker."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot import capture
from harrix_swiss_knife.screenshot.capture import (
    clear_pending_screen_freeze,
    prepare_capture_long_press_freeze,
    set_pending_screen_freeze,
    take_pending_screen_freeze,
)
from harrix_swiss_knife.screenshot.dpi import ScreenGrab


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
def _clear_freeze() -> Iterator[None]:
    clear_pending_screen_freeze()
    yield
    clear_pending_screen_freeze()


def _fake_grab() -> tuple[list[ScreenGrab], QRect]:
    pixmap = QPixmap(10, 10)
    pixmap.fill()
    grab = ScreenGrab(geometry=QRect(0, 0, 10, 10), dpr=1.0, pixmap=pixmap)
    return [grab], QRect(0, 0, 10, 10)


def test_take_pending_screen_freeze_is_one_shot(qapp: QApplication) -> None:  # noqa: ARG001
    grabs, geometry = _fake_grab()
    set_pending_screen_freeze(grabs, geometry)
    first = take_pending_screen_freeze()
    assert first is not None
    assert first[0] is not grabs  # stored as a new list copy
    assert first[0][0] is grabs[0]
    assert take_pending_screen_freeze() is None


def test_prepare_capture_long_press_freeze_stores_grabs(qapp: QApplication) -> None:  # noqa: ARG001
    grabs, geometry = _fake_grab()
    with patch(
        "harrix_swiss_knife.screenshot.capture.grab_all_screens",
        return_value=(grabs, geometry),
    ):
        assert prepare_capture_long_press_freeze() is True
    pending = take_pending_screen_freeze()
    assert pending is not None
    assert pending[0][0] is grabs[0]
    assert pending[1] == geometry


def test_prepare_capture_long_press_freeze_fails_without_grabs(qapp: QApplication) -> None:  # noqa: ARG001
    with patch(
        "harrix_swiss_knife.screenshot.capture.grab_all_screens",
        return_value=([], QRect()),
    ):
        assert prepare_capture_long_press_freeze() is False
    assert take_pending_screen_freeze() is None


def test_grabs_for_overlay_pass_uses_pending_once(qapp: QApplication) -> None:  # noqa: ARG001
    frozen, geometry = _fake_grab()
    live, live_geometry = _fake_grab()
    set_pending_screen_freeze(frozen, geometry)
    with patch.object(capture, "grab_all_screens", return_value=(live, live_geometry)) as grab:
        first = capture._grabs_for_overlay_pass(use_pending=True)
        second = capture._grabs_for_overlay_pass(use_pending=False)
    assert first[0][0] is frozen[0]
    assert second[0][0] is live[0]
    grab.assert_called_once()


def test_capture_loop_consumes_pending_freeze_on_first_pass(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frozen, _geometry = _fake_grab()
    live, live_geometry = _fake_grab()
    set_pending_screen_freeze(frozen, _geometry)
    grab_calls: list[str] = []
    overlay_grabs: list[list[ScreenGrab]] = []

    def fake_grab() -> tuple[list[ScreenGrab], QRect]:
        grab_calls.append("live")
        return live, live_geometry

    class FakeOverlay:
        adjust_mode = False
        guides_mode = False
        clipboard_only = True
        ocr_translate = False

        def __init__(
            self,
            *_args: object,
            screen_grabs: list[ScreenGrab] | tuple[ScreenGrab, ...] = (),
            **_kwargs: object,
        ) -> None:
            overlay_grabs.append(list(screen_grabs))
            self.cropped_image = QPixmap(4, 4).toImage()

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(capture, "list_snappable_window_rects", lambda **_kwargs: [])
    monkeypatch.setattr(capture, "grab_all_screens", fake_grab)
    monkeypatch.setattr(capture, "RegionOverlay", FakeOverlay)
    monkeypatch.setattr(capture, "play_screenshot_shutter_sound", lambda: None)
    monkeypatch.setattr(capture, "_copy_image_to_clipboard", lambda _image: None)

    session = capture._HideSession(hide_app=False, show_preview=False)
    image = capture._capture_loop(with_controls=False, session=session)

    assert image is not None
    assert grab_calls == []
    assert take_pending_screen_freeze() is None
    assert len(overlay_grabs) == 1
    assert overlay_grabs[0][0] is frozen[0]


def test_long_press_flow_clears_leftover_freeze_after_cancel(qapp: QApplication) -> None:  # noqa: ARG001
    """Mirror app_startup.run_capture_long_press cleanup when the picker is cancelled."""
    grabs, geometry = _fake_grab()
    with patch(
        "harrix_swiss_knife.screenshot.capture.grab_all_screens",
        return_value=(grabs, geometry),
    ):
        prepare_capture_long_press_freeze()
    try:
        chosen = None
        if chosen:
            pass
    finally:
        clear_pending_screen_freeze()
    assert take_pending_screen_freeze() is None


def test_long_press_flow_keeps_freeze_until_action_runs(qapp: QApplication) -> None:  # noqa: ARG001
    """Freeze must still be pending while the chosen capture action runs."""
    grabs, geometry = _fake_grab()
    with patch(
        "harrix_swiss_knife.screenshot.capture.grab_all_screens",
        return_value=(grabs, geometry),
    ):
        prepare_capture_long_press_freeze()
    seen_during_action: list[bool] = []
    try:
        chosen = "OnScreenshotRegion"
        if chosen:
            seen_during_action.append(take_pending_screen_freeze() is not None)
    finally:
        clear_pending_screen_freeze()
    assert seen_during_action == [True]
    assert take_pending_screen_freeze() is None
