"""SmoothScroller must tolerate eventFilter before init finishes."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QListWidget


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_smooth_scroller_event_filter_before_viewport_ready(qapp: QApplication) -> None:
    """Polish storms must not crash when `_viewport` is still unset."""
    assert qapp is not None
    from harrix_swiss_knife.fluent.widgets.views import SmoothScroller

    area = QListWidget()
    scroller = SmoothScroller.__new__(SmoothScroller)
    QObject.__init__(scroller, area)
    event = QWheelEvent(
        QPoint(0, 0),
        QPoint(0, 0),
        QPoint(0, 0),
        QPoint(0, 120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,  # noqa: FBT003
    )
    assert scroller.eventFilter(area, event) is False
    assert scroller.eventFilter(area, QEvent(QEvent.Type.Polish)) is False
    area.close()
