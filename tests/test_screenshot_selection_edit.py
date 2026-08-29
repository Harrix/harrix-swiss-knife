"""Tests for adjustable screenshot selection geometry helpers."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect

from harrix_swiss_knife.screenshot.selection_edit import (
    collect_edge_guides,
    hit_test_selection_handle,
    nudge_selection_rect,
    snap_rect_to_edges,
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


def test_collect_edge_guides_includes_window_and_bounds() -> None:
    bounds = QRect(0, 0, 200, 100)
    xs, ys = collect_edge_guides([QRect(10, 20, 30, 40)], bounds)
    assert 0 in xs
    assert 199 in xs
    assert 10 in xs
    assert 39 in xs
    assert 0 in ys
    assert 99 in ys
    assert 20 in ys
    assert 59 in ys


def test_snap_rect_to_edges_moves_left_toward_guide() -> None:
    bounds = QRect(0, 0, 200, 200)
    rect = QRect(48, 10, 40, 30)
    snapped = snap_rect_to_edges(rect, "move", [50], [10], threshold=8, bounds=bounds)
    assert snapped.left() == 50
    assert snapped.size() == rect.size()


def test_nudge_moves_one_pixel_and_shift_step() -> None:
    bounds = QRect(0, 0, 200, 200)
    rect = QRect(10, 10, 40, 30)
    assert nudge_selection_rect(rect, "right", step=1, resize=False, bounds=bounds).left() == 11
    assert nudge_selection_rect(rect, "down", step=10, resize=False, bounds=bounds).top() == 20


def test_nudge_resize_changes_size_with_fixed_origin() -> None:
    bounds = QRect(0, 0, 200, 200)
    rect = QRect(10, 10, 40, 30)
    wider = nudge_selection_rect(rect, "right", step=5, resize=True, bounds=bounds)
    assert wider.topLeft() == rect.topLeft()
    assert wider.width() == 45
    taller = nudge_selection_rect(rect, "down", step=5, resize=True, bounds=bounds)
    assert taller.height() == 35
    narrower = nudge_selection_rect(rect, "left", step=5, resize=True, bounds=bounds)
    assert narrower.width() == 35
