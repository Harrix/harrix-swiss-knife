---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `vector_render.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `fitted_content_rect`](#-function-fitted_content_rect)
- [🔧 Function `render_icon_to_image`](#-function-render_icon_to_image)
- [🔧 Function `render_svg_to_image`](#-function-render_svg_to_image)
- [🔧 Function `render_vector_document_to_image`](#-function-render_vector_document_to_image)
- [🔧 Function `svg_needs_contrast_background`](#-function-svg_needs_contrast_background)

</details>

## 🔧 Function `fitted_content_rect`

```python
def fitted_content_rect(renderer: QSvgRenderer, bounds: QRectF) -> QRectF
```

Return a centered rect inside `bounds` that keeps the SVG aspect ratio.

<details>
<summary>Code:</summary>

```python
def fitted_content_rect(renderer: QSvgRenderer, bounds: QRectF) -> QRectF:
    view = renderer.viewBoxF()
    if view.width() > 0 and view.height() > 0:
        content_w, content_h = view.width(), view.height()
    else:
        default = renderer.defaultSize()
        content_w, content_h = float(default.width()), float(default.height())
    if content_w <= 0 or content_h <= 0:
        return QRectF(bounds)
    scale = min(bounds.width() / content_w, bounds.height() / content_h)
    draw_w = content_w * scale
    draw_h = content_h * scale
    x = bounds.x() + (bounds.width() - draw_w) / 2
    y = bounds.y() + (bounds.height() - draw_h) / 2
    return QRectF(x, y, draw_w, draw_h)
```

</details>

## 🔧 Function `render_icon_to_image`

```python
def render_icon_to_image(path: Path, size: int) -> QImage | None
```

Rasterize an icon file into a square ARGB image.

Dispatch:

- `.svg` → Qt SVG renderer
- `.ai` / `.pdf` / `.eps` → PyMuPDF, then pypdf `/Thumb`, then Ghostscript

<details>
<summary>Code:</summary>

```python
def render_icon_to_image(path: Path, size: int) -> QImage | None:
    if not path.is_file() or size <= 0:
        return None
    suffix = path.suffix.casefold()
    if suffix in _SVG_SUFFIXES:
        return render_svg_to_image(path, size)
    if suffix in _VECTOR_SUFFIXES:
        return render_vector_document_to_image(path, size)
    return None
```

</details>

## 🔧 Function `render_svg_to_image`

```python
def render_svg_to_image(svg_path: Path, size: int) -> QImage | None
```

Rasterize an SVG into a square image.

Non-square SVGs keep their aspect ratio and are centered (letterboxed).
White variants (`*_white_*`) get a rounded gray backdrop so they stay visible.
The icon itself is inset so it does not touch the gray tile edges.

<details>
<summary>Code:</summary>

```python
def render_svg_to_image(svg_path: Path, size: int) -> QImage | None:
    if not svg_path.is_file():
        return None
    renderer = QSvgRenderer(str(svg_path))
    if not renderer.isValid():
        return None
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    if svg_needs_contrast_background(svg_path):
        _paint_rounded_preview_background(painter, size)
        inset = max(2.0, size * PREVIEW_ICON_INSET_RATIO)
        bounds = QRectF(inset, inset, size - 2 * inset, size - 2 * inset)
    else:
        bounds = QRectF(0, 0, size, size)
    renderer.render(painter, fitted_content_rect(renderer, bounds))
    painter.end()
    return image
```

</details>

## 🔧 Function `render_vector_document_to_image`

```python
def render_vector_document_to_image(path: Path, size: int) -> QImage | None
```

Render AI/PDF/EPS via PyMuPDF, embedded thumb, or Ghostscript.

<details>
<summary>Code:</summary>

```python
def render_vector_document_to_image(path: Path, size: int) -> QImage | None:
    image = _render_with_pymupdf(path, size)
    if image is not None:
        return image
    image = _render_with_pypdf_thumb(path, size)
    if image is not None:
        return image
    return _render_with_ghostscript(path, size)
```

</details>

## 🔧 Function `svg_needs_contrast_background`

```python
def svg_needs_contrast_background(svg_path: Path) -> bool
```

Return whether the SVG is a white-fill variant that needs a gray tile.

<details>
<summary>Code:</summary>

```python
def svg_needs_contrast_background(svg_path: Path) -> bool:
    return "_white" in svg_path.stem.casefold()
```

</details>
