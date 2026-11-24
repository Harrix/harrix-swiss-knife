---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pdf_bottom_margin.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PdfBottomMarginResult`](#%EF%B8%8F-class-pdfbottommarginresult)
- [🔧 Function `bottom_margin_target_rect`](#-function-bottom_margin_target_rect)
- [🔧 Function `cm_to_pt`](#-function-cm_to_pt)
- [🔧 Function `default_output_path`](#-function-default_output_path)
- [🔧 Function `shrink_pdf_for_bottom_margin`](#-function-shrink_pdf_for_bottom_margin)

</details>

## 🏛️ Class `PdfBottomMarginResult`

```python
class PdfBottomMarginResult
```

Outcome of writing a PDF with a bottom margin.

<details>
<summary>Code:</summary>

```python
class PdfBottomMarginResult:

    source: Path
    output: Path
    page_count: int
    bottom_margin_cm: float
    scale: float
```

</details>

## 🔧 Function `bottom_margin_target_rect`

```python
def bottom_margin_target_rect(page_width: float, page_height: float, *, bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM) -> pymupdf.Rect
```

Return the destination rect for proportionally shrunk page content.

The content keeps the page aspect ratio, is centered horizontally, and sits
above a bottom margin of `bottom_margin_cm`.

Raises:

- `ValueError`: When the page is not taller than the requested margin.

<details>
<summary>Code:</summary>

```python
def bottom_margin_target_rect(
    page_width: float,
    page_height: float,
    *,
    bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM,
) -> pymupdf.Rect:
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
    # PyMuPDF page coords: (0, 0) is top-left, y grows downward.
    x0 = (page_width - new_width) / 2
    y0 = 0.0
    return pymupdf.Rect(x0, y0, x0 + new_width, y0 + new_height)
```

</details>

## 🔧 Function `cm_to_pt`

```python
def cm_to_pt(centimeters: float) -> float
```

Convert centimeters to PDF points (1/72 inch).

<details>
<summary>Code:</summary>

```python
def cm_to_pt(centimeters: float) -> float:
    return centimeters * _PT_PER_CM
```

</details>

## 🔧 Function `default_output_path`

```python
def default_output_path(source: Path, *, bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM) -> Path
```

Return `name_bottom_Ncm.pdf` next to `source`.

<details>
<summary>Code:</summary>

```python
def default_output_path(source: Path, *, bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM) -> Path:
    label = _margin_label(bottom_margin_cm)
    return source.with_name(f"{source.stem}_bottom_{label}{source.suffix}")
```

</details>

## 🔧 Function `shrink_pdf_for_bottom_margin`

```python
def shrink_pdf_for_bottom_margin(source: Path, output: Path | None = None, *, bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM) -> PdfBottomMarginResult
```

Write a PDF whose pages keep size but leave `bottom_margin_cm` empty at the bottom.

Each page is drawn scaled down proportionally into the area above the
margin and centered horizontally.

Raises:

- `FileNotFoundError`: When `source` is missing.
- `ValueError`: When the file is not a PDF or a page is too short for the margin.
- `OSError`: When the output cannot be written.

<details>
<summary>Code:</summary>

```python
def shrink_pdf_for_bottom_margin(
    source: Path,
    output: Path | None = None,
    *,
    bottom_margin_cm: float = DEFAULT_BOTTOM_MARGIN_CM,
) -> PdfBottomMarginResult:
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
```

</details>
