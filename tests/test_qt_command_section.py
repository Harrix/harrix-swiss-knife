"""Tests for command-section font helpers."""

from __future__ import annotations

from PySide6.QtGui import QFont, QPalette
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.qt_command_section import (
    COMMAND_SECTION_BORDER_COLOR,
    COMMAND_SECTION_DIVIDER_OBJECT_NAME,
    create_command_section,
    create_command_section_divider,
    grow_qfont,
)


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_grow_qfont_increments_point_size() -> None:
    """Point-sized fonts grow with setPointSize."""
    font = QFont()
    font.setPointSize(10)
    grow_qfont(font)
    assert font.pointSize() == 11


def test_grow_qfont_increments_pixel_size_without_set_point_size() -> None:
    """Pixel-sized fonts must not call setPointSize(-1)."""
    font = QFont()
    font.setPixelSize(16)
    assert font.pointSize() <= 0
    grow_qfont(font)
    assert font.pixelSize() == 17
    assert font.pointSize() <= 0


def test_create_command_section_title_is_bold() -> None:
    """Section titles stay bold after the safe font bump."""
    assert _qapp() is not None
    _frame, label, _layout = create_command_section(title="Food")
    assert label is not None
    assert label.text() == "Food"
    assert label.font().bold()


def test_create_command_section_flat_has_no_border() -> None:
    assert _qapp() is not None
    frame, _label, _layout = create_command_section(title="Images", bordered=False)
    assert "border: none" in frame.styleSheet()
    assert "border-radius" not in frame.styleSheet()


def test_create_command_section_divider_uses_border_color() -> None:
    assert _qapp() is not None
    line = create_command_section_divider()
    assert line.objectName() == COMMAND_SECTION_DIVIDER_OBJECT_NAME
    assert line.minimumHeight() == 1
    assert line.maximumHeight() == 1
    assert line.autoFillBackground()
    assert line.palette().color(QPalette.ColorRole.Window).name() == COMMAND_SECTION_BORDER_COLOR
