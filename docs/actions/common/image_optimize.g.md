---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_optimize.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OptimizeSizeStats`](#%EF%B8%8F-class-optimizesizestats)
  - [⚙️ Method `add`](#%EF%B8%8F-method-add)
  - [⚙️ Method `format_summary`](#%EF%B8%8F-method-format_summary)
- [🔧 Function `find_optimized_output`](#-function-find_optimized_output)
- [🔧 Function `format_byte_size`](#-function-format_byte_size)
- [🔧 Function `optimize_image_file`](#-function-optimize_image_file)
- [🔧 Function `optimize_images_in_folder`](#-function-optimize_images_in_folder)

</details>

## 🏛️ Class `OptimizeSizeStats`

```python
class OptimizeSizeStats
```

Accumulated before/after byte sizes for optimized images.

<details>
<summary>Code:</summary>

```python
class OptimizeSizeStats:

    before_bytes: int = 0
    after_bytes: int = 0
    count: int = 0

    def add(self, before: int, after: int) -> None:
        """Record one optimized image pair."""
        self.before_bytes += before
        self.after_bytes += after
        self.count += 1

    def format_summary(self) -> str:
        """Return a console summary line for total size change."""
        if self.count <= 0:
            return "📊 No images optimized for size summary."
        saved = self.before_bytes - self.after_bytes
        before_text = format_byte_size(self.before_bytes)
        after_text = format_byte_size(self.after_bytes)
        images_label = "image" if self.count == 1 else "images"
        if self.before_bytes > 0:
            percent = abs(saved) * 100 / self.before_bytes
            if saved >= 0:
                return (
                    f"📊 {self.count} {images_label}: {before_text} → {after_text} "
                    f"(saved {format_byte_size(saved)}, {percent:.1f}%)"
                )
            return (
                f"📊 {self.count} {images_label}: {before_text} → {after_text} "
                f"(grew by {format_byte_size(-saved)}, {percent:.1f}%)"
            )
        return f"📊 {self.count} {images_label}: {before_text} → {after_text}"
```

</details>

### ⚙️ Method `add`

```python
def add(self, before: int, after: int) -> None
```

Record one optimized image pair.

<details>
<summary>Code:</summary>

```python
def add(self, before: int, after: int) -> None:
        self.before_bytes += before
        self.after_bytes += after
        self.count += 1
```

</details>

### ⚙️ Method `format_summary`

```python
def format_summary(self) -> str
```

Return a console summary line for total size change.

<details>
<summary>Code:</summary>

```python
def format_summary(self) -> str:
        if self.count <= 0:
            return "📊 No images optimized for size summary."
        saved = self.before_bytes - self.after_bytes
        before_text = format_byte_size(self.before_bytes)
        after_text = format_byte_size(self.after_bytes)
        images_label = "image" if self.count == 1 else "images"
        if self.before_bytes > 0:
            percent = abs(saved) * 100 / self.before_bytes
            if saved >= 0:
                return (
                    f"📊 {self.count} {images_label}: {before_text} → {after_text} "
                    f"(saved {format_byte_size(saved)}, {percent:.1f}%)"
                )
            return (
                f"📊 {self.count} {images_label}: {before_text} → {after_text} "
                f"(grew by {format_byte_size(-saved)}, {percent:.1f}%)"
            )
        return f"📊 {self.count} {images_label}: {before_text} → {after_text}"
```

</details>

## 🔧 Function `find_optimized_output`

```python
def find_optimized_output(output_folder: Path, stem: str) -> Path | None
```

Return the optimized output file for `stem`, preferring AVIF when present.

<details>
<summary>Code:</summary>

```python
def find_optimized_output(output_folder: Path, stem: str) -> Path | None:
    for ext in _OUTPUT_EXTENSION_ORDER:
        candidate = output_folder / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None
```

</details>

## 🔧 Function `format_byte_size`

```python
def format_byte_size(num_bytes: int) -> str
```

Format a byte count as a short human-readable size.

<details>
<summary>Code:</summary>

```python
def format_byte_size(num_bytes: int) -> str:
    value = float(abs(num_bytes))
    for unit in ("B", "KB", "MB", "GB"):
        if value < _BYTES_PER_UNIT or unit == "GB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.2f} {unit}"
        value /= _BYTES_PER_UNIT
    return f"{value:.2f} GB"
