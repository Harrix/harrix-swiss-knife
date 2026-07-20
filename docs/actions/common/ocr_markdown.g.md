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
- [🔧 Function `ocr_text_to_markdown_section`](#-function-ocr_text_to_markdown_section)
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

Return a POSIX relative path for a Markdown image link.

<details>
<summary>Code:</summary>

```python
def image_link_path(image_path: Path, base_folder: Path) -> str:
    try:
        return image_path.relative_to(base_folder).as_posix()
    except ValueError:
        return image_path.name
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
    lines = reader.readtext(arr, detail=0, paragraph=True)
    return "\n".join(lines)
```

</details>

## 🔧 Function `ocr_text_to_markdown_section`

```python
def ocr_text_to_markdown_section(ocr_text: str, image_path: Path, base_folder: Path) -> str
```

Build one Markdown section: heading, image embed, and recognized text.

<details>
<summary>Code:</summary>

```python
def ocr_text_to_markdown_section(ocr_text: str, image_path: Path, base_folder: Path) -> str:
    title = title_from_image_path(image_path)
    link = image_link_path(image_path, base_folder)
    alt = image_path.stem
    body = format_ocr_body(ocr_text)
    if not body:
        body = "_No text recognized._"
    return f"# {title}\n\n![{alt}]({link})\n\n{body}\n"
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
