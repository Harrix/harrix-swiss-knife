"""Tests for screenshot annotation model."""

from __future__ import annotations

import math

import pytest
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage

from harrix_swiss_knife.apps.snippets.seed import SEED_COLORS
from harrix_swiss_knife.screenshot.annotation_colors import load_annotation_colors
from harrix_swiss_knife.screenshot.annotation_edit import (
    apply_annotation_edit,
    hit_test_annotation,
    hit_test_topmost,
)
from harrix_swiss_knife.screenshot.annotations import (
    Annotation,
    AnnotationDocument,
    AnnotationStyle,
    AnnotationTool,
    _arrow_head_path,
    constrain_shape_end,
)


def _blank(width: int = 100, height: int = 80) -> QImage:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(255, 255, 255))
    return image


def test_arrow_commit_and_undo() -> None:
    doc = AnnotationDocument(_blank())
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.ARROW,
            points=[QPointF(10, 10), QPointF(60, 40)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    assert len(doc.annotations) == 1
    rendered = doc.render(include_draft=False)
    assert rendered.width() == 100
    assert doc.can_undo
    assert doc.undo()
    assert doc.annotations == []


def test_arrow_is_round_shaft_with_filled_head() -> None:
    color = QColor("#de2b26")
    doc = AnnotationDocument(_blank(160, 80))
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.ARROW,
            points=[QPointF(12, 40), QPointF(140, 40)],
            style=AnnotationStyle(color=color, width=3.0),
        )
    )
    assert doc.commit_draft()
    rendered = doc.render(include_draft=False)
    shaft = rendered.pixelColor(50, 40)
    shaft_edge = rendered.pixelColor(50, 41)
    above_shaft = rendered.pixelColor(50, 30)
    # Tip 140, head length 18 → wings near x=122; sample inside the fill.
    head = rendered.pixelColor(130, 40)
    head_wing = rendered.pixelColor(128, 43)
    assert shaft.red() > 150
    assert shaft.green() < 80
    assert shaft_edge.red() > 150
    assert above_shaft.green() > 200
    assert head.red() > 150
    assert head.green() < 80
    assert head_wing.red() > 150
    assert head_wing.green() < 80


def test_arrow_head_back_is_concave_like_sharex() -> None:
    """Rear edge bows toward the tip (ShareX Classic quadratic notch)."""
    path = _arrow_head_path(QPointF(12, 40), QPointF(140, 40), stroke=3.0)
    assert path is not None
    assert path.contains(QPointF(134, 40))
    assert path.contains(QPointF(128, 40))
    # Centerline behind the quadratic notch stays empty.
    assert not path.contains(QPointF(120, 40))
    assert not path.contains(QPointF(122, 40))


def test_tiny_drag_is_ignored() -> None:
    doc = AnnotationDocument(_blank())
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.RECTANGLE,
            points=[QPointF(10, 10), QPointF(11, 10)],
            style=AnnotationStyle(),
        )
    )
    assert not doc.commit_draft()
    assert doc.annotations == []


