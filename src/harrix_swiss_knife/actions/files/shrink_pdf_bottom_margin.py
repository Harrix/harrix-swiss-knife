"""Shrink PDF pages to leave a 4 cm bottom field."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.pdf_bottom_margin import (
    DEFAULT_BOTTOM_MARGIN_CM,
    PdfBottomMarginResult,
    shrink_pdf_for_bottom_margin,
)


class OnShrinkPdfBottomMargin(ActionBase):
    """Shrink each PDF page proportionally and leave a 4 cm bottom field.

    Keeps the original page size. Content is scaled down so a blank band of
    4 cm remains at the bottom, and is centered horizontally.

    """

    icon = "📄"
    title = "Shrink PDF for bottom margin…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("shrinking PDF for bottom margin")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Ask for a PDF, shrink pages in a worker thread, then show the result."""
        start = str(self.config.get("path_articles") or Path.home())
        selected = self.dialogs.get_open_filename(
            "Select PDF",
            start,
            "PDF files (*.pdf);;All files (*.*)",
        )
        if selected is None:
            return
        self._source = Path(selected)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("shrinking PDF for bottom margin thread")
    def in_thread(self) -> PdfBottomMarginResult:
        """Shrink the selected PDF in a background thread."""
        source = getattr(self, "_source", None)
        if not isinstance(source, Path):
            msg = "No PDF selected"
            raise TypeError(msg)
        self.add_line(f"🔵 Shrinking PDF for a {DEFAULT_BOTTOM_MARGIN_CM:g} cm bottom margin: {source}")
        return shrink_pdf_for_bottom_margin(source, bottom_margin_cm=DEFAULT_BOTTOM_MARGIN_CM)

    @ActionBase.handle_exceptions("shrinking PDF for bottom margin thread completion")
    def thread_after(self, result: Any) -> None:
        """Report the output path and open the result dialog."""
        if not isinstance(result, PdfBottomMarginResult):
            self.add_line(str(result))
            self.show_result()
            return
        percent = result.scale * 100
        self.add_line(
            f"✅ Wrote {result.output} ({result.page_count} page(s), scale {percent:.1f}%, "
            f"bottom margin {result.bottom_margin_cm:g} cm).",
        )
        self.show_toast(f"Saved {result.output.name}")
        self.show_result()
