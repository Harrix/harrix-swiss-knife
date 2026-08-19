---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `icon_assets.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `asset_candidates`](#-function-asset_candidates)
- [🔧 Function `find_app_ico`](#-function-find_app_ico)
- [🔧 Function `find_logo_svg`](#-function-find_logo_svg)
- [🔧 Function `header_logo_pixmap`](#-function-header_logo_pixmap)
- [🔧 Function `largest_image_from_ico`](#-function-largest_image_from_ico)
- [🔧 Function `make_window_icon`](#-function-make_window_icon)
- [🔧 Function `padded_image`](#-function-padded_image)
- [🔧 Function `source_logo_image`](#-function-source_logo_image)
- [🔧 Function `welcome_logo_pixmap`](#-function-welcome_logo_pixmap)
- [🔧 Function `write_padded_ico`](#-function-write_padded_ico)

</details>

## 🔧 Function `asset_candidates`

```python
def asset_candidates(*relative: str) -> list[Path]
```

Return search paths for a file under `harrix_swiss_knife/assets/`.

<details>
<summary>Code:</summary>

```python
def asset_candidates(*relative: str) -> list[Path]:
    name = Path(*relative)
    roots = [Path(__file__).resolve().parents[1] / "assets"]
    meipass = getattr(sys, "_MEIPASS", None)
    if isinstance(meipass, str):
        roots.append(Path(meipass) / "harrix_swiss_knife" / "assets")
    return [root / name for root in roots]
```

</details>

## 🔧 Function `find_app_ico`

```python
def find_app_ico() -> Path | None
```

Return `app.ico` if it exists.

<details>
<summary>Code:</summary>

```python
def find_app_ico() -> Path | None:
    for path in asset_candidates("app.ico"):
        if path.is_file():
            return path
    return None
```

</details>

## 🔧 Function `find_logo_svg`

```python
def find_logo_svg() -> Path | None
```

Return `logo.svg` if it exists.

<details>
<summary>Code:</summary>

```python
def find_logo_svg() -> Path | None:
    for path in asset_candidates("logo.svg"):
        if path.is_file():
            return path
    return None
```

</details>

## 🔧 Function `header_logo_pixmap`

```python
def header_logo_pixmap(size: int = _HEADER_LOGO_PX) -> QPixmap
```

Return a padded logo pixmap for the wizard header.

<details>
<summary>Code:</summary>

```python
def header_logo_pixmap(size: int = _HEADER_LOGO_PX) -> QPixmap:
    return welcome_logo_pixmap(size)
```

</details>

## 🔧 Function `largest_image_from_ico`

```python
def largest_image_from_ico(ico_path: Path) -> QImage
```

Decode the largest PNG (or any) frame from a multi-size ICO.

<details>
<summary>Code:</summary>

```python
def largest_image_from_ico(ico_path: Path) -> QImage:
    data = ico_path.read_bytes()
    png = _largest_png_frame(data)
    if png:
        image = QImage.fromData(png, _PNG_FORMAT)
        if not image.isNull():
            return image
    icon = QIcon(str(ico_path))
    sizes = icon.availableSizes()
    if sizes:
        best = max(sizes, key=lambda s: s.width() * s.height())
        pixmap = icon.pixmap(best)
        if not pixmap.isNull():
            return pixmap.toImage()
    image = QImage(str(ico_path))
    if image.isNull():
        msg = f"Could not decode icon: {ico_path}"
        raise RuntimeError(msg)
    return image
```

</details>

## 🔧 Function `make_window_icon`

```python
def make_window_icon() -> QIcon
```

Return a QIcon with padded full-resolution pixmaps so Windows does not pick a blurry small frame.

<details>
<summary>Code:</summary>

```python
def make_window_icon() -> QIcon:
    source = source_logo_image()
    if source.isNull():
        ico = find_app_ico()
        return QIcon(str(ico)) if ico is not None else QIcon()
    icon = QIcon()
    for size in _ICON_SIZES:
        icon.addPixmap(QPixmap.fromImage(padded_image(source, size)))
    return icon
```

</details>

## 🔧 Function `padded_image`

```python
def padded_image(source: QImage, size: int, *, pad_ratio: float = _PAD_RATIO) -> QImage
```

Scale `source` into a square canvas with transparent margins.

<details>
<summary>Code:</summary>

```python
def padded_image(source: QImage, size: int, *, pad_ratio: float = _PAD_RATIO) -> QImage:
    out = QImage(size, size, QImage.Format.Format_ARGB32)
    out.fill(Qt.GlobalColor.transparent)
    inner = max(1, int(size * (1 - 2 * pad_ratio)))
    scaled = source.scaled(
        inner,
        inner,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(x, y, scaled)
    painter.end()
    return out
```

</details>

## 🔧 Function `source_logo_image`

```python
def source_logo_image() -> QImage
```

Best available logo: SVG if present, else the largest ICO frame.

<details>
<summary>Code:</summary>

```python
def source_logo_image() -> QImage:
    svg = find_logo_svg()
    if svg is not None:
        image = _render_svg(svg, _ICO_256)
        if image is not None and not image.isNull():
            return image
    ico = find_app_ico()
    if ico is None:
        return QImage()
    return largest_image_from_ico(ico)
```

</details>

## 🔧 Function `welcome_logo_pixmap`

```python
def welcome_logo_pixmap(size: int = _WELCOME_LOGO_PX) -> QPixmap
```

Return a padded logo pixmap for the welcome page.

<details>
<summary>Code:</summary>

```python
def welcome_logo_pixmap(size: int = _WELCOME_LOGO_PX) -> QPixmap:
    source = source_logo_image()
    if source.isNull():
        return QPixmap()
    return QPixmap.fromImage(padded_image(source, size))
```

</details>

## 🔧 Function `write_padded_ico`

```python
def write_padded_ico(dest: Path) -> Path
```

Write a multi-size ICO with padding, generated from the largest source frame.

<details>
<summary>Code:</summary>

```python
def write_padded_ico(dest: Path) -> Path:
    source = source_logo_image()
    if source.isNull():
        ico = find_app_ico()
        if ico is None:
            msg = "No app.ico or logo.svg to build installer icon"
            raise FileNotFoundError(msg)
        dest.write_bytes(ico.read_bytes())
        return dest
    images = [padded_image(source, size) for size in _ICON_SIZES]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(_ico_from_png_images(images))
    return dest
```

</details>
