---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ocr_markdown.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `combine_markdown_sections`](#-function-combine_markdown_sections)
- [🔧 Function `default_markdown_base`](#-function-default_markdown_base)
- [🔧 Function `format_ocr_body`](#-function-format_ocr_body)
- [🔧 Function `image_link_path`](#-function-image_link_path)
- [🔧 Function `ocr_image`](#-function-ocr_image)
- [🔧 Function `ocr_text_to_markdown`](#-function-ocr_text_to_markdown)
- [🔧 Function `ocr_text_to_markdown_section`](#-function-ocr_text_to_markdown_section)
- [🔧 Function `save_ocr_markdown_with_images`](#-function-save_ocr_markdown_with_images)
- [🔧 Function `suggest_markdown_filename`](#-function-suggest_markdown_filename)
- [🔧 Function `title_from_image_path`](#-function-title_from_image_path)

</details>

## 🔧 Function `combine_markdown_sections`

```python
def combine_markdown_sections(sections: list[str]) -> str
```

Join per-image Markdown sections with horizontal rules.

<details>
<summary>Code:</summary>

```python
def combine_markdown_sections(sections: list[str]) -> str:
    return "\n\n---\n\n".join(section.strip() for section in sections)
```

</details>

## 🔧 Function `default_markdown_base`

```python
def default_markdown_base(images: list[Path]) -> Path
```

Pick a folder for relative image links (e.g. year folder when images live in `img/`).

<details>
<summary>Code:</summary>

```python
def default_markdown_base(images: list[Path]) -> Path:
    if not images:
        msg = "images must not be empty"
        raise ValueError(msg)

    parents = {p.parent for p in images}
    if len(parents) == 1:
        parent = next(iter(parents))
        if parent.name == "img":
            return parent.parent
        return parent

    common = Path(os.path.commonpath([str(p.parent) for p in images]))
    if common.name == "img":
        return common.parent
    return common
```

</details>

## 🔧 Function `format_ocr_body`

```python
def format_ocr_body(text: str) -> str
```

Normalize OCR paragraphs for Markdown body text.

<details>
<summary>Code:</summary>

```python
def format_ocr_body(text: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n") if paragraph.strip()]
    return "\n\n".join(paragraphs)
```

</details>

## 🔧 Function `image_link_path`

```python
def image_link_path(image_path: Path, base_folder: Path) -> str
```

Return a POSIX relative path for a Markdown image link under `img/` when needed.

<details>
<summary>Code:</summary>

```python
def image_link_path(image_path: Path, base_folder: Path) -> str:
    try:
        relative = image_path.relative_to(base_folder).as_posix()
    except ValueError:
        return f"img/{image_path.name}"

    if relative.startswith("img/"):
        return relative
    return f"img/{image_path.name}"
```

</details>

## 🔧 Function `ocr_image`

```python
def ocr_image(path: Path, reader: easyocr.Reader) -> str
```

Run EasyOCR on one image file and return paragraph-joined text.

<details>
<summary>Code:</summary>

```python
def ocr_image(path: Path, reader: easyocr.Reader) -> str:
    with Image.open(path) as img:
        rgb = img.convert("RGB") if img.mode != "RGB" else img
        arr = np.array(rgb)
    # EasyOCR sets pin_memory=True even with gpu=False; torch warns on CPU-only hosts.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=r".*pin_memory.*", category=UserWarning)
        lines = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(lines)
```

</details>

## 🔧 Function `ocr_text_to_markdown`

```python
def ocr_text_to_markdown(ocr_text: str) -> str
```

Format recognized text as Markdown body (no filename heading or image embed).

<details>
<summary>Code:</summary>

```python
def ocr_text_to_markdown(ocr_text: str) -> str:
    body = format_ocr_body(ocr_text)
    return body or "_No text recognized._"
```

</details>

## 🔧 Function `ocr_text_to_markdown_section`

```python
def ocr_text_to_markdown_section(ocr_text: str, image_path: Path | None = None, base_folder: Path | None = None) -> str
```

Format recognized text as Markdown body.

`image_path` and `base_folder` are ignored; kept for existing callers.

<details>
<summary>Code:</summary>

```python
def ocr_text_to_markdown_section(ocr_text: str, image_path: Path | None = None, base_folder: Path | None = None) -> str:
    del image_path, base_folder
    return ocr_text_to_markdown(ocr_text)
```

</details>

## 🔧 Function `save_ocr_markdown_with_images`

```python
def save_ocr_markdown_with_images(save_path: Path, image_paths: list[Path], ocr_texts: list[str]) -> tuple[Path, list[Path]]
```

Save a named note folder: `stem/stem.md` and `stem/img/` images.

`save_path` is the path from the save dialog (`…/stem.md`). Creates::

    parent/stem/
      `stem.md`
      img/
        …

Returns `(note_dir, saved_image_paths)`.

<details>
<summary>Code:</summary>

```python
def save_ocr_markdown_with_images(
    save_path: Path,
    image_paths: list[Path],
    ocr_texts: list[str],
) -> tuple[Path, list[Path]]:
    if len(image_paths) != len(ocr_texts):
        msg = "image_paths and ocr_texts must have the same length"
        raise ValueError(msg)

    chosen = Path(save_path)
    stem = chosen.stem
    note_dir = chosen.parent / stem
    markdown_path = note_dir / f"{stem}.md"
    img_dir = note_dir / "img"
    note_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    saved_images: list[Path] = []
    for image_path in image_paths:
        source = Path(image_path)
        dest = _unique_image_dest(img_dir, source.name, source)
        if dest.resolve() != source.resolve():
            shutil.copy2(source, dest)
        saved_images.append(dest)

    sections = [
        ocr_text_to_markdown_section(text, image, note_dir) for text, image in zip(ocr_texts, saved_images, strict=True)
    ]
    markdown = combine_markdown_sections(sections).strip() + "\n"
    markdown_path.write_text(markdown, encoding="utf-8")
    return note_dir, saved_images
```

</details>

## 🔧 Function `suggest_markdown_filename`

```python
def suggest_markdown_filename(images: list[Path]) -> str
```

Suggest a default `.md` filename for OCR output.

<details>
<summary>Code:</summary>

```python
def suggest_markdown_filename(images: list[Path]) -> str:
    if len(images) == 1:
        return f"{title_from_image_path(images[0])}.md"
    return "ocr-scans.md"
```

</details>

## 🔧 Function `title_from_image_path`

```python
def title_from_image_path(path: Path) -> str
```

Return `YYYY-MM-DD` from the filename when present, else the stem.

<details>
<summary>Code:</summary>

```python
def title_from_image_path(path: Path) -> str:
    match = _DATE_IN_NAME.search(path.stem)
    return match.group(1) if match else path.stem
```

</details>
