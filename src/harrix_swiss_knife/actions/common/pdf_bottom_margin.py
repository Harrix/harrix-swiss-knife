"""Shrink PDF page content to leave a fixed bottom margin."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path  # noqa: TC003

import pymupdf

DEFAULT_BOTTOM_MARGIN_CM = 4.0
_PT_PER_CM = 72 / 2.54


@dataclass(frozen=True, slots=True)
class PdfBottomMarginResult:
    """Outcome of writing a PDF with a bottom margin."""

    source: Path
    output: Path
    page_count: int
    bottom_margin_cm: float
    scale: float


def bottom_margin_target_rect(
    page_width: float,
    page_height: float,
    *,
    bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM,
) -> pymupdf.Rect:
    """Return the destination rect for proportionally shrunk page content.

    The content keeps the page aspect ratio, is centered horizontally, and sits
    above a bottom margin of `bottom_margin_cm`.

    Raises:

    - `ValueError`: When the page is not taller than the requested margin.

    """
    margin_pt = cm_to_pt(bottom_margin_cm)
    if page_height <= margin_pt:
        msg = f"Page height {page_height:.2f} pt is not greater than bottom margin {margin_pt:.2f} pt"
        raise ValueError(msg)
    if page_width <= 0 or page_height <= 0:
        msg = f"Invalid page size: {page_width} x {page_height}"
        raise ValueError(msg)

    scale = (page_height - margin_pt) / page_height
    new_width = page_width * scale
    new_height = page_height * scale
    x0 = (page_width - new_width) / 2
    y0 = margin_pt
    return pymupdf.Rect(x0, y0, x0 + new_width, y0 + new_height)


def cm_to_pt(centimeters: float) -> float:
    """Convert centimeters to PDF points (1/72 inch)."""
    return centimeters * _PT_PER_CM


def default_output_path(source: Path, *, bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM) -> Path:
    """Return `name_bottom_Ncm.pdf` next to `source`."""
    label = _margin_label(bottom_margin_cm)
    return source.with_name(f"{source.stem}_bottom_{label}{source.suffix}")


def shrink_pdf_for_bottom_margin(
    source: Path,
    output: Path | None = None,
    *,
    bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM,
) -> PdfBottomMarginResult:
    """Write a PDF whose pages keep size but leave `bottom_margin_cm` empty at the bottom.

    Each page is drawn scaled down proportionally into the area above the
    margin and centered horizontally.

    Raises:

    - `FileNotFoundError`: When `source` is missing.
    - `ValueError`: When the file is not a PDF or a page is too short for the margin.
    - `OSError`: When the output cannot be written.

    """
    src = source.expanduser().resolve()
    if not src.is_file():
        msg = f"PDF not found: {src}"
        raise FileNotFoundError(msg)
    if src.suffix.casefold() != ".pdf":
        msg = f"Not a PDF file: {src}"
        raise ValueError(msg)

    out = (output or default_output_path(src, bottom_margin_cm=bottom_margin_cm)).expanduser().resolve()
    if out == src:
        msg = "Output path must differ from the source PDF"
        raise ValueError(msg)

    scale = 0.0
    with pymupdf.open(src) as src_doc:
        if src_doc.page_count < 1:
            msg = f"PDF has no pages: {src}"
            raise ValueError(msg)
        with pymupdf.open() as out_doc:
            for page_index in range(src_doc.page_count):
                page = src_doc[page_index]
                rect = page.rect
                target = bottom_margin_target_rect(
                    rect.width,
                    rect.height,
                    bottom_margin_cm=bottom_margin_cm,
                )
                scale = (rect.height - cm_to_pt(bottom_margin_cm)) / rect.height
                new_page = out_doc.new_page(width=rect.width, height=rect.height)
                new_page.show_pdf_page(target, src_doc, page_index, keep_proportion=True)
            out.parent.mkdir(parents=True, exist_ok=True)
            out_doc.save(out, garbage=4, deflate=True)
            page_count = out_doc.page_count

    return PdfBottomMarginResult(
        source=src,
        output=out,
        page_count=page_count,
        bottom_margin_cm=bottom_margin_cm,
        scale=scale,
    )


def _margin_label(bottom_margin_cm: float) -> str:
    if float(bottom_margin_cm).is_integer():
        return f"{int(bottom_margin_cm)}cm"
    text = f"{bottom_margin_cm:.2f}".rstrip("0").rstrip(".")
    return f"{text}cm"
