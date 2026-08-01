"""Tests for toast stack positioning (center and pinned)."""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize

from harrix_swiss_knife.toast_notification_base import SCREEN_MARGIN, STACK_GAP, compute_toast_stack_positions


def test_single_toast_uses_home_center() -> None:
    area = QRect(0, 0, 1000, 800)
    size = QSize(200, 80)
    points = compute_toast_stack_positions([size], area=area, pinned=False)
    assert len(points) == 1
    assert points[0].x() == (1000 - 200) // 2
    assert points[0].y() == (800 - 80) // 2


def test_single_toast_uses_home_bottom_right() -> None:
    area = QRect(0, 0, 1000, 800)
    size = QSize(200, 60)
    points = compute_toast_stack_positions([size], area=area, pinned=True)
    assert points[0].x() == 1000 - 200 - SCREEN_MARGIN
    assert points[0].y() == 800 - 60 - SCREEN_MARGIN


def test_two_toasts_stack_upward_when_room() -> None:
    area = QRect(0, 0, 1000, 800)
    older = QSize(200, 80)
    newer = QSize(200, 80)
    points = compute_toast_stack_positions([older, newer], area=area, pinned=False)
    newer_home_y = (800 - 80) // 2
    assert points[1].y() == newer_home_y
    assert points[0].y() == newer_home_y - STACK_GAP - older.height()
    assert points[0].y() < points[1].y()


def test_overflow_overlaps_home_when_no_room_at_top() -> None:
    # Tiny area: stacking a second toast above home would go past the top margin.
    area = QRect(0, 0, 400, 120)
    older = QSize(100, 50)
    newer = QSize(100, 50)
    points = compute_toast_stack_positions([older, newer], area=area, pinned=False)
    home_y = (120 - 50) // 2
    assert points[1].y() == home_y
    assert points[0].y() == home_y


def test_pinned_stack_grows_upward_from_bottom_right() -> None:
    area = QRect(0, 0, 1000, 800)
    older = QSize(180, 40)
    newer = QSize(180, 40)
    points = compute_toast_stack_positions([older, newer], area=area, pinned=True)
    newer_y = 800 - 40 - SCREEN_MARGIN
    assert points[1].y() == newer_y
    assert points[0].y() == newer_y - STACK_GAP - older.height()
    assert points[0].x() == 1000 - 180 - SCREEN_MARGIN
