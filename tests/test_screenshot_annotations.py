"""Tests for screenshot annotation model."""

from __future__ import annotations

import math

import pytest
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication

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
    next_step_number,
    sample_composited_color,
    step_circle_points,
)


def _blank(width: int = 100, height: int = 80) -> QImage:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(255, 255, 255))
    return image


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


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


def test_resize_scales_image_and_undo_restores_it() -> None:
    doc = AnnotationDocument(_blank(40, 20))
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.LINE,
            points=[QPointF(1, 1), QPointF(10, 10)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    assert not doc.apply_resize(40, 20)
    assert not doc.apply_resize(80, 10)
    assert doc.apply_resize(20, 10)
    assert doc.annotations == []
    assert doc.base_image.width() == 20
    assert doc.base_image.height() == 10
    assert doc.undo()
    assert doc.base_image.width() == 40
    assert len(doc.annotations) == 1


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


def test_highlight_is_translucent_and_selectable() -> None:
    doc = AnnotationDocument(_blank())
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.HIGHLIGHT,
            points=[QPointF(10, 10), QPointF(30, 20)],
            style=AnnotationStyle(color=QColor("#ff0000")),
        )
    )
    assert doc.commit_draft()
    rendered = doc.render()
    center = rendered.pixelColor(20, 15)
    outside = rendered.pixelColor(2, 2)
    assert center.red() == 255
    assert center.green() < 200
    assert center.blue() < 200
    assert (outside.red(), outside.green(), outside.blue()) == (255, 255, 255)
    highlight = doc.annotations[0]
    assert hit_test_annotation(highlight, QPointF(20, 15), handle_size=8) == "move"
    end = constrain_shape_end(AnnotationTool.HIGHLIGHT, QPointF(10, 10), QPointF(50, 30), shift=True)
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


@pytest.mark.usefixtures("qapp")
def test_blur_softens_pixels_inside_and_keeps_outside() -> None:
    image = _blank(100, 60)
    painter = QPainter(image)
    painter.fillRect(40, 20, 20, 20, QColor(0, 0, 0))
    painter.end()
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.BLUR,
            points=[QPointF(30, 10), QPointF(70, 50)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    rendered = doc.render(include_draft=False)
    outside = rendered.pixelColor(29, 30)
    assert outside.red() == 255
    assert outside.green() == 255
    assert outside.blue() == 255
    center = rendered.pixelColor(50, 30)
    assert center.alpha() == 255
    assert center.red() > 20
    nearby = rendered.pixelColor(36, 30)
    assert nearby.alpha() == 255
    assert nearby.red() < 250
    assert doc.undo()
    restored = doc.render(include_draft=False)
    assert restored.pixelColor(50, 30).red() == 0


@pytest.mark.usefixtures("qapp")
def test_blur_follows_the_rectangle_instead_of_a_baked_patch() -> None:
    image = _blank(200, 80)
    painter = QPainter(image)
    painter.fillRect(140, 30, 20, 20, QColor(0, 0, 0))
    painter.end()
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.BLUR,
            points=[QPointF(4, 4), QPointF(24, 24)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    moved = doc.render(include_draft=False).pixelColor(14, 14)
    assert moved.red() == 255
    doc.annotations[0].points = [QPointF(130, 20), QPointF(170, 60)]
    rendered = doc.render(include_draft=False)
    assert rendered.pixelColor(150, 40).red() > 20
    assert rendered.pixelColor(14, 14).red() == 255


@pytest.mark.usefixtures("qapp")
def test_shape_drawn_after_blur_stays_sharp() -> None:
    image = _blank(100, 60)
    painter = QPainter(image)
    painter.fillRect(40, 20, 20, 20, QColor(0, 0, 0))
    painter.end()
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.BLUR,
            points=[QPointF(10, 10), QPointF(90, 50)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.LINE,
            points=[QPointF(10, 30), QPointF(90, 30)],
            style=AnnotationStyle(color=QColor(255, 0, 0), width=6.0),
        )
    )
    assert doc.commit_draft()
    stroke = doc.render(include_draft=False).pixelColor(50, 30)
    assert stroke.red() > 200
    assert stroke.green() < 40
    assert stroke.blue() < 40


def test_shift_makes_blur_square() -> None:
    end = constrain_shape_end(AnnotationTool.BLUR, QPointF(10, 10), QPointF(50, 30), shift=True)
    assert end.x() == pytest.approx(30.0)
    assert end.y() == pytest.approx(30.0)


def test_smart_eraser_fills_with_the_color_where_the_drag_started() -> None:
    image = _blank(40, 40)
    painter = QPainter(image)
    painter.fillRect(0, 0, 8, 40, QColor(0, 0, 220))
    painter.end()
    color = sample_composited_color(image, [], QPointF(2, 5))
    assert color.blue() == 220
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.SMART_ERASER,
            points=[QPointF(0, 4), QPointF(30, 20)],
            style=AnnotationStyle(color=color),
        )
    )
    assert doc.commit_draft()
    rendered = doc.render(include_draft=False)
    covered = rendered.pixelColor(20, 10)
    assert covered.blue() == 220
    assert covered.red() == 0
    outside = rendered.pixelColor(35, 35)
    assert outside.red() == 255
    assert outside.blue() == 255


