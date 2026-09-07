"""Tests for Lucide SVG UI icons."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QMenu

from harrix_swiss_knife import qt_lucide_icon as lucide_mod
from harrix_swiss_knife.qt_lucide_icon import (
    ACCEPT_BUTTON_STYLE,
    CANCEL_BUTTON_STYLE,
    LUCIDE_COLOR_BLUE,
    LUCIDE_COLOR_DARK,
    LUCIDE_COLOR_GREEN,
    LUCIDE_COLOR_ON_FILLED,
    LUCIDE_COLOR_RED,
    add_lucide_action,
    apply_leading_chrome_icons,
    apply_lucide_dialog_buttons,
    create_ai_lucide_icon,
    create_lucide_icon,
    lucide_color_for,
    lucide_name_for_chrome_emoji,
    lucide_svg_path,
    make_lucide_push_button,
    set_action_text_with_lucide_icon,
    style_accept_button,
    style_cancel_button,
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


def _first_opaque_pixel(icon_name: str, *, color: str | None = None) -> QColor:
    lucide_mod._CACHE.clear()
    icon = create_lucide_icon(icon_name, 24, color=color, device_pixel_ratio=1.0)
    pixmap = icon.pixmap(QSize(24, 24), 1.0)
    image = pixmap.toImage()
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = QColor(image.pixelColor(x, y))
            if pixel.alpha() >= 32:
                lucide_mod._CACHE.clear()
                return pixel
    lucide_mod._CACHE.clear()
    msg = f"No opaque pixels in Lucide icon {icon_name!r}"
    raise AssertionError(msg)


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


def test_lucide_color_for_semantic_map() -> None:
    assert lucide_color_for("trash") == LUCIDE_COLOR_RED
    assert lucide_color_for("circle-check") == LUCIDE_COLOR_GREEN
    assert lucide_color_for("sparkles") == LUCIDE_COLOR_BLUE
    assert lucide_color_for("folder") == LUCIDE_COLOR_DARK


def test_create_lucide_icon_uses_semantic_colors(qapp: QApplication) -> None:
    assert qapp is not None
    trash = _first_opaque_pixel("trash")
    check = _first_opaque_pixel("circle-check")
    sparkles = _first_opaque_pixel("sparkles")
    assert trash.red() > trash.green()
    assert check.green() > check.red()
    assert sparkles.blue() > sparkles.red()


def test_create_lucide_icon_explicit_color_overrides_map(qapp: QApplication) -> None:
    assert qapp is not None
    pixel = _first_opaque_pixel("trash", color="#ff00aa")
    assert pixel.red() > 180
    assert pixel.blue() > 120


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


def test_robot_chrome_emoji_maps_to_sparkles() -> None:
    assert lucide_name_for_chrome_emoji("🤖") == "sparkles"
    assert lucide_name_for_chrome_emoji("⋯") == "ellipsis"
    assert lucide_name_for_chrome_emoji("…") == "ellipsis"
    assert lucide_name_for_chrome_emoji("⋮") == "ellipsis-vertical"
    assert lucide_svg_path("sparkles") is not None


def test_create_ai_lucide_icon_uses_brand_blue(qapp: QApplication) -> None:
    assert qapp is not None
    lucide_mod._CACHE.clear()
    icon = create_ai_lucide_icon(24)
    pixmap = icon.pixmap(QSize(24, 24), 1.0)
    image = pixmap.toImage()
    found = False
    for y in range(image.height()):
        for x in range(image.width()):
            pixel = QColor(image.pixelColor(x, y))
            if pixel.alpha() < 32:
                continue
            assert pixel.red() < 80
            assert 100 < pixel.green() < 180
            assert pixel.blue() > 150
            found = True
            break
        if found:
            break
    assert found
    lucide_mod._CACHE.clear()


def test_apply_lucide_dialog_buttons_paints_ok_green_and_cancel_red(qapp: QApplication) -> None:
    assert qapp is not None
    box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok
        | QDialogButtonBox.StandardButton.Apply
        | QDialogButtonBox.StandardButton.Cancel
    )
    apply_button = box.addButton("Apply translations", QDialogButtonBox.ButtonRole.AcceptRole)
    apply_lucide_dialog_buttons(box)
    ok = box.button(QDialogButtonBox.StandardButton.Ok)
    apply = box.button(QDialogButtonBox.StandardButton.Apply)
    cancel = box.button(QDialogButtonBox.StandardButton.Cancel)
    assert ok is not None
    assert apply is not None
    assert cancel is not None
    assert ok.styleSheet() == ACCEPT_BUTTON_STYLE
    assert apply.styleSheet() == ACCEPT_BUTTON_STYLE
    assert apply_button.styleSheet() == ACCEPT_BUTTON_STYLE
    assert cancel.styleSheet() == CANCEL_BUTTON_STYLE


def test_style_accept_button_sets_shared_green(qapp: QApplication) -> None:
    assert qapp is not None
    button = make_lucide_push_button("OK", "circle-check")
    style_accept_button(button)
    assert button.styleSheet() == ACCEPT_BUTTON_STYLE


def test_filled_accept_and_cancel_use_on_filled_white_icons(qapp: QApplication) -> None:
    assert qapp is not None
    lucide_mod._CACHE.clear()
    ok = make_lucide_push_button("OK", "circle-check")
    style_accept_button(ok)
    cancel = make_lucide_push_button("Cancel", "x")
    ok_pixel = None
    cancel_pixel = None
    for button, store in ((ok, "ok"), (cancel, "cancel")):
        pixmap = button.icon().pixmap(QSize(18, 18), 1.0)
        image = pixmap.toImage()
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = QColor(image.pixelColor(x, y))
                if pixel.alpha() < 32:
                    continue
                if store == "ok":
                    ok_pixel = pixel
                else:
                    cancel_pixel = pixel
                break
            if (store == "ok" and ok_pixel is not None) or (store == "cancel" and cancel_pixel is not None):
                break
    assert ok_pixel is not None
    assert cancel_pixel is not None
    on_filled = QColor(LUCIDE_COLOR_ON_FILLED)
    assert abs(ok_pixel.red() - on_filled.red()) < 40
    assert abs(ok_pixel.green() - on_filled.green()) < 40
    assert abs(ok_pixel.blue() - on_filled.blue()) < 40
    assert abs(cancel_pixel.red() - on_filled.red()) < 40
    lucide_mod._CACHE.clear()


def test_make_lucide_push_button_paints_cancel_red(qapp: QApplication) -> None:
    assert qapp is not None
    cancel = make_lucide_push_button("Cancel", "x")
    cancel_screenshot = make_lucide_push_button("Cancel screenshot", "x")
    assert cancel.styleSheet() == CANCEL_BUTTON_STYLE
    assert cancel_screenshot.styleSheet() == CANCEL_BUTTON_STYLE
    style_cancel_button(cancel)
    assert cancel.styleSheet() == CANCEL_BUTTON_STYLE
