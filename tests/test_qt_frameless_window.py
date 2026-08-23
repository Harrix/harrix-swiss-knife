"""Tests for frameless window resize hit-testing."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, QSize
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from harrix_swiss_knife.qt_frameless_window import (
    _HTCLIENT,
    _HTRIGHT,
    _HTTOPRIGHT,
    _blocks_frameless_resize,
    frameless_hit_test,
    frameless_local_from_native,
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


def test_frameless_hit_test_keeps_inner_area_as_client() -> None:
    """Points away from the 8 px strip are not resize edges."""
    size = QSize(200, 100)
    assert frameless_hit_test(QPoint(20, 20), size) == _HTCLIENT
    assert frameless_hit_test(QPoint(199, 1), size) == _HTTOPRIGHT
    assert frameless_hit_test(QPoint(199, 50), size) == _HTRIGHT


def test_frameless_local_from_native_uses_device_pixel_ratio() -> None:
    """Native WM_NCHITTEST pixels must be divided by the display scale."""
    assert frameless_local_from_native(
        native_x=1536,
        native_y=24,
        window_left=0,
        window_top=0,
        device_pixel_ratio=1.5,
    ) == QPoint(1024, 16)
    assert frameless_local_from_native(
        native_x=100,
        native_y=20,
        window_left=0,
        window_top=0,
        device_pixel_ratio=1.0,
    ) == QPoint(100, 20)


def test_close_button_blocks_frameless_resize(qapp: QApplication) -> None:
    """A close button in the top-right corner must stay clickable."""
    window = QWidget()
    window.resize(200, 100)
    button = QPushButton("X", window)
    button.setGeometry(164, 8, 28, 28)
    window.show()
    qapp.processEvents()

    assert _blocks_frameless_resize(window, QPoint(178, 20))
    assert not _blocks_frameless_resize(window, QPoint(199, 1))
    window.close()
