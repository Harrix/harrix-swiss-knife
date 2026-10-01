"""Tests for Lucide checkbox indicators (per-widget style, no app QSS / setStyle)."""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QCheckBox, QStyle, QStyleOptionButton, QWidget

from harrix_swiss_knife.apps.common.delegates.lucide_checkable_item_delegate import (
    LucideCheckableItemDelegate,
)
from harrix_swiss_knife.qt_lucide_checkbox import (
    LucideCheckboxStyle,
    apply_lucide_checkbox_style,
    apply_lucide_checkboxes,
    lucide_checkbox_pixmap,
    paint_lucide_checkbox,
)


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_lucide_checkbox_pixmap_checked_and_unchecked() -> None:
    assert _qapp() is not None
    unchecked = lucide_checkbox_pixmap(checked=False)
    checked = lucide_checkbox_pixmap(checked=True)
    partial = lucide_checkbox_pixmap(partial=True)
    assert not unchecked.isNull()
    assert not checked.isNull()
    assert not partial.isNull()
    assert unchecked.toImage() != checked.toImage()


def test_apply_lucide_checkboxes_sets_widget_style_not_app_style() -> None:
    app = _qapp()
    before = app.style()
    host = QWidget()
    box = QCheckBox("Demo", host)
    apply_lucide_checkboxes(host)
    assert app.style() is before
    assert not isinstance(app.style(), LucideCheckboxStyle)
    assert isinstance(box.style(), LucideCheckboxStyle)
    host.close()


def test_apply_lucide_checkbox_style_is_idempotent() -> None:
    assert _qapp() is not None
    box = QCheckBox("Demo")
    apply_lucide_checkbox_style(box)
    first = box.style()
    apply_lucide_checkbox_style(box)
    assert box.style() is first
    box.close()


def test_lucide_checkbox_style_draws_indicator() -> None:
    assert _qapp() is not None
    style = LucideCheckboxStyle()
    canvas = QPixmap(40, 40)
    canvas.fill(Qt.GlobalColor.white)
    painter = QPainter(canvas)
    option = QStyleOptionButton()
    option.rect = QRect(8, 8, 16, 16)
    option.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_On
    style.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorCheckBox, option, painter, None)
    painter.end()
    assert any(canvas.toImage().pixelColor(x, y) != Qt.GlobalColor.white for x in range(40) for y in range(40))


def test_paint_lucide_checkbox_draws_into_pixmap() -> None:
    assert _qapp() is not None
    canvas = QPixmap(40, 40)
    canvas.fill(Qt.GlobalColor.white)
    painter = QPainter(canvas)
    paint_lucide_checkbox(painter, QRect(0, 0, 40, 40), checked=True)
    painter.end()
    assert any(canvas.toImage().pixelColor(x, y) != Qt.GlobalColor.white for x in range(40) for y in range(40))


def test_lucide_checkable_item_delegate_constructs() -> None:
    assert _qapp() is not None
    host = QWidget()
    delegate = LucideCheckableItemDelegate(host)
    assert isinstance(delegate, LucideCheckableItemDelegate)
    host.close()
