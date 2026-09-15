"""Tests for Ctrl+wheel icon size changes in Vector Icons."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.icons.settings import ICON_SIZE_WHEEL_STEP
from harrix_swiss_knife.apps.icons.widgets import DraggableIconList, icon_size_delta_from_wheel


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _wheel(angle_y: int, *, ctrl: bool) -> MagicMock:
    event = MagicMock()
    event.modifiers.return_value = Qt.KeyboardModifier.ControlModifier if ctrl else Qt.KeyboardModifier.NoModifier
    event.angleDelta.return_value.y.return_value = angle_y
    return event


def test_icon_size_delta_from_wheel_requires_ctrl() -> None:
    assert icon_size_delta_from_wheel(_wheel(120, ctrl=False), variants_context=False) is None
    assert icon_size_delta_from_wheel(_wheel(120, ctrl=True), variants_context=True) is None
    assert icon_size_delta_from_wheel(_wheel(120, ctrl=True), variants_context=False) == ICON_SIZE_WHEEL_STEP
    assert icon_size_delta_from_wheel(_wheel(-120, ctrl=True), variants_context=False) == -ICON_SIZE_WHEEL_STEP
    assert icon_size_delta_from_wheel(_wheel(60, ctrl=True), variants_context=False) == ICON_SIZE_WHEEL_STEP


def test_main_grid_ctrl_wheel_emits_size_delta(qapp: QApplication) -> None:  # noqa: ARG001
    icon_list = DraggableIconList(variants_context=False)
    emitted: list[int] = []
    icon_list.icon_size_delta_requested.connect(emitted.append)
    icon_list.wheelEvent(_wheel(120, ctrl=True))
    assert emitted == [ICON_SIZE_WHEEL_STEP]
    icon_list.wheelEvent(_wheel(-240, ctrl=True))
    assert emitted == [ICON_SIZE_WHEEL_STEP, -2 * ICON_SIZE_WHEEL_STEP]


def test_variants_grid_ctrl_wheel_does_not_emit(qapp: QApplication) -> None:  # noqa: ARG001
    icon_list = DraggableIconList(variants_context=True)
    emitted: list[int] = []
    icon_list.icon_size_delta_requested.connect(emitted.append)
    assert icon_size_delta_from_wheel(_wheel(120, ctrl=True), variants_context=True) is None
    # Avoid calling Qt's wheelEvent with a mock; the helper already gates variants.
    assert emitted == []
