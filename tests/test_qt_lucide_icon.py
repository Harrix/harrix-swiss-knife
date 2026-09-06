"""Tests for Lucide SVG UI icons."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QMenu

from harrix_swiss_knife import qt_lucide_icon as lucide_mod
from harrix_swiss_knife.qt_lucide_icon import (
    add_lucide_action,
    apply_leading_chrome_icons,
    create_lucide_icon,
    lucide_svg_path,
    make_lucide_push_button,
    set_action_text_with_lucide_icon,
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


def test_lucide_svg_path_accepts_known_ids() -> None:
    path = lucide_svg_path("save")
    assert path is not None
    assert path.name == "save.svg"


def test_lucide_svg_path_rejects_unknown_and_unsafe_ids() -> None:
    assert lucide_svg_path("not-a-real-icon-zzzz") is None
    assert lucide_svg_path("../save") is None
    assert lucide_svg_path("SAVE") is None


def test_create_lucide_icon_unknown_name_is_empty(qapp: QApplication) -> None:
    assert qapp is not None
    icon = create_lucide_icon("not-a-real-icon-zzzz", 16)
    assert icon.isNull()


def test_create_lucide_icon_uses_device_pixel_ratio(qapp: QApplication) -> None:
    assert qapp is not None
    icon = create_lucide_icon("x", 20, device_pixel_ratio=2.0)
    pixmap = icon.pixmap(QSize(20, 20), 2.0)
    assert pixmap.devicePixelRatio() == 2.0
    assert pixmap.width() == 40
    assert pixmap.height() == 40


def test_create_lucide_icon_recolors_from_palette(qapp: QApplication) -> None:
    assert qapp is not None
    previous = qapp.palette()
    palette = QPalette(previous)
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ff00aa"))
    qapp.setPalette(palette)
    try:
        lucide_mod._CACHE.clear()
        icon = create_lucide_icon("x", 24, device_pixel_ratio=1.0)
        pixmap = icon.pixmap(QSize(24, 24), 1.0)
        image = pixmap.toImage()
        found = False
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = QColor(image.pixelColor(x, y))
                if pixel.alpha() < 32:
                    continue
                assert pixel.red() > 180
                assert pixel.blue() > 120
                found = True
                break
            if found:
                break
        assert found
    finally:
        qapp.setPalette(previous)
        lucide_mod._CACHE.clear()


def test_add_lucide_action_keeps_plain_label(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    action = add_lucide_action(menu, "Delete", "trash")
    assert action.text() == "Delete"
    assert not action.icon().isNull()


def test_set_action_text_with_lucide_icon(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    action = menu.addAction("placeholder")
    set_action_text_with_lucide_icon(action, "Show All Transactions", "clipboard-list")
    assert action.text() == "Show All Transactions"
    assert not action.icon().isNull()


def test_make_lucide_push_button(qapp: QApplication) -> None:
    assert qapp is not None
    button = make_lucide_push_button("Save", "save")
    assert button.text() == "Save"
    assert not button.icon().isNull()


def test_apply_leading_chrome_icons_maps_emoji_prefix(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    delete_action = menu.addAction("🗑️ Delete")
    copy_action = menu.addAction("📋 Copy file")
    records_action = menu.addAction("📋 Show All Set Records")
    apply_leading_chrome_icons(menu)
    assert delete_action.text() == "Delete"
    assert copy_action.text() == "Copy file"
    assert records_action.text() == "Show All Set Records"
    assert all(not action.icon().isNull() for action in menu.actions())


def test_set_action_text_with_lucide_icon_strips_leading_emoji(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    action = menu.addAction("placeholder")
    set_action_text_with_lucide_icon(action, "📂 Show database in folder")
    assert action.text() == "Show database in folder"
    assert not action.icon().isNull()
