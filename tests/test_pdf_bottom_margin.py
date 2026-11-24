"""Tests for PDF bottom-margin shrink helpers."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

from harrix_swiss_knife.actions.common.pdf_bottom_margin import (
    DEFAULT_BOTTOM_MARGIN_CM,
    bottom_margin_target_rect,
    cm_to_pt,
    default_output_path,
    shrink_pdf_for_bottom_margin,
)
from harrix_swiss_knife.actions.files.shrink_pdf_bottom_margin import OnShrinkPdfBottomMargin


def test_bottom_margin_target_rect_leaves_requested_band() -> None:
    width = 595.0
    height = 842.0
    margin = cm_to_pt(DEFAULT_BOTTOM_MARGIN_CM)
    rect = bottom_margin_target_rect(width, height)
    assert rect.y0 == pytest.approx(0.0)
    assert rect.y1 == pytest.approx(height - margin)
    assert rect.height == pytest.approx(height - margin)
    assert rect.width == pytest.approx(width * ((height - margin) / height))
    assert rect.x0 == pytest.approx((width - rect.width) / 2)
    assert height - rect.y1 == pytest.approx(margin)


def test_bottom_margin_target_rect_rejects_short_page() -> None:
    with pytest.raises(ValueError, match="not greater"):
        bottom_margin_target_rect(200, cm_to_pt(4), bottom_margin_cm=4)


def test_default_output_path_uses_margin_label(tmp_path: Path) -> None:
    source = tmp_path / "scan.pdf"
    assert default_output_path(source).name == "scan_bottom_4cm.pdf"
    assert default_output_path(source, bottom_margin_cm=3.5).name == "scan_bottom_3.5cm.pdf"


def test_on_shrink_pdf_bottom_margin_metadata() -> None:
    action = OnShrinkPdfBottomMargin()
    assert action.title == "Shrink PDF for bottom margin…"
    assert action.icon == "📄"


def test_shrink_pdf_for_bottom_margin_writes_scaled_pages(tmp_path: Path) -> None:
    source = tmp_path / "input.pdf"
    with pymupdf.open() as doc:
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 72), "Hello PDF")
        doc.save(source)

    result = shrink_pdf_for_bottom_margin(source)
    assert result.output.is_file()
    assert result.output.name == "input_bottom_4cm.pdf"
    assert result.page_count == 1
    assert result.scale == pytest.approx((842 - cm_to_pt(4)) / 842)

    with pymupdf.open(result.output) as out_doc:
        assert out_doc.page_count == 1
        page = out_doc[0]
        assert page.rect.width == pytest.approx(595)
        assert page.rect.height == pytest.approx(842)
        assert page.get_contents()
        blocks = page.get_text("blocks")
        assert blocks
        lowest = max(block[3] for block in blocks)
        assert lowest <= page.rect.height - cm_to_pt(4) + 2.0
