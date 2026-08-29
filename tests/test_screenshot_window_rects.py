"""Tests for screenshot window snap helpers."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect

from harrix_swiss_knife.screenshot.window_rects import (
    _SnapCandidate,
    filter_nested_control_candidates,
    snap_rect_at_point,
)


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
