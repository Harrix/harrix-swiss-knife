"""Tests for screenshot annotation model."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QImage

from harrix_swiss_knife.apps.snippets.seed import SEED_COLORS
from harrix_swiss_knife.screenshot.annotation_colors import load_annotation_colors
from harrix_swiss_knife.screenshot.annotations import (
    Annotation,
    AnnotationDocument,
    AnnotationStyle,
    AnnotationTool,
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
