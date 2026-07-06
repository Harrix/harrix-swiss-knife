---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `raster_optimize.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `optimize_raster_file`](#-function-optimize_raster_file)
- [🔧 Function `process_jpg_webp_to_avif`](#-function-process_jpg_webp_to_avif)
- [🔧 Function `process_png_compare`](#-function-process_png_compare)
- [🔧 Function `process_png_to_avif`](#-function-process_png_to_avif)

</details>

## 🔧 Function `optimize_raster_file`

```python
def optimize_raster_file(source: Path, output_folder: Path, project_root: Path) -> str
```

Optimize a PNG, JPG, or WEBP file using Pillow and ffmpeg.

Args:

- `source` (`Path`): Source image path.
- `output_folder` (`Path`): Destination folder.
- `project_root` (`Path`): Folder containing ffmpeg.exe.
- `quality` (`bool`): Use higher quality AVIF settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.
- `compare_png_avif` (`bool`): For PNG, compare optimized PNG vs AVIF. Defaults to `True`.

Returns:

- `str`: Status message.

<details>
<summary>Code:</summary>

```python
def optimize_raster_file(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
    compare_png_avif: bool = True,
    convert_png_to_avif: bool = False,
) -> str:
    output_folder.mkdir(parents=True, exist_ok=True)
    ext = source.suffix.lower()
    if ext == ".png":
        if compare_png_avif:
            return process_png_compare(source, output_folder, project_root, quality=quality, max_size=max_size)
        if convert_png_to_avif:
            return process_png_to_avif(source, output_folder, project_root, quality=quality, max_size=max_size)
        image = _load_and_resize(source, max_size)
        output_path = output_folder / f"{source.stem}.png"
        output_path.write_bytes(_encode_optimized_png(image))
        return f"✅ File {source.name} successfully optimized."
    if ext in _JPG_WEBP_EXTENSIONS:
        output_path = output_folder / f"{source.stem}.avif"
        return process_jpg_webp_to_avif(
            source,
            output_path,
            project_root,
            quality=quality,
            max_size=max_size,
        )
    msg = f"File {source.name} is not a supported raster format."
    raise ValueError(msg)
```

</details>

## 🔧 Function `process_jpg_webp_to_avif`

```python
def process_jpg_webp_to_avif(source: Path, output_path: Path, project_root: Path) -> str
```

Convert JPG or WEBP to AVIF using ffmpeg.

<details>
<summary>Code:</summary>

```python
def process_jpg_webp_to_avif(
    source: Path,
    output_path: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _convert_to_avif(source, output_path, project_root, quality=quality, max_size=max_size)
    return f"✅ File {source.name} successfully converted to AVIF."
```

</details>

## 🔧 Function `process_png_compare`

```python
def process_png_compare(source: Path, output_folder: Path, project_root: Path) -> str
```

Optimize PNG, compare with AVIF from ffmpeg, and keep the smaller file.

<details>
<summary>Code:</summary>

```python
def process_png_compare(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    output_folder.mkdir(parents=True, exist_ok=True)
    image = _load_and_resize(source, max_size)
    png_bytes = _encode_optimized_png(image)
    output_png = output_folder / f"{source.stem}.png"
    output_avif = output_folder / f"{source.stem}.avif"

    with tempfile.TemporaryDirectory(prefix="png_compare_") as temp_dir:
        temp_path = Path(temp_dir)
        temp_png = temp_path / "input.png"
        image.save(temp_png, format="PNG")
        temp_avif = temp_path / "output.avif"
        _convert_to_avif(temp_png, temp_avif, project_root, quality=quality, max_size=None)
        avif_size = temp_avif.stat().st_size
        avif_bytes = temp_avif.read_bytes()

    png_size = len(png_bytes)
    if png_size <= avif_size:
        output_png.write_bytes(png_bytes)
        return (
            f"✅ File {source.name} kept as PNG (smaller size): "
            f"PNG {(png_size / 1024):.2f} KB, AVIF {(avif_size / 1024):.2f} KB."
        )

    output_avif.write_bytes(avif_bytes)
    return (
        f"✅ File {source.name} converted to AVIF (smaller size): "
        f"PNG {(png_size / 1024):.2f} KB, AVIF {(avif_size / 1024):.2f} KB."
    )
```

</details>

## 🔧 Function `process_png_to_avif`

```python
def process_png_to_avif(source: Path, output_folder: Path, project_root: Path) -> str
```

Convert PNG to AVIF using ffmpeg.

<details>
<summary>Code:</summary>

```python
def process_png_to_avif(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
) -> str:
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"{source.stem}.avif"
    image = _load_and_resize(source, max_size)
    with tempfile.TemporaryDirectory(prefix="png_to_avif_") as temp_dir:
        temp_png = Path(temp_dir) / "input.png"
        image.save(temp_png, format="PNG")
        _convert_to_avif(temp_png, output_path, project_root, quality=quality, max_size=None)
    return f"✅ File {source.name} successfully converted to AVIF."
```

</details>
