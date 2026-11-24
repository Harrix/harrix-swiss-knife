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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Ask for a PDF, shrink pages in a worker thread, then show the result.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
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
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> PdfBottomMarginResult
```

Shrink the selected PDF in a background thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> PdfBottomMarginResult:
        source = getattr(self, "_source", None)
        if not isinstance(source, Path):
            msg = "No PDF selected"
            raise TypeError(msg)
        self.add_line(f"🔵 Shrinking PDF for a {DEFAULT_BOTTOM_MARGIN_CM:g} cm bottom margin: {source}")
        return shrink_pdf_for_bottom_margin(source, bottom_margin_cm=DEFAULT_BOTTOM_MARGIN_CM)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Report the output path and open the result dialog.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
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
```

</details>
