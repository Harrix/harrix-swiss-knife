"""Tests for adjustable screenshot selection geometry helpers."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect

from harrix_swiss_knife.screenshot.selection_edit import (
    hit_test_selection_handle,
    transform_selection_rect,
)


def test_hit_test_prefers_corners_then_edges_then_move() -> None:
    rect = QRect(10, 10, 100, 80)
    assert hit_test_selection_handle(rect, QPoint(10, 10)) == "nw"
    assert hit_test_selection_handle(rect, QPoint(60, 10)) == "n"
    assert hit_test_selection_handle(rect, QPoint(50, 50)) == "move"
    assert hit_test_selection_handle(rect, QPoint(0, 0)) is None


def test_transform_move_keeps_size_and_clamps_to_bounds() -> None:
    start = QRect(10, 10, 40, 30)
    bounds = QRect(0, 0, 100, 100)
    moved = transform_selection_rect(
        start,
        "move",
        QPoint(20, 20),
        QPoint(30, 25),
        bounds=bounds,
    )
    assert moved.size() == start.size()
    assert moved.topLeft() == QPoint(20, 15)


def test_transform_resize_se_grows_bottom_right() -> None:
    start = QRect(10, 10, 40, 30)
    bounds = QRect(0, 0, 200, 200)
    resized = transform_selection_rect(
        start,
        "se",
        QPoint(49, 39),
        QPoint(59, 49),
        bounds=bounds,
    )
    assert resized.width() >= start.width()
    assert resized.height() >= start.height()
    assert resized.topLeft() == start.topLeft()
