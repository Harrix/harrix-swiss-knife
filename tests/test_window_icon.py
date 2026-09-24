"""Taskbar icons stay rasterized so Windows does not drop a blank button."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QWidget

if TYPE_CHECKING:
    from PySide6.QtGui import QImage

from harrix_swiss_knife.installer.icon_assets import apply_window_icon, make_window_icon
from harrix_swiss_knife.win11_backdrop import ensure_windows_app_user_model_id, try_apply_system_backdrop


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt pixmaps."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_window_icon_has_taskbar_sizes(qapp: QApplication) -> None:
    del qapp
    icon = make_window_icon()
    assert not icon.isNull()
    widths = {size.width() for size in icon.availableSizes()}
    assert 16 in widths
    assert 32 in widths
    assert make_window_icon() is icon


def test_window_icon_fills_the_square(qapp: QApplication) -> None:
    del qapp
    image = make_window_icon().pixmap(QSize(32, 32)).toImage()
    left, top, right, bottom = _opaque_bounds(image)
    assert left <= 1
    assert top <= 1
    assert right >= image.width() - 2
    assert bottom >= image.height() - 2


def test_apply_window_icon_sets_widget_icon(qapp: QApplication) -> None:
    del qapp
    widget = QWidget()
    apply_window_icon(widget)
    assert not widget.windowIcon().isNull()


def test_app_user_model_id_is_safe_to_call() -> None:
    ensure_windows_app_user_model_id()


def _opaque_bounds(image: QImage) -> tuple[int, int, int, int]:
    width = image.width()
    height = image.height()
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for y in range(height):
        for x in range(width):
            if image.pixelColor(x, y).alpha() <= 16:
                continue
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    return min_x, min_y, max_x, max_y


def test_mica_backdrop_does_not_extend_frame_over_the_window() -> None:
    source = inspect.getsource(try_apply_system_backdrop)
    assert "DwmExtendFrameIntoClientArea(" not in source
