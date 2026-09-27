"""Tests for the Windows 11 caption row."""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

import pytest
from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QHoverEvent, QImage, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QSplitter,
    QTabWidget,
    QToolButton,
    QWidget,
)

from harrix_swiss_knife.apps.common.qt_main_window import resolve_window_menu_bar
from harrix_swiss_knife.win11_caption import (
    CAPTION_BUTTON_HEIGHT,
    CAPTION_BUTTON_WIDTH,
    CLOSE_HOVER_COLOR,
    HTCAPTION,
    HTCLIENT,
    HTRIGHT,
    HTTOP,
    CaptionButton,
    _sync_caption_button_hover,
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
    """Menu titles and tab labels sit in the middle of the white caption row."""
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
    window.resize(1200, 240)
    window.show()
    qapp.processEvents()

    background = window.palette().color(QPalette.ColorRole.Window)
    assert background.name(QColor.NameFormat.HexRgb) == "#ffffff"
    assert "#ffffff" in tabs.tabBar().styleSheet()
    _assert_ink_centered(tabs.tabBar().grab(), background)
    _assert_ink_centered(menu.grab(), background)
    assert "#ebebeb" not in tabs.tabBar().styleSheet().lower()
    assert "font-weight: 400" in menu.styleSheet()
    assert "#404654" in menu.styleSheet()
    assert "#404654" in tabs.tabBar().styleSheet()
    title = window.findChild(QLabel, "captionTitleLabel")
    assert title is not None
    assert title.isVisible()
    assert title.text() == "Food tracker - Harrix Swiss Knife"
    assert title.toolTip() == title.text()
    assert "font-weight: 700" in title.styleSheet()
    assert "#2e333d" in title.styleSheet()
    left = tabs.cornerWidget(Qt.Corner.TopLeftCorner)
    right = tabs.cornerWidget(Qt.Corner.TopRightCorner)
    assert left is not None
    assert right is not None
    assert title.parentWidget() is left
    assert menu.parentWidget() is right
    icon = window.findChild(QToolButton, "captionIconButton")
    row = window.findChild(QWidget, "captionButtonRow")
    assert icon is not None
    assert row is not None
    assert icon.parentWidget() is left
    assert title.geometry().left() >= icon.geometry().right() - 1
    assert row.parentWidget() is right
    assert menu.geometry().right() <= row.geometry().left()
    title_right = title.mapTo(tabs, QPoint(title.width(), 0)).x()
    tab_left = tabs.tabBar().mapTo(tabs, QPoint(0, 0)).x()
    assert title_right <= tab_left
    last = tabs.tabBar().tabRect(tabs.tabBar().count() - 1)
    last_right = tabs.tabBar().mapTo(tabs, last.bottomRight()).x()
    assert menu.mapTo(tabs, QPoint(0, 0)).x() >= last_right
    window.close()


def _caption_line_color(image: QImage, x: int) -> str:
    return image.pixelColor(x, CAPTION_BUTTON_HEIGHT - 1).name()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_caption_tab_line_spans_the_window(qapp: QApplication) -> None:
    """The caption rule runs the full width and breaks under the active tab."""
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
    window.resize(1600, 240)
    window.show()
    tabs.setCurrentIndex(1)
    qapp.processEvents()
    image = tabs.grab().toImage()
    tab_bar = tabs.tabBar()
    selected = tab_bar.tabRect(tab_bar.currentIndex())
    selected_x = tab_bar.mapTo(tabs, selected.center()).x()
    assert _caption_line_color(image, selected_x) == "#ffffff"
    last = tab_bar.tabRect(tab_bar.count() - 1)
    after_tabs = tab_bar.mapTo(tabs, last.bottomRight()).x() + 40
    assert _caption_line_color(image, after_tabs) == "#dbdbdb"
    right = tabs.cornerWidget(Qt.Corner.TopRightCorner)
    assert right is not None
    empty_x = (after_tabs + right.mapTo(tabs, QPoint(0, 0)).x()) // 2
    assert _caption_line_color(image, empty_x) == "#dbdbdb"
    edges = window.findChildren(QWidget, "captionEdgeLine")
    assert len(edges) == 2
    for edge in edges:
        assert edge.grab().toImage().pixelColor(2, 0).name() == "#dbdbdb"
    close = window.findChild(CaptionButton, "captionCloseButton")
    assert close is not None
    assert tabs.childAt(close.mapTo(tabs, close.rect().center())) is close
    window.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_menu_only_caption_has_no_base_line(qapp: QApplication) -> None:
    """A caption without tabs does not draw the tab rule."""
    window = QMainWindow()
    window.setWindowTitle("Vector Icons")
    window.menuBar().addMenu("File")
    window.setCentralWidget(QWidget())
    assert install_win11_caption(window)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
    window.resize(800, 240)
    window.show()
    qapp.processEvents()
    host = window.findChild(QWidget, "captionBar")
    assert host is not None
    assert window.findChild(QWidget, "captionBaseLine") is None
    image = host.grab().toImage()
    assert _caption_line_color(image, 8) == "#ffffff"
    window.close()


def _resize_caption(window: QMainWindow, qapp: QApplication, width: int) -> None:
    window.setMinimumWidth(0)
    window.resize(width, 320)
    qapp.processEvents()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_caption_overflow_hides_title_then_menu(qapp: QApplication) -> None:
    """A narrow caption drops the title first, then replaces the menu with a hamburger."""
    window = _window_with_tabs()
    tabs = window.tabWidget
    corner = QWidget()
    layout = QHBoxLayout(corner)
    layout.setContentsMargins(0, 0, 0, 0)
    menu_host = QMenuBar(corner)
    menu_host.addMenu("File")
    menu_host.addMenu("Help")
    layout.addWidget(menu_host)
    tabs.setCornerWidget(corner, Qt.Corner.TopLeftCorner)
    assert install_win11_caption(window)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
    window.show()
    _resize_caption(window, qapp, 1600)
    title = window.findChild(QLabel, "captionTitleLabel")
    menu = resolve_window_menu_bar(window)
    button = window.findChild(QToolButton, "captionMenuButton")
    assert title is not None
    assert menu is not None
    assert button is not None
    assert title.isVisible()
    assert menu.isVisible()
    assert not button.isVisible()

    title_hidden = False
    for width in range(1500, 240, -15):
        _resize_caption(window, qapp, width)
        if not title.isVisible() and menu.isVisible() and not button.isVisible():
            title_hidden = True
            break
    assert title_hidden

    menu_folded = False
    for width in range(window.width(), 180, -15):
        _resize_caption(window, qapp, width)
        if not title.isVisible() and not menu.isVisible() and button.isVisible():
            menu_folded = True
            break
    assert menu_folded
    assert tabs.tabBar().isVisible()

    button.click()
    qapp.processEvents()
    popup = button.findChild(QMenu, "captionOverflowMenu")
    assert popup is not None
    assert [action.text() for action in popup.actions()] == ["File", "Help"]
    assert [action.text() for action in menu.actions()] == ["File", "Help"]

    menu_restored = False
    for width in range(window.width(), 1700, 15):
        _resize_caption(window, qapp, width)
        if menu.isVisible() and not button.isVisible():
            menu_restored = True
            assert not title.isVisible()
            break
    assert menu_restored
    _resize_caption(window, qapp, 1700)
    assert title.isVisible()
    assert menu.isVisible()
    window.close()


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_panels_and_menus_are_white(qapp: QApplication) -> None:
    """Group boxes and popup menus use a white background."""
    previous_style = qapp.style().objectName()
    qapp.setStyle("windows11")
    window = _window_with_tabs()
    try:
        assert install_win11_caption(window)
        sheet = window.styleSheet()
        assert "QGroupBox" in sheet
        assert "QMenu::item:selected { color: #202020;" in sheet
        assert "#ffffff" in sheet

        box = QGroupBox(window)
        box.resize(180, 72)
        box.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        box.show()
        menu = QMenu(window)
        menu.addAction("Refresh")
        menu.resize(180, 48)
        menu.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        menu.show()
        qapp.processEvents()
        assert box.grab().toImage().pixelColor(40, 36).name() == "#ffffff"
        assert menu.grab().toImage().pixelColor(150, 20).name() == "#ffffff"
        assert "QTabWidget QWidget" not in sheet
        assert "QScrollBar" not in sheet
        assert "QHeaderView" not in sheet
        page = window.tabWidget.widget(0)
        page.resize(120, 80)
        page.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        page.show()
        qapp.processEvents()
        assert page.grab().toImage().pixelColor(8, 8).name() == "#ffffff"
    finally:
        window.close()
        qapp.setStyle(previous_style)


def _handle_colors(splitter: QSplitter) -> list[str]:
    handle = splitter.handle(1)
    image = splitter.grab().toImage()
    geometry = handle.geometry()
    if splitter.orientation() == Qt.Orientation.Horizontal:
        y = geometry.center().y()
        return [image.pixelColor(x, y).name() for x in range(geometry.left(), geometry.right() + 1)]
    x = geometry.center().x()
    return [image.pixelColor(x, y).name() for y in range(geometry.top(), geometry.bottom() + 1)]


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_splitter_handle_keeps_width_with_gray_hairline(qapp: QApplication) -> None:
    """Splitter handles stay 5px, with a 1px gray line that fills on hover."""
    previous_style = qapp.style().objectName()
    qapp.setStyle("windows11")
    window = QMainWindow()
    try:
        window.setCentralWidget(QWidget())
        assert install_win11_caption(window)
        window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        window.resize(240, 200)
        window.show()
        hairline = ["#ffffff", "#ffffff", "#c0c0c0", "#ffffff", "#ffffff"]
        filled = ["#c0c0c0", "#c0c0c0", "#c0c0c0", "#c0c0c0", "#c0c0c0"]
        for orientation in (Qt.Orientation.Horizontal, Qt.Orientation.Vertical):
            splitter = QSplitter(orientation, window)
            splitter.addWidget(QWidget())
            splitter.addWidget(QWidget())
            splitter.setSizes([80, 80])
            splitter.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
            splitter.resize(200, 160)
            splitter.show()
            qapp.processEvents()
            handle = splitter.handle(1)
            thickness = handle.width() if orientation == Qt.Orientation.Horizontal else handle.height()
            assert thickness == 5
            assert _handle_colors(splitter) == hairline
            local = QPoint(2, 2)
            qapp.sendEvent(handle, QHoverEvent(QEvent.Type.HoverEnter, local, local, QPoint(-1, -1)))
            qapp.processEvents()
            assert _handle_colors(splitter) == filled
            splitter.hide()
        assert "QScrollBar" not in window.styleSheet()
    finally:
        window.close()
        qapp.setStyle(previous_style)


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_install_caption_on_menu_only_window(qapp: QApplication) -> None:
    """A window without tabs keeps File in the caption row next to the window buttons."""
    previous_style = qapp.style().objectName()
    qapp.setStyle("windows11")
    window = QMainWindow()
    try:
        window.setWindowTitle("Vector Icons")
        file_menu = window.menuBar().addMenu("File")
        help_menu = window.menuBar().addMenu("Help")
        pinned = file_menu.addMenu("Pinned")
        window.setCentralWidget(QWidget())
        assert install_win11_caption(window)
        window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        window.resize(800, 240)
        window.show()
        qapp.processEvents()
        assert not file_menu.isVisible()
        assert not help_menu.isVisible()
        assert not pinned.isVisible()
        pinned.clear()
        pinned.addAction("Folder")
        assert pinned.actions()[0].text() == "Folder"
        assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
        host = window.findChild(QWidget, "captionBar")
        assert host is window.menuWidget()
        assert host is not None
        assert host.height() == CAPTION_BUTTON_HEIGHT
        menu = host.findChild(QMenuBar)
        assert menu is not None
        assert menu.actions()[0].text() == "File"
        assert "font-weight: 400" in menu.styleSheet()
        assert "font-weight: 700" not in menu.styleSheet()
        file_rect = menu.actionGeometry(file_menu.menuAction())
        menu_image = menu.grab().toImage()
        chevron_ink = any(
            _color_distance(menu_image.pixelColor(x, y), QColor("#ffffff")) > _INK_DISTANCE
            for x in range(max(0, file_rect.right() - 12), file_rect.right())
            for y in range(max(0, file_rect.center().y() - 4), file_rect.center().y() + 5)
        )
        assert chevron_ink, "menu title has no down arrow"
        text_mid = _ink_center_y(menu_image, file_rect.adjusted(2, 0, -16, 0))
        arrow_mid = _ink_center_y(menu_image, QRect(file_rect.right() - 14, file_rect.top(), 13, file_rect.height()))
        assert text_mid is not None
        assert arrow_mid is not None
        assert abs(text_mid - arrow_mid) <= 2, f"arrow center {arrow_mid}, text center {text_mid}"
        title = window.findChild(QLabel, "captionTitleLabel")
        assert title is not None
        assert title.isVisible()
        assert title.text() == "Vector Icons - Harrix Swiss Knife"
        assert title.toolTip() == title.text()
        assert "font-weight: 700" in title.styleSheet()
        assert "#2e333d" in title.styleSheet()
        assert title.styleSheet().count("{") == title.styleSheet().count("}")
        assert "#404654" in menu.styleSheet()
        row = window.findChild(QWidget, "captionButtonRow")
        icon = window.findChild(QToolButton, "captionIconButton")
        assert row is not None
        assert icon is not None
        assert icon.geometry().right() <= title.geometry().left()
        assert title.geometry().right() < menu.geometry().left()
        assert menu.geometry().right() <= row.geometry().left()
        help_rect = menu.actionGeometry(help_menu.menuAction())
        assert file_rect.width() > 0
        assert help_rect.left() >= file_rect.right()
        icon = window.findChild(QToolButton, "captionIconButton")
        assert icon is not None
        assert icon.toolTip() == "Vector Icons - Harrix Swiss Knife"
        close = window.findChild(CaptionButton, "captionCloseButton")
        assert close is not None
        assert close.grab().toImage().pixelColor(4, 4).name() == "#ffffff"
    finally:
        window.close()
        qapp.setStyle(previous_style)


@pytest.mark.skipif(sys.platform != "win32", reason="Win11 caption is Windows-only")
def test_caption_button_hover_tracks_pointer(qapp: QApplication) -> None:
    """Caption buttons highlight from the pointer even when Qt hover events are stuck."""
    window = _window_with_tabs()
    assert install_win11_caption(window)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
    window.resize(800, 240)
    window.show()
    qapp.processEvents()
    close = window.findChild(CaptionButton, "captionCloseButton")
    minimize = window.findChild(CaptionButton, "captionMinimizeButton")
    assert close is not None
    assert minimize is not None
    _sync_caption_button_hover(window, close.mapToGlobal(close.rect().center()))
    assert close.underMouse()
    assert not minimize.underMouse()
    _sync_caption_button_hover(window, QPoint(-10_000, -10_000))
    assert not close.underMouse()
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


def _ink_center_y(image: QImage, rect: QRect) -> float | None:
    rows = [
        y
        for y in range(rect.top(), rect.bottom() + 1)
        if any(
            _color_distance(image.pixelColor(x, y), QColor("#ffffff")) > _INK_DISTANCE
            for x in range(max(0, rect.left()), min(image.width(), rect.right() + 1))
        )
    ]
    if not rows:
        return None
    return (rows[0] + rows[-1]) / 2


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
