"""Tests for compact numeric spin boxes."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionSpinBox

from harrix_swiss_knife.qt_compact_spin_box import CompactDoubleSpinBox, CompactSpinBox


def test_compact_spin_buttons_are_narrow_and_stacked() -> None:
    app = QApplication.instance() or QApplication([])
    assert app is not None
    spin = CompactSpinBox()
    spin.resize(120, 32)
    spin.show()
    QApplication.processEvents()

    option = QStyleOptionSpinBox()
    spin.initStyleOption(option)
    up = spin.style().subControlRect(
        QStyle.ComplexControl.CC_SpinBox,
        option,
        QStyle.SubControl.SC_SpinBoxUp,
        spin,
    )
    down = spin.style().subControlRect(
        QStyle.ComplexControl.CC_SpinBox,
        option,
        QStyle.SubControl.SC_SpinBoxDown,
        spin,
    )
    edit = spin.style().subControlRect(
        QStyle.ComplexControl.CC_SpinBox,
        option,
        QStyle.SubControl.SC_SpinBoxEditField,
        spin,
    )

    assert up.width() == 11
    assert down.width() == 11
    assert up.x() == down.x()
    assert spin.rect().right() - up.right() == 5
    assert up.top() - spin.rect().top() == 2
    assert spin.rect().bottom() - down.bottom() == 2
    assert up.center().y() < down.center().y()
    assert edit.right() == up.left() - 1
    spin.close()


def test_compact_style_survives_caller_stylesheet() -> None:
    spin = CompactDoubleSpinBox()
    caller_style = "QDoubleSpinBox { background: lightblue; }"
    spin.setStyleSheet(caller_style)

    assert spin.styleSheet() == caller_style
    spin.close()
