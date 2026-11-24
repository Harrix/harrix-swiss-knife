---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `shrink_pdf_bottom_margin.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnShrinkPdfBottomMargin`](#%EF%B8%8F-class-onshrinkpdfbottommargin)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnShrinkPdfBottomMargin`

```python
class OnShrinkPdfBottomMargin(ActionBase)
```

Shrink each PDF page proportionally and leave a 4 cm bottom field.

Keeps the original page size. Content is scaled down so a blank band of
4 cm remains at the bottom, and is centered horizontally.

<details>
<summary>Code:</summary>

```python
class OnShrinkPdfBottomMargin(ActionBase):

    icon = "📄"
    title = "Shrink PDF for bottom margin…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("shrinking PDF for bottom margin")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Ask for PDF files via drop dialog, then shrink pages in a worker thread."""
        start = str(self.config.get("path_articles") or Path.home())
        selected = self.dialogs.get_open_filenames(
            "Select PDF",
            start,
            "PDF files (*.pdf);;All files (*.*)",
        )
        if selected is None:
            return
        pdfs = [path for path in selected if path.suffix.casefold() == ".pdf"]
        if not pdfs:
            self.add_line("⚠️ No PDF files selected.")
            self.show_result()
            return
        self._sources = pdfs
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("shrinking PDF for bottom margin thread")
    def in_thread(self) -> list[PdfBottomMarginResult]:
        """Shrink selected PDF files in a background thread."""
        sources = getattr(self, "_sources", None)
        if not isinstance(sources, list) or not sources:
            msg = "No PDF selected"
            raise TypeError(msg)
        results: list[PdfBottomMarginResult] = []
        for source in sources:
            if not isinstance(source, Path):
                msg = "No PDF selected"
                raise TypeError(msg)
            self.add_line(f"🔵 Shrinking PDF for a {DEFAULT_BOTTOM_MARGIN_CM:g} cm bottom margin: {source}")
            results.append(shrink_pdf_for_bottom_margin(source, bottom_margin_cm=DEFAULT_BOTTOM_MARGIN_CM))
        return results

    @ActionBase.handle_exceptions("shrinking PDF for bottom margin thread completion")
    def thread_after(self, result: Any) -> None:
        """Report output paths and open the result dialog."""
        if not isinstance(result, list) or not result:
            self.add_line(str(result))
            self.show_result()
            return
        for item in result:
            if not isinstance(item, PdfBottomMarginResult):
                self.add_line(str(item))
                continue
            percent = item.scale * 100
            self.add_line(
                f"✅ Wrote {item.output} ({item.page_count} page(s), scale {percent:.1f}%, "
                f"bottom margin {item.bottom_margin_cm:g} cm).",
            )
        last = result[-1]
        if isinstance(last, PdfBottomMarginResult):
            if len(result) == 1:
                self.show_toast(f"Saved {last.output.name}")
            else:
                self.show_toast(f"Saved {len(result)} PDF files")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Ask for PDF files via drop dialog, then shrink pages in a worker thread.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        start = str(self.config.get("path_articles") or Path.home())
        selected = self.dialogs.get_open_filenames(
            "Select PDF",
            start,
            "PDF files (*.pdf);;All files (*.*)",
        )
        if selected is None:
            return
        pdfs = [path for path in selected if path.suffix.casefold() == ".pdf"]
        if not pdfs:
            self.add_line("⚠️ No PDF files selected.")
            self.show_result()
            return
        self._sources = pdfs
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> list[PdfBottomMarginResult]
```

Shrink selected PDF files in a background thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> list[PdfBottomMarginResult]:
        sources = getattr(self, "_sources", None)
        if not isinstance(sources, list) or not sources:
            msg = "No PDF selected"
            raise TypeError(msg)
        results: list[PdfBottomMarginResult] = []
        for source in sources:
            if not isinstance(source, Path):
                msg = "No PDF selected"
                raise TypeError(msg)
            self.add_line(f"🔵 Shrinking PDF for a {DEFAULT_BOTTOM_MARGIN_CM:g} cm bottom margin: {source}")
            results.append(shrink_pdf_for_bottom_margin(source, bottom_margin_cm=DEFAULT_BOTTOM_MARGIN_CM))
        return results
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Report output paths and open the result dialog.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        if not isinstance(result, list) or not result:
            self.add_line(str(result))
            self.show_result()
            return
        for item in result:
            if not isinstance(item, PdfBottomMarginResult):
                self.add_line(str(item))
                continue
            percent = item.scale * 100
            self.add_line(
                f"✅ Wrote {item.output} ({item.page_count} page(s), scale {percent:.1f}%, "
                f"bottom margin {item.bottom_margin_cm:g} cm).",
            )
        last = result[-1]
        if isinstance(last, PdfBottomMarginResult):
            if len(result) == 1:
                self.show_toast(f"Saved {last.output.name}")
            else:
                self.show_toast(f"Saved {len(result)} PDF files")
        self.show_result()
```

</details>
