"""Tests for the Windows 11 caption row."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

import pytest
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QMenuBar, QTabWidget, QToolButton, QWidget

from harrix_swiss_knife.win11_caption import (
    CAPTION_BUTTON_HEIGHT,
    CAPTION_BUTTON_WIDTH,
    CLOSE_HOVER_COLOR,
    HTCAPTION,
    HTCLIENT,
    HTRIGHT,
    HTTOP,
    CaptionButton,
    caption_hit_test,
    install_win11_caption,
    write_nccalcsize_client_rect,
)

_INK_DISTANCE = 80
_INK_CENTER_SLACK = 3


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_caption_hit_test_drags_empty_space_and_keeps_buttons() -> None:
    """Empty caption space drags; buttons stay clickable; edges resize."""
    size = QSize(800, 600)
    caption = QRect(0, 0, 800, CAPTION_BUTTON_HEIGHT)
    buttons = [
        QRect(800 - CAPTION_BUTTON_WIDTH * 3, 0, CAPTION_BUTTON_WIDTH, CAPTION_BUTTON_HEIGHT),
        QRect(800 - CAPTION_BUTTON_WIDTH * 2, 0, CAPTION_BUTTON_WIDTH, CAPTION_BUTTON_HEIGHT),
        QRect(800 - CAPTION_BUTTON_WIDTH, 0, CAPTION_BUTTON_WIDTH, CAPTION_BUTTON_HEIGHT),
    ]
    assert caption_hit_test(QPoint(200, 16), size, caption=caption, interactive=buttons, maximized=False) == HTCAPTION
    assert caption_hit_test(QPoint(790, 16), size, caption=caption, interactive=buttons, maximized=False) == HTCLIENT
    assert caption_hit_test(QPoint(790, 1), size, caption=caption, interactive=buttons, maximized=False) == HTCLIENT
    assert caption_hit_test(QPoint(200, 1), size, caption=caption, interactive=buttons, maximized=False) == HTTOP
    assert caption_hit_test(QPoint(799, 100), size, caption=caption, interactive=buttons, maximized=False) == HTRIGHT


def test_caption_hit_test_maximized_does_not_resize() -> None:
    """A maximized window drags from the caption and does not resize from the edges."""
    size = QSize(800, 600)
    caption = QRect(0, 0, 800, CAPTION_BUTTON_HEIGHT)
    assert caption_hit_test(QPoint(200, 1), size, caption=caption, interactive=[], maximized=True) == HTCAPTION
    assert caption_hit_test(QPoint(799, 100), size, caption=caption, interactive=[], maximized=True) == HTCLIENT


def test_write_nccalcsize_client_rect_updates_first_rect() -> None:
    """The maximized client rect is written into the first NCCALCSIZE rectangle."""

    class Params(ctypes.Structure):
        _fields_ = (
            ("rgrc", wintypes.RECT * 3),
            ("lppos", ctypes.c_void_p),
        )

    params = Params()
    write_nccalcsize_client_rect(ctypes.addressof(params), 10, 20, 30, 40)
    assert params.rgrc[0].left == 10
    assert params.rgrc[0].top == 20
    assert params.rgrc[0].right == 30
    assert params.rgrc[0].bottom == 40


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_caption_buttons_match_windows_11_size(qapp: QApplication) -> None:  # noqa: ARG001
    """Three 46 by 32 buttons sit on the right, and the app icon stays on the left."""
    window = _window_with_tabs()
    assert install_win11_caption(window)
    assert window.windowTitle() == "Food tracker"
    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint

    row = window.tabWidget.cornerWidget(Qt.Corner.TopRightCorner)
    assert row is not None
    buttons = row.findChildren(CaptionButton)
    assert len(buttons) == 3
    assert {button.width() for button in buttons} == {CAPTION_BUTTON_WIDTH}
    assert {button.height() for button in buttons} == {CAPTION_BUTTON_HEIGHT}
    assert {button.objectName() for button in buttons} == {
        "captionMinimizeButton",
        "captionMaximizeButton",
        "captionCloseButton",
    }
    icon = window.findChild(QToolButton, "captionIconButton")
    assert icon is not None
    assert icon.toolTip() == "Food tracker - Harrix Swiss Knife"
    assert "border: none" in window.tabWidget.styleSheet()
    assert window.tabWidget.tabBar().drawBase() is False
    close = window.findChild(CaptionButton, "captionCloseButton")
    assert close is not None
    assert close.hover_background().name(QColor.NameFormat.HexRgb) == CLOSE_HOVER_COLOR.name(QColor.NameFormat.HexRgb)
    window.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_install_accepts_ui_central_widget_attribute(qapp: QApplication) -> None:  # noqa: ARG001
    """Generated UI assigns `centralWidget` to a widget and hides the method."""
    window = QMainWindow()
    central = QWidget()
    layout = QHBoxLayout(central)
    tabs = QTabWidget()
    tabs.setObjectName("tabWidget")
    tabs.addTab(QWidget(), "Food")
    layout.addWidget(tabs)
    window.setCentralWidget(central)
    # Generated UI assigns this name onto the instance and hides the method.
    setattr(window, "centralWidget", central)  # noqa: B010
    window.tabWidget = tabs  # type: ignore[attr-defined]
    assert install_win11_caption(window)
    margins = central.layout()
    assert margins is not None
    assert margins.contentsMargins().left() == 0
    assert margins.contentsMargins().top() == 0
    window.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_caption_labels_are_centered_on_gray_tabs(qapp: QApplication) -> None:
    """Menu titles and tab labels sit in the middle of the gray caption row."""
    window = _window_with_tabs()
    tabs = window.tabWidget
    corner = QWidget()
    layout = QHBoxLayout(corner)
    layout.setContentsMargins(0, 0, 0, 0)
    menu = QMenuBar(corner)
    menu.addMenu("File")
    layout.addWidget(menu)
    tabs.setCornerWidget(corner, Qt.Corner.TopLeftCorner)
    assert install_win11_caption(window)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
    window.resize(800, 240)
    window.show()
    qapp.processEvents()

    background = window.palette().color(QPalette.ColorRole.Window)
    assert background.name(QColor.NameFormat.HexRgb) in tabs.tabBar().styleSheet()
    _assert_ink_centered(tabs.tabBar().grab(), background)
    _assert_ink_centered(menu.grab(), background)
    window.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_maximize_button_swaps_to_restore_glyph(qapp: QApplication) -> None:
    """Maximized windows show the overlapping-squares glyph."""
    window = _window_with_tabs()
    install_win11_caption(window)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
    window.show()
    qapp.processEvents()
    button = window.findChild(CaptionButton, "captionMaximizeButton")
    assert button is not None
    assert button.glyph_name() == "maximize"
    window.showMaximized()
    qapp.processEvents()
    assert button.glyph_name() == "square_multiple"
    window.close()


def _assert_ink_centered(pixmap: QPixmap, background: QColor) -> None:
    image = pixmap.toImage()
    ink_rows = [
        y
        for y in range(image.height())
        if any(_color_distance(image.pixelColor(x, y), background) > _INK_DISTANCE for x in range(image.width()))
    ]
    band = _longest_ink_run(ink_rows)
    assert band, "caption text was not painted"
    center = (band[0] + band[-1]) / 2
    mid = image.height() / 2
    assert abs(center - mid) <= _INK_CENTER_SLACK, f"ink center {center}, bar mid {mid}"


def _longest_ink_run(rows: list[int]) -> list[int]:
    best: list[int] = []
    current: list[int] = []
    for y in rows:
        if current and y != current[-1] + 1:
            if len(current) > len(best):
                best = current
            current = []
        current.append(y)
    if len(current) > len(best):
        best = current
    return best


def _color_distance(left: QColor, right: QColor) -> int:
    return abs(left.red() - right.red()) + abs(left.green() - right.green()) + abs(left.blue() - right.blue())


def _window_with_tabs() -> QMainWindow:
    window = QMainWindow()
    tabs = QTabWidget()
    tabs.setObjectName("tabWidget")
    tabs.addTab(QWidget(), "Food")
    tabs.addTab(QWidget(), "Stats")
    window.setCentralWidget(tabs)
    window.tabWidget = tabs  # type: ignore[attr-defined]
    window.setWindowTitle("Food tracker")
    return window
