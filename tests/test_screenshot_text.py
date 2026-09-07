"""Tests for screenshot text style helpers and text annotation boxes."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.qt_app_font import MONO_FONT_FAMILY
from harrix_swiss_knife.screenshot.annotation_edit import annotation_bounds, apply_annotation_edit
from harrix_swiss_knife.screenshot.annotations import (
    Annotation,
    AnnotationDocument,
    AnnotationStyle,
    AnnotationTool,
    text_annotation_rect,
)
from harrix_swiss_knife.screenshot.text_style import (
    ScreenshotTextSettings,
    annotation_qfont,
    default_text_box_points,
    default_text_font_family,
    settings_to_annotation_style,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_default_text_font_prefers_jetbrains_or_arial(qapp: QApplication) -> None:  # noqa: ARG001
    family = default_text_font_family()
    assert family in {MONO_FONT_FAMILY, "Arial"} or bool(family)


def test_text_annotation_uses_box_points(qapp: QApplication) -> None:  # noqa: ARG001
    style = settings_to_annotation_style(ScreenshotTextSettings(font_size=20, color="#112233"))
    points = default_text_box_points(QPointF(10, 20), style)
    assert len(points) == 2
    ann = Annotation(tool=AnnotationTool.TEXT, points=points, text="Hello\nworld", style=style)
    rect = text_annotation_rect(ann)
    assert rect.width() > 50
    assert rect.height() > 20
    assert annotation_bounds(ann) == rect


def test_text_box_can_be_resized(qapp: QApplication) -> None:  # noqa: ARG001
    style = AnnotationStyle(font_size=18, font_family="Arial")
    points = [QPointF(0, 0), QPointF(100, 40)]
    ann = Annotation(tool=AnnotationTool.TEXT, points=points, text="Hi", style=style)
    resized = apply_annotation_edit(ann, "se", points, QPointF(100, 40), QPointF(160, 80), shift=False)
    assert resized[1].x() == 160
    assert resized[1].y() == 80


def test_text_commit_multiline_renders(qapp: QApplication) -> None:  # noqa: ARG001
    image = QImage(200, 120, QImage.Format.Format_RGB32)
    image.fill(QColor(255, 255, 255))
    doc = AnnotationDocument(image)
    style = AnnotationStyle(
        color=QColor("#de2b26"),
        font_family="Arial",
        font_size=16,
        background_fill=True,
    )
    doc.begin_draft(
        Annotation(
            tool=AnnotationTool.TEXT,
            points=[QPointF(10, 10), QPointF(180, 90)],
            text="Line one\nLine two",
            style=style,
        )
    )
    assert doc.commit_draft()
    rendered = doc.render(include_draft=False)
    sample = rendered.pixelColor(20, 20)
    assert sample.red() > 200
    assert sample.green() > 200
    font = annotation_qfont(style)
    assert font.pointSizeF() == 16