```

</details>

## 🔧 Function `optimize_image_file`

```python
def optimize_image_file(source: Path, output_folder: Path, project_root: Path) -> str | None
```

Optimize a single supported image file.

<details>
<summary>Code:</summary>

```python
def optimize_image_file(
    source: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
    compare_png_avif: bool = True,
    convert_png_to_avif: bool = False,
) -> str | None:
    ext = source.suffix.lower()
    if ext == ".svg":
        return h.svg_opt.SvgOptimizer().optimize_file(source, output_folder / source.name)
    if ext in TOOL_EXTENSIONS:
        output_name = source.with_suffix(".avif").name if ext in {".gif", ".mp4"} else source.name
        return h.img.optimize_image_with_tools(
            source,
            output_folder / output_name,
            project_root=project_root,
            quality=quality,
            max_size=max_size,
        )
    if ext in RASTER_EXTENSIONS:
        return optimize_raster_file(
            source,
            output_folder,
            project_root,
            quality=quality,
            max_size=max_size,
            compare_png_avif=compare_png_avif,
            convert_png_to_avif=convert_png_to_avif,
        )
    return None
```

</details>

## 🔧 Function `optimize_images_in_folder`

```python
def optimize_images_in_folder(images_folder: Path, output_folder: Path, project_root: Path) -> str
```

Optimize all supported images in a folder.

Args:

- `images_folder` (`Path`): Source folder with images.
- `output_folder` (`Path`): Destination folder for optimized images.
- `project_root` (`Path`): Project root with `ffmpeg.exe`, `avifenc.exe`, `avifdec.exe`.
- `quality` (`bool`): Use higher quality settings. Defaults to `False`.
- `max_size` (`int | None`): Maximum width or height in pixels. Defaults to `None`.
- `compare_png_avif` (`bool`): For PNG, compare optimized PNG vs AVIF. Defaults to `True`.
- `convert_png_to_avif` (`bool`): For PNG, always convert to AVIF. Defaults to `False`.
- `clear_output` (`bool`): Clear output folder before processing. Defaults to `True`.
- `size_stats` (`OptimizeSizeStats | None`): Optional accumulator for before/after sizes.
  When omitted, a local summary is appended to the result. Defaults to `None`.

Returns:

- `str`: Newline-separated status messages.

<details>
<summary>Code:</summary>

```python
def optimize_images_in_folder(
    images_folder: Path,
    output_folder: Path,
    project_root: Path,
    *,
    quality: bool = False,
    max_size: int | None = None,
    compare_png_avif: bool = True,
    convert_png_to_avif: bool = False,
    clear_output: bool = True,
    size_stats: OptimizeSizeStats | None = None,
) -> str:
    lines: list[str] = []
    local_stats = size_stats if size_stats is not None else OptimizeSizeStats()
    if clear_output:
        if output_folder.exists():
            for item in output_folder.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        else:
            output_folder.mkdir(parents=True, exist_ok=True)
    else:
        output_folder.mkdir(parents=True, exist_ok=True)

    if not images_folder.exists():
        lines.append(f"❌ Images folder not found: {images_folder}")
        return "\n".join(lines)

    for file in sorted(images_folder.iterdir()):
        if not file.is_file():
            continue
        before_size = file.stat().st_size
        try:
            message = optimize_image_file(
                file,
                output_folder,
                project_root,
                quality=quality,
                max_size=max_size,
                compare_png_avif=compare_png_avif,
                convert_png_to_avif=convert_png_to_avif,
            )
        except (RuntimeError, ValueError) as error:
            lines.append(f"❌ Error while processing file {file.name}: {error}")
            continue
        if message:
            lines.append(message)
            output = find_optimized_output(output_folder, file.stem)
            if output is not None:
                local_stats.add(before_size, output.stat().st_size)

    if not lines:
        lines.append("🔵 No supported image files found.")
    elif size_stats is None and local_stats.count > 0:
        lines.append(local_stats.format_summary())

    return "\n".join(lines)
```

</details>