def test_smart_eraser_samples_annotations_already_drawn() -> None:
    image = _blank(40, 40)
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.LINE,
            points=[QPointF(0, 8), QPointF(30, 8)],
            style=AnnotationStyle(color=QColor(200, 10, 10), width=6.0),
        )
    )
    assert doc.commit_draft()
    color = sample_composited_color(doc.base_image, doc.annotations, QPointF(8, 8))
    assert color.red() > 150
    assert color.green() < 40


def test_shift_makes_smart_eraser_square() -> None:
    end = constrain_shape_end(AnnotationTool.SMART_ERASER, QPointF(10, 10), QPointF(50, 30), shift=True)
    assert end.x() == pytest.approx(30.0)
    assert end.y() == pytest.approx(30.0)


@pytest.mark.usefixtures("qapp")
def test_pixelate_blocks_pixels_inside_and_keeps_outside() -> None:
    image = _blank(40, 40)
    painter = QPainter(image)
    painter.fillRect(15, 0, 1, 40, QColor(0, 0, 0))
    painter.end()
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.PIXELATE,
            points=[QPointF(0, 0), QPointF(40, 40)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    rendered = doc.render(include_draft=False)
    block = rendered.pixelColor(12, 12)
    assert block.red() < 250
    assert block.red() > 100
    assert rendered.pixelColor(19, 19).red() == block.red()
    assert rendered.pixelColor(25, 12).red() == 255


@pytest.mark.usefixtures("qapp")
def test_pixelate_follows_the_rectangle_instead_of_a_baked_patch() -> None:
    image = _blank(80, 40)
    painter = QPainter(image)
    painter.fillRect(50, 10, 10, 10, QColor(0, 0, 0))
    painter.end()
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.PIXELATE,
            points=[QPointF(0, 0), QPointF(20, 20)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    assert doc.render(include_draft=False).pixelColor(5, 5).red() == 255
    doc.annotations[0].points = [QPointF(40, 0), QPointF(70, 30)]
    rendered = doc.render(include_draft=False)
    assert rendered.pixelColor(5, 5).red() == 255
    assert rendered.pixelColor(55, 15).red() < 255


@pytest.mark.usefixtures("qapp")
def test_shape_drawn_after_pixelate_stays_sharp() -> None:
    image = _blank(40, 40)
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.PIXELATE,
            points=[QPointF(0, 0), QPointF(40, 40)],
            style=AnnotationStyle(),
        )
    )
    assert doc.commit_draft()
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.LINE,
            points=[QPointF(4, 20), QPointF(36, 20)],
            style=AnnotationStyle(color=QColor(255, 0, 0), width=4.0),
        )
    )
    assert doc.commit_draft()
    stroke = doc.render(include_draft=False).pixelColor(20, 20)
    assert stroke.red() > 200
    assert stroke.green() < 40


def test_shift_makes_pixelate_square() -> None:
    end = constrain_shape_end(AnnotationTool.PIXELATE, QPointF(10, 10), QPointF(50, 30), shift=True)
    assert end.x() == pytest.approx(30.0)
    assert end.y() == pytest.approx(30.0)


def test_step_click_is_a_default_circle_and_drag_uses_the_radius() -> None:
    clicked = step_circle_points(QPointF(40, 50), QPointF(40, 50), clicked=True)
    assert clicked[0].x() == pytest.approx(22.0)
    assert clicked[1].x() == pytest.approx(58.0)
    assert clicked[1].y() - clicked[0].y() == pytest.approx(clicked[1].x() - clicked[0].x())
    dragged = step_circle_points(QPointF(40, 50), QPointF(70, 50))
    assert dragged[0].x() == pytest.approx(10.0)
    assert dragged[1].x() == pytest.approx(70.0)
    assert dragged[1].y() - dragged[0].y() == pytest.approx(60.0)


def test_next_step_number_follows_the_highest_remaining_circle() -> None:
    assert next_step_number([]) == 1
    first = Annotation(tool=AnnotationTool.STEP, points=[], style=AnnotationStyle(), text="1")
    third = Annotation(tool=AnnotationTool.STEP, points=[], style=AnnotationStyle(), text="3")
    assert next_step_number([first, third]) == 4
    assert next_step_number([first]) == 2


@pytest.mark.usefixtures("qapp")
def test_step_circle_is_filled_and_selectable_inside_only() -> None:
    image = _blank(100, 100)
    doc = AnnotationDocument(image)
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.STEP,
            points=step_circle_points(QPointF(40, 40), QPointF(40, 40), clicked=True),
            style=AnnotationStyle(color=QColor(222, 43, 38)),
            text="1",
        )
    )
    assert doc.commit_draft()
    rendered = doc.render(include_draft=False)
    inside = rendered.pixelColor(50, 40)
    assert inside.red() > 180
    assert inside.green() < 80
    corner = rendered.pixelColor(10, 10)
    assert corner.red() == 255
    assert corner.green() == 255
    step = doc.annotations[0]
    assert hit_test_annotation(step, QPointF(40, 40), handle_size=8) == "move"
    assert hit_test_annotation(step, QPointF(90, 10), handle_size=8) is None
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.STEP,
            points=step_circle_points(QPointF(80, 80), QPointF(80, 80), clicked=True),
            style=AnnotationStyle(color=QColor(222, 43, 38)),
            text=str(next_step_number(doc.annotations)),
        )
    )
    assert doc.commit_draft()
    assert doc.annotations[1].text == "2"
