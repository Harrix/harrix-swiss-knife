---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `md_image_optimize.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `optimize_image_file`](#-function-optimize_image_file)
- [🔧 Function `optimize_images_in_md_file`](#-function-optimize_images_in_md_file)
- [🔧 Function `optimize_single_image_for_template`](#-function-optimize_single_image_for_template)
- [🔧 Function `process_markdown_image_line`](#-function-process_markdown_image_line)
- [🔧 Function `transform_markdown_content`](#-function-transform_markdown_content)
- [🔧 Function `_determine_new_extension`](#-function-_determine_new_extension)
- [🔧 Function `_resolve_md_dir`](#-function-_resolve_md_dir)
- [🔧 Function `_run_npm_optimize`](#-function-_run_npm_optimize)

</details>

## 🔧 Function `optimize_image_file`

```python
def optimize_image_file(image_filename: Path) -> tuple[Path, str] | None
```

Optimize a local image file and copy it to the target location.

Returns:

- `tuple[Path, str] | None`: New absolute path and relative markdown path, or
  `None` when optimisation did not produce output.

<details>
<summary>Code:</summary>

```python
def optimize_image_file(
    image_filename: Path,
    *,
    md_dir: Path,
    image_path: str,
    image_folder: str = "img",
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> tuple[Path, str] | None:
    ext = image_filename.suffix.lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        return None

    with TemporaryDirectory() as temp_folder:
        temp_folder_path = Path(temp_folder)
        temp_image_filename = temp_folder_path / image_filename.name
        shutil.copy(image_filename, temp_image_filename)

        optimized_images_dir = _run_npm_optimize(
            temp_folder,
            ext=ext,
            is_convert_png_to_avif=is_convert_png_to_avif,
            is_compare_png_avif_sizes=is_compare_png_avif_sizes,
            max_size=max_size,
        )

        new_ext = _determine_new_extension(
            ext,
            optimized_images_dir=optimized_images_dir,
            image_stem=image_filename.stem,
            is_convert_png_to_avif=is_convert_png_to_avif,
            is_compare_png_avif_sizes=is_compare_png_avif_sizes,
        )
        optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"
        if not optimized_image.exists():
            return None

        if Path(image_path).is_absolute():
            new_image_path = image_filename.with_suffix(new_ext)
            new_image_rel_path = str(new_image_path)
        else:
            img_folder_path = md_dir / image_folder
            img_folder_path.mkdir(exist_ok=True)
            new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
            new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

        if image_filename.exists():
            image_filename.unlink()
        shutil.copy(optimized_image, new_image_path)
        return new_image_path, new_image_rel_path
```

</details>

## 🔧 Function `optimize_images_in_md_file`

```python
def optimize_images_in_md_file(filename: Path | str) -> str
```

Optimise images in a Markdown file and write changes when content differs.

<details>
<summary>Code:</summary>

```python
def optimize_images_in_md_file(
    filename: Path | str,
    *,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
    filter_names: set[str] | None = None,
) -> str:
    path = Path(filename)
    document = path.read_text(encoding="utf-8")
    document_new = transform_markdown_content(
        document,
        path.parent,
        filter_names=filter_names,
        is_convert_png_to_avif=is_convert_png_to_avif,
        is_compare_png_avif_sizes=is_compare_png_avif_sizes,
        max_size=max_size,
    )
    if document != document_new:
        path.write_text(document_new, encoding="utf-8")
        return f"✅ File {path} applied."
    return "File is not changed."
```

</details>

## 🔧 Function `optimize_single_image_for_template`

```python
def optimize_single_image_for_template(image_path: str, image_save_dir: Path, max_size: int | None = None, image_folder: str = "img") -> str
```

Optimise one image for template workflows and return the new relative path.

<details>
<summary>Code:</summary>

```python
def optimize_single_image_for_template(
    image_path: str,
    image_save_dir: Path,
    max_size: int | None = None,
    image_folder: str = "img",
) -> str:
    image_filename = Path(image_path) if Path(image_path).is_absolute() else (image_save_dir / image_path)
    if not image_filename.exists():
        return image_path

    result = optimize_image_file(
        image_filename,
        md_dir=image_save_dir,
        image_path=image_path,
        image_folder=image_folder,
        is_compare_png_avif_sizes=True,
        max_size=max_size,
    )
    if result is None:
        return image_path

    _new_image_path, new_image_rel_path = result
    return new_image_rel_path.replace("\\", "/")
```

</details>

## 🔧 Function `process_markdown_image_line`

```python
def process_markdown_image_line(markdown_line: str, path_md: Path | str) -> str
```

Process a single Markdown line and optimise any matching local image reference.

<details>
<summary>Code:</summary>

```python
def process_markdown_image_line(
    markdown_line: str,
    path_md: Path | str,
    *,
    filter_names: set[str] | None = None,
    image_folder: str = "img",
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> str:
    if REMOTE_IMAGE_PATTERN.search(markdown_line.strip()):
        return markdown_line

    local_match = LOCAL_IMAGE_PATTERN.search(markdown_line.strip())
    if not local_match:
        return markdown_line

    alt_text = local_match.group(1)
    image_path = local_match.group(2)
    if image_path.startswith("http"):
        return markdown_line

    md_dir = _resolve_md_dir(path_md)
    image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path
    if not image_filename.exists():
        return markdown_line
    if filter_names is not None and image_filename.name not in filter_names:
        return markdown_line

    result = optimize_image_file(
        image_filename,
        md_dir=md_dir,
        image_path=image_path,
        image_folder=image_folder,
        is_convert_png_to_avif=is_convert_png_to_avif,
        is_compare_png_avif_sizes=is_compare_png_avif_sizes,
        max_size=max_size,
    )
    if result is None:
        return markdown_line

    _new_image_path, new_image_rel_path = result
    return f"![{alt_text}]({new_image_rel_path})"
```

</details>

## 🔧 Function `transform_markdown_content`

```python
def transform_markdown_content(markdown_text: str, path_md: Path | str) -> str
```

Optimise local images referenced in Markdown content, preserving YAML and code blocks.

<details>
<summary>Code:</summary>

```python
def transform_markdown_content(
    markdown_text: str,
    path_md: Path | str,
    *,
    filter_names: set[str] | None = None,
    image_folder: str = "img",
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> str:
    yaml_md, content_md = h.md.split_yaml_content(markdown_text)

    new_lines = []
    lines = content_md.split("\n")
    for line_content, is_code_block in h.md.identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line_content)
            continue
        new_lines.append(
            process_markdown_image_line(
                line_content,
                path_md,
                filter_names=filter_names,
                image_folder=image_folder,
                is_convert_png_to_avif=is_convert_png_to_avif,
                is_compare_png_avif_sizes=is_compare_png_avif_sizes,
                max_size=max_size,
            )
        )
    content_md = "\n".join(new_lines)
    return yaml_md + "\n\n" + content_md
```

</details>

## 🔧 Function `_determine_new_extension`

```python
def _determine_new_extension(ext: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _determine_new_extension(
    ext: str,
    *,
    optimized_images_dir: Path,
    image_stem: str,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
) -> str:
    new_ext = ext
    if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"] or (
        ext == ".png"
        and (
            (is_compare_png_avif_sizes and (optimized_images_dir / f"{image_stem}.avif").exists())
            or is_convert_png_to_avif
        )
    ):
        new_ext = ".avif"
    return new_ext
```

</details>

## 🔧 Function `_resolve_md_dir`

```python
def _resolve_md_dir(path_md: Path | str) -> Path
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _resolve_md_dir(path_md: Path | str) -> Path:
    path = Path(path_md) if isinstance(path_md, str) else path_md
    return path.parent if path.is_file() else path
```

</details>

## 🔧 Function `_run_npm_optimize`

```python
def _run_npm_optimize(temp_folder: str) -> Path
```

Run npm optimize in a temporary folder and return the output directory.

<details>
<summary>Code:</summary>

```python
def _run_npm_optimize(
    temp_folder: str,
    *,
    ext: str,
    is_convert_png_to_avif: bool = False,
    is_compare_png_avif_sizes: bool = False,
    max_size: int | None = None,
) -> Path:
    commands = f'npm run optimize imagesFolder="{temp_folder}"'
    if is_compare_png_avif_sizes and ext == ".png":
        commands += " convertPngToAvif=compare"
    elif is_convert_png_to_avif and ext == ".png":
        commands += " convertPngToAvif=true"
    if max_size is not None:
        commands += f" maxSize={max_size}"
    h.dev.run_command(commands)
    return Path(temp_folder) / "temp"
```

</details>
