---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `vector_render.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `render_icon_to_image`](#-function-render_icon_to_image)
- [🔧 Function `render_svg_to_image`](#-function-render_svg_to_image)
- [🔧 Function `render_vector_document_to_image`](#-function-render_vector_document_to_image)
- [🔧 Function `svg_needs_contrast_background`](#-function-svg_needs_contrast_background)

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
        icon_size = size - 2 * inset
        renderer.render(painter, QRectF(inset, inset, icon_size, icon_size))
    else:
        renderer.render(painter)
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
