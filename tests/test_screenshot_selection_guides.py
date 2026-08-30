"""Tests for screenshot composition guides and measurement labels."""

from __future__ import annotations

from PySide6.QtCore import QRect

from harrix_swiss_knife.screenshot.selection_guides import (
    diagonal_angle_degrees,
    diagonal_length_px,
    format_angle_label,
    guide_offsets,
    place_angle_label,
    place_height_label,
    place_width_label,
)


def test_diagonal_length_and_angle_match_example_frame() -> None:
    """110 x 207 frame: integer diagonal 234 and angle about 62.0138 degrees."""
    assert diagonal_length_px(110, 207) == 234
    assert round(diagonal_angle_degrees(110, 207), 4) == 62.0138
    assert format_angle_label(62.0138) == "62.0138 °"


def test_guide_offsets_are_thirds_and_half() -> None:
    assert guide_offsets(90) == (30, 45, 60)
    assert guide_offsets(100) == (33, 50, 66)


def test_width_and_height_labels_flip_inside_near_edges() -> None:
    bounds = QRect(0, 0, 200, 200)
    roomy = QRect(40, 40, 80, 60)
    width_box, width_inside = place_width_label(roomy, bounds, text_width=20, text_height=12)
    height_box, height_inside = place_height_label(roomy, bounds, text_width=20, text_height=12)
    assert not width_inside
    assert width_box.bottom() <= roomy.top()
    assert not height_inside
    assert height_box.right() <= roomy.left()

    tight = QRect(0, 0, 80, 60)
    _width_box, width_inside = place_width_label(tight, bounds, text_width=20, text_height=12)
    _height_box, height_inside = place_height_label(tight, bounds, text_width=20, text_height=12)
    assert width_inside
    assert height_inside


def test_angle_label_flips_inside_at_bottom_right() -> None:
    bounds = QRect(0, 0, 200, 200)
    roomy = QRect(40, 40, 80, 60)
    box, inside = place_angle_label(roomy, bounds, text_width=70, text_height=12)
    assert not inside
    assert box.top() >= roomy.bottom()

    flush = QRect(120, 140, 80, 60)
    box, inside = place_angle_label(flush, bounds, text_width=70, text_height=12)
    assert inside
    assert bounds.contains(box)
    assert flush.contains(box)
