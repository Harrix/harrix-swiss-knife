"""Tests for magnetic snapping between screenshot annotations."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor

from harrix_swiss_knife.screenshot.annotation_edit import apply_annotation_edit
from harrix_swiss_knife.screenshot.annotation_snap import (
    collect_annotation_guides,
    snap_annotation_edit,
    snap_point,
    snap_shape_end,
)
from harrix_swiss_knife.screenshot.annotations import Annotation, AnnotationStyle, AnnotationTool


def _arrow(start: QPointF, end: QPointF) -> Annotation:
    return Annotation(tool=AnnotationTool.ARROW, points=[start, end], style=AnnotationStyle())


def _rect(top_left: QPointF, bottom_right: QPointF) -> Annotation:
    return Annotation(
        tool=AnnotationTool.RECTANGLE,
        points=[top_left, bottom_right],
        style=AnnotationStyle(color=QColor("#de2b26")),
    )


def test_collect_annotation_guides_includes_endpoints_and_excludes_index() -> None:
    first = _arrow(QPointF(10, 20), QPointF(50, 20))
    second = _arrow(QPointF(80, 40), QPointF(90, 70))
    xs, ys = collect_annotation_guides([first, second], exclude_index=1)
    assert 10.0 in xs
    assert 50.0 in xs
    assert 80.0 not in xs
    assert 20.0 in ys
    assert 40.0 not in ys


def test_collect_annotation_guides_includes_image_bounds() -> None:
    xs, ys = collect_annotation_guides([], bounds=QRectF(0, 0, 200, 100))
    assert xs[0] == pytest.approx(0.0)
    assert xs[-1] == pytest.approx(200.0)
    assert ys[0] == pytest.approx(0.0)
    assert ys[-1] == pytest.approx(100.0)


def test_move_arrow_snaps_to_shared_origin() -> None:
    origin = _arrow(QPointF(10, 10), QPointF(50, 10))
    other = _arrow(QPointF(14, 16), QPointF(80, 40))
    xs, ys = collect_annotation_guides([origin, other], exclude_index=1)
    moved = apply_annotation_edit(
        other,
        "move",
        [QPointF(14, 16), QPointF(80, 40)],
        QPointF(14, 16),
        QPointF(14, 16),
        shift=False,
    )
    snapped = snap_annotation_edit(other, "move", moved, xs, ys)
    assert snapped.points[0].x() == pytest.approx(10.0)
    assert snapped.points[0].y() == pytest.approx(10.0)
    assert snapped.points[1].x() == pytest.approx(76.0)
    assert snapped.points[1].y() == pytest.approx(34.0)
    assert snapped.x_guide == pytest.approx(10.0)
    assert snapped.y_guide == pytest.approx(10.0)


def test_move_arrow_snaps_to_same_vertical() -> None:
    vertical = _arrow(QPointF(30, 10), QPointF(30, 50))
    other = _arrow(QPointF(36, 20), QPointF(70, 40))
    xs, ys = collect_annotation_guides([vertical, other], exclude_index=1)
    moved = apply_annotation_edit(
        other,
        "move",
        [QPointF(36, 20), QPointF(70, 40)],
        QPointF(36, 20),
        QPointF(36, 20),
        shift=False,
    )
    snapped = snap_annotation_edit(other, "move", moved, xs, ys)
    assert snapped.points[0].x() == pytest.approx(30.0)
    assert snapped.points[1].x() == pytest.approx(64.0)
    assert snapped.points[0].y() == pytest.approx(20.0)
    assert snapped.x_guide == pytest.approx(30.0)
    assert snapped.y_guide is None


def test_drag_arrow_end_snaps_to_other_tip() -> None:
    first = _arrow(QPointF(10, 40), QPointF(80, 40))
    second = _arrow(QPointF(20, 10), QPointF(76, 36))
    xs, ys = collect_annotation_guides([first, second], exclude_index=1)
    points = apply_annotation_edit(
        second,
        "end",
        [QPointF(20, 10), QPointF(76, 36)],
        QPointF(76, 36),
        QPointF(76, 36),
        shift=False,
    )
    snapped = snap_annotation_edit(second, "end", points, xs, ys)
    assert snapped.points[0].x() == pytest.approx(20.0)
    assert snapped.points[1].x() == pytest.approx(80.0)
    assert snapped.points[1].y() == pytest.approx(40.0)


def test_no_snap_outside_threshold() -> None:
    first = _arrow(QPointF(10, 10), QPointF(50, 10))
    second = _arrow(QPointF(40, 40), QPointF(90, 70))
    xs, ys = collect_annotation_guides([first, second], exclude_index=1)
    snapped = snap_annotation_edit(second, "move", list(second.points), xs, ys, threshold=8.0)
    assert snapped.points[0].x() == pytest.approx(40.0)
    assert snapped.points[0].y() == pytest.approx(40.0)
    assert snapped.x_guide is None
    assert snapped.y_guide is None


def test_shift_horizontal_endpoint_snaps_x_only() -> None:
    first = _arrow(QPointF(10, 10), QPointF(50, 10))
    second = _arrow(QPointF(20, 40), QPointF(46, 40))
    xs, ys = collect_annotation_guides([first, second], exclude_index=1)
    snapped = snap_annotation_edit(second, "end", list(second.points), xs, ys, shift=True)
    assert snapped.points[1].x() == pytest.approx(50.0)
    assert snapped.points[1].y() == pytest.approx(40.0)
    assert snapped.y_guide is None


def test_rectangle_edge_snaps_to_other_rect() -> None:
    first = _rect(QPointF(10, 10), QPointF(40, 50))
    second = _rect(QPointF(46, 20), QPointF(90, 60))
    xs, ys = collect_annotation_guides([first, second], exclude_index=1)
    snapped = snap_annotation_edit(second, "w", list(second.points), xs, ys)
    assert snapped.points[0].x() == pytest.approx(40.0)
    assert snapped.points[1].x() == pytest.approx(90.0)
    assert snapped.x_guide == pytest.approx(40.0)


def test_snap_point_and_draft_end() -> None:
    snapped, x_guide, y_guide = snap_point(QPointF(12, 18), [10.0], [20.0], threshold=8.0)
    assert snapped.x() == pytest.approx(10.0)
    assert snapped.y() == pytest.approx(20.0)
    assert x_guide == pytest.approx(10.0)
    assert y_guide == pytest.approx(20.0)
    end, gx, gy = snap_shape_end(
        AnnotationTool.ARROW,
        QPointF(0, 40),
        QPointF(48, 40),
        [50.0],
        [10.0],
        shift=True,
    )
    assert end.x() == pytest.approx(50.0)
    assert end.y() == pytest.approx(40.0)
    assert gx == pytest.approx(50.0)
    assert gy is None
