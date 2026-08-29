"""Tests for screenshot window snap helpers."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect

from harrix_swiss_knife.screenshot.window_rects import snap_rect_at_point


def test_snap_rect_at_point_returns_topmost_containing_rect() -> None:
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
