"""Tests for custom action SVG icons used in the GUI."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife import qt_action_icon as action_icon_mod
from harrix_swiss_knife.actions.apps.icons import OnIcons
from harrix_swiss_knife.menu_list_markdown import generate_markdown_from_menu_structure
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.qt_action_icon import (
    action_svg_path,
    create_action_icon,
    create_menu_icon,
    resolve_ui_icon_spec,
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


def test_on_icons_keeps_emoji_for_docs() -> None:
    assert OnIcons.icon == "🎨"
    assert OnIcons.icon_svg == "object__palette.svg"


def test_on_icons_markdown_uses_emoji_not_svg() -> None:
    lines = generate_markdown_from_menu_structure(get_menu_structure())
    assert "- 🎨 Vector Icons" in lines
    assert not any("object__palette" in line for line in lines)


def test_resolve_ui_icon_spec_prefers_existing_svg() -> None:
    assert resolve_ui_icon_spec(OnIcons) == "object__palette.svg"


def test_resolve_ui_icon_spec_falls_back_to_emoji_when_svg_missing() -> None:
    class _MissingSvg:
        icon = "🎨"
        icon_svg = "not-a-real-action-icon.svg"

    assert resolve_ui_icon_spec(_MissingSvg) == "🎨"


def test_action_svg_path_accepts_palette_and_rejects_unsafe_names() -> None:
    path = action_svg_path("object__palette.svg")
    assert path is not None
    assert path.name == "object__palette.svg"
    assert action_svg_path("object__palette") == path
    assert action_svg_path("../object__palette.svg") is None
    assert action_svg_path("not-a-real-action-icon.svg") is None


def test_create_action_icon_for_on_icons_is_not_empty(qapp: QApplication) -> None:
    assert qapp is not None
    action_icon_mod._CACHE.clear()
    icon = create_action_icon(OnIcons, 24)
    assert not icon.isNull()
    raster = create_menu_icon("object__palette.svg", 24, device_pixel_ratio=1.0)
    pixmap = raster.pixmap(QSize(24, 24), 1.0)
    image = pixmap.toImage()
    found = False
    for y in range(image.height()):
        for x in range(image.width()):
            if QColor(image.pixelColor(x, y)).alpha() >= 32:
                found = True
                break
        if found:
            break
    action_icon_mod._CACHE.clear()
    assert found


def test_create_menu_icon_uses_device_pixel_ratio(qapp: QApplication) -> None:
    assert qapp is not None
    action_icon_mod._CACHE.clear()
    icon = create_menu_icon("object__palette.svg", 20, device_pixel_ratio=2.0)
    pixmap = icon.pixmap(QSize(20, 20), 2.0)
    action_icon_mod._CACHE.clear()
    assert pixmap.devicePixelRatio() == 2.0
    assert pixmap.width() == 40
    assert pixmap.height() == 40
