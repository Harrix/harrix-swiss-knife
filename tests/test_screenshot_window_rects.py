"""Tests for screenshot window snap helpers."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QApplication, QDialog

from harrix_swiss_knife.screenshot.window_rects import (
    _list_qt_top_level_rects,
    _SnapCandidate,
    filter_nested_control_candidates,
    merge_preferred_rects,
    snap_rect_at_point,
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


def test_snap_rect_at_point_returns_first_containing_rect() -> None:
    top = QRect(10, 10, 100, 80)
    under = QRect(0, 0, 200, 200)
    assert snap_rect_at_point(QPoint(50, 50), [top, under]) == top


def test_snap_rect_at_point_returns_none_outside_windows() -> None:
    windows = [QRect(10, 10, 40, 40), QRect(100, 100, 50, 50)]
    assert snap_rect_at_point(QPoint(0, 0), windows) is None


def test_snap_rect_at_point_copies_rect() -> None:
    original = QRect(5, 5, 20, 20)
    snapped = snap_rect_at_point(QPoint(10, 10), [original])
    assert snapped is not None
    snapped.moveTopLeft(QPoint(0, 0))
    assert original.topLeft() == QPoint(5, 5)


def test_filter_nested_control_candidates_keeps_windows() -> None:
    frame = QRect(0, 0, 200, 200)
    client = QRect(8, 30, 184, 162)
    filtered = filter_nested_control_candidates(
        [
            _SnapCandidate(rect=client, is_window=False),
            _SnapCandidate(rect=frame, is_window=True),
        ]
    )
    assert filtered == [client, frame]


def test_filter_nested_control_candidates_drops_control_inside_earlier_region() -> None:
    panel = QRect(0, 0, 100, 100)
    button = QRect(10, 10, 20, 20)
    filtered = filter_nested_control_candidates(
        [
            _SnapCandidate(rect=panel, is_window=False),
            _SnapCandidate(rect=button, is_window=False),
        ]
    )
    assert filtered == [panel]


def test_merge_preferred_rects_inserts_dialog_before_owner() -> None:
    owner = QRect(0, 0, 1000, 800)
    dialog = QRect(200, 150, 400, 300)
    button = QRect(220, 400, 80, 30)
    assert merge_preferred_rects([button, owner], [dialog]) == [button, dialog, owner]


def test_merge_preferred_rects_skips_duplicate() -> None:
    dialog = QRect(200, 150, 400, 300)
    assert merge_preferred_rects([dialog], [dialog]) == [dialog]


def test_snap_prefers_merged_dialog_over_owner() -> None:
    owner = QRect(0, 0, 1000, 800)
    dialog = QRect(200, 150, 400, 300)
    merged = merge_preferred_rects([owner], [dialog])
    assert snap_rect_at_point(QPoint(250, 200), merged) == dialog
    assert snap_rect_at_point(QPoint(20, 20), merged) == owner


def test_list_qt_top_level_rects_includes_dialog(qapp: QApplication) -> None:  # noqa: ARG001
    dialog = QDialog()
    dialog.setWindowTitle("Balance check")
    dialog.resize(400, 300)
    dialog.show()
    QApplication.processEvents()
    try:
        rects = _list_qt_top_level_rects(exclude_hwnds=set())
        frame = dialog.frameGeometry()
        assert any(rect == frame or rect.contains(frame.center()) for rect in rects)
    finally:
        dialog.close()