def test_crop_resets_annotations() -> None:
    doc = AnnotationDocument(_blank(200, 100))
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.LINE,
            points=[QPointF(5, 5), QPointF(50, 50)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    assert doc.apply_crop(QRectF(20, 10, 80, 60))
    assert doc.annotations == []
    assert doc.base_image.width() == 80
    assert doc.base_image.height() == 60
    assert doc.undo()
    assert doc.base_image.width() == 200
    assert len(doc.annotations) == 1


def test_text_requires_non_empty() -> None:
    doc = AnnotationDocument(_blank())
    doc.begin_draft(Annotation(tool=AnnotationTool.TEXT, points=[QPointF(5, 5)], text="  ", style=AnnotationStyle()))
    assert not doc.commit_draft()
    doc.begin_draft(Annotation(tool=AnnotationTool.TEXT, points=[QPointF(5, 5)], text="Hi", style=AnnotationStyle()))
    assert doc.commit_draft()


def test_load_annotation_colors_fallback() -> None:
    colors = load_annotation_colors()
    assert colors
    assert all(isinstance(hex_value, str) and hex_value.startswith("#") for hex_value, _hint in colors)
    # Without a usable snippets DB in the test env, seed palette is acceptable.
    assert len(colors) >= len(SEED_COLORS) or colors == list(SEED_COLORS)


def test_shift_keeps_free_end_without_modifier() -> None:
    start = QPointF(10, 10)
    raw = QPointF(50, 30)
    end = constrain_shape_end(AnnotationTool.LINE, start, raw, shift=False)
    assert end.x() == pytest.approx(50.0)
    assert end.y() == pytest.approx(30.0)


def test_shift_makes_ellipse_circle() -> None:
    start = QPointF(10, 10)
    end = constrain_shape_end(AnnotationTool.ELLIPSE, start, QPointF(50, 30), shift=True)
    assert end.x() == pytest.approx(30.0)
    assert end.y() == pytest.approx(30.0)


def test_shift_makes_ellipse_circle_up_left() -> None:
    start = QPointF(80, 80)
    end = constrain_shape_end(AnnotationTool.ELLIPSE, start, QPointF(20, 50), shift=True)
    assert end.x() == pytest.approx(50.0)
    assert end.y() == pytest.approx(50.0)


def test_shift_makes_rectangle_square() -> None:
    start = QPointF(10, 10)
    end = constrain_shape_end(AnnotationTool.RECTANGLE, start, QPointF(50, 30), shift=True)
    assert end.x() == pytest.approx(30.0)
    assert end.y() == pytest.approx(30.0)


def test_shift_pen_ignores_constraint() -> None:
    start = QPointF(10, 10)
    raw = QPointF(50, 30)
    end = constrain_shape_end(AnnotationTool.PEN, start, raw, shift=True)
    assert end.x() == pytest.approx(50.0)
    assert end.y() == pytest.approx(30.0)


def test_shift_snaps_arrow_to_45_degrees() -> None:
    start = QPointF(0, 0)
    end = constrain_shape_end(AnnotationTool.ARROW, start, QPointF(100, 84), shift=True)
    length = math.hypot(100, 84)
    expected = length / math.sqrt(2)
    assert end.x() == pytest.approx(expected)
    assert end.y() == pytest.approx(expected)


def test_shift_snaps_line_to_horizontal() -> None:
    start = QPointF(10, 20)
    end = constrain_shape_end(AnnotationTool.LINE, start, QPointF(80, 25), shift=True)
    assert end.y() == pytest.approx(20.0)
    assert end.x() == pytest.approx(10 + math.hypot(70, 5))


def test_shift_snaps_line_to_vertical() -> None:
    start = QPointF(40, 10)
    end = constrain_shape_end(AnnotationTool.LINE, start, QPointF(48, 90), shift=True)
    assert end.x() == pytest.approx(40.0)
    assert end.y() == pytest.approx(10 + math.hypot(8, 80))


def test_hit_test_arrow_prefers_endpoint_handle() -> None:
    arrow = Annotation(
        tool=AnnotationTool.ARROW,
        points=[QPointF(10, 40), QPointF(80, 40)],
        style=AnnotationStyle(width=3.0),
    )
    assert hit_test_annotation(arrow, QPointF(80, 40), handle_size=8.0) == "end"
    assert hit_test_annotation(arrow, QPointF(10, 40), handle_size=8.0) == "start"
    assert hit_test_annotation(arrow, QPointF(45, 40), handle_size=8.0) == "move"
    assert hit_test_annotation(arrow, QPointF(45, 20), handle_size=8.0) is None


def test_hit_test_topmost_uses_front_annotation() -> None:
    back = Annotation(
        tool=AnnotationTool.LINE,
        points=[QPointF(10, 10), QPointF(90, 10)],
        style=AnnotationStyle(width=3.0),
    )
    front = Annotation(
        tool=AnnotationTool.LINE,
        points=[QPointF(10, 10), QPointF(90, 10)],
        style=AnnotationStyle(width=3.0),
    )
    hit = hit_test_topmost([back, front], QPointF(50, 10), handle_size=8.0)
    assert hit == (1, "move")


def test_hit_test_topmost_prefers_matching_tool() -> None:
    arrow = Annotation(
        tool=AnnotationTool.ARROW,
        points=[QPointF(10, 40), QPointF(80, 40)],
        style=AnnotationStyle(width=3.0),
    )
    line = Annotation(
        tool=AnnotationTool.LINE,
        points=[QPointF(10, 40), QPointF(80, 40)],
        style=AnnotationStyle(width=3.0),
    )
    hit = hit_test_topmost([arrow, line], QPointF(45, 40), handle_size=8.0)
    assert hit == (1, "move")
    preferred = hit_test_topmost(
        [arrow, line],
        QPointF(45, 40),
        handle_size=8.0,
        prefer_tool=AnnotationTool.ARROW,
    )
    assert preferred == (0, "move")


def test_hit_test_rectangle_uses_stroke_not_interior() -> None:
    rect = Annotation(
        tool=AnnotationTool.RECTANGLE,
        points=[QPointF(10, 10), QPointF(80, 60)],
        style=AnnotationStyle(width=3.0),
    )
    assert hit_test_annotation(rect, QPointF(10, 30), handle_size=8.0) == "move"
    assert hit_test_annotation(rect, QPointF(40, 35), handle_size=8.0) is None
    assert hit_test_annotation(rect, QPointF(10, 10), handle_size=8.0) == "nw"


def test_delete_annotation_and_undo() -> None:
    doc = AnnotationDocument(_blank())
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.ARROW,
            points=[QPointF(10, 10), QPointF(60, 40)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    assert doc.delete_at(0)
    assert doc.annotations == []
    assert doc.undo()
    assert len(doc.annotations) == 1


def test_move_arrow_keeps_length() -> None:
    arrow = Annotation(
        tool=AnnotationTool.ARROW,
        points=[QPointF(10, 10), QPointF(50, 10)],
        style=AnnotationStyle(),
    )
    moved = apply_annotation_edit(
        arrow,
        "move",
        [QPointF(10, 10), QPointF(50, 10)],
        QPointF(10, 10),
        QPointF(20, 25),
        shift=False,
    )
    assert moved[0].x() == pytest.approx(20.0)
    assert moved[0].y() == pytest.approx(25.0)
    assert moved[1].x() == pytest.approx(60.0)
    assert moved[1].y() == pytest.approx(25.0)


def test_drag_arrow_end_updates_tip() -> None:
    arrow = Annotation(
        tool=AnnotationTool.ARROW,
        points=[QPointF(10, 40), QPointF(80, 40)],
        style=AnnotationStyle(),
    )
    points = apply_annotation_edit(
        arrow,
        "end",
        [QPointF(10, 40), QPointF(80, 40)],
        QPointF(80, 40),
        QPointF(70, 20),
        shift=False,
    )
    assert points[0].x() == pytest.approx(10.0)
    assert points[1].x() == pytest.approx(70.0)
    assert points[1].y() == pytest.approx(20.0)
