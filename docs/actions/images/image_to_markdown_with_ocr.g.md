---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_to_markdown_with_ocr.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnImageToMarkdownWithOcr`](#️-class-onimagetomarkdownwithocr)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after_markdown`](#️-method-thread_after_markdown)

</details>

## 🏛️ Class `OnImageToMarkdownWithOcr`

```python
class OnImageToMarkdownWithOcr(ActionBase)
```

OCR selected images (ru/en) and build Markdown with headings and image links.

<details>
<summary>Code:</summary>

```python
class OnImageToMarkdownWithOcr(ActionBase):

    icon = "🔤"
    title = "Image to Markdown (OCR, local)…"
    bold_title = False

    _IMAGE_FILTER = "Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.avif *.tif *.tiff);;All Files (*)"
    _PREVIEW_MAX_LEN = 120

    @ActionBase.handle_exceptions("image to Markdown OCR")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Select images, run OCR in a background thread, and show Markdown output."""
        selected = self.dialogs.get_open_filenames(
            "Select scan images",
            self.config["path_articles"],
            self._IMAGE_FILTER,
        )
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self._markdown_base = default_markdown_base(self._image_paths)
        self._markdown_result = ""
        self.start_thread(self.in_thread, self.thread_after_markdown, self.title)

    @ActionBase.handle_exceptions("image to Markdown OCR thread")
    def in_thread(self) -> str | None:
        """Run EasyOCR on each selected image and assemble Markdown sections."""
        try:
            import easyocr  # noqa: PLC0415
        except ImportError:
            self.add_line("❌ easyocr is not installed. Run `uv sync` after updating dependencies.")
            return None

        reader = self._create_reader(easyocr)
        sections: list[str] = []
        total = len(self._image_paths)

        for index, path in enumerate(self._image_paths, 1):
            self.add_line(f"🔵 [{index}/{total}] {path.name}")
            text = ocr_image(path, reader)
            section = ocr_text_to_markdown_section(text, path, self._markdown_base)
            sections.append(section)
            preview = text.strip().replace("\n", " ")
            if len(preview) > self._PREVIEW_MAX_LEN:
                preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
            self.add_line(f"📝 {preview or '(no text recognized)'}")

        self._markdown_result = combine_markdown_sections(sections)
        return f"✅ Recognized text in {len(sections)} image(s)"

    @ActionBase.handle_exceptions("image to Markdown OCR completion")
    def thread_after_markdown(self, result: Any) -> None:
        """Show Markdown in a dialog, copy to clipboard, and offer to save a ``.md`` file."""
        if result:
            self.show_toast(result)

        markdown = self._markdown_result.strip()
        if not markdown:
            self.show_result()
            return

        self.text_to_clipboard(markdown)
        self.add_line("📋 Markdown copied to clipboard")
        self.dialogs.show_text_multiline(markdown, title="Image OCR → Markdown")

        default_name = suggest_markdown_filename(self._image_paths)
        save_path = self.dialogs.get_save_filename(
            "Save Markdown",
            str(self._markdown_base / default_name),
            "Markdown Files (*.md);;All Files (*)",
        )
        if save_path is not None:
            save_path.write_text(markdown + "\n", encoding="utf-8")
            self.add_line(f"💾 Saved: {save_path}")

        self.show_result()

    @staticmethod
    def _create_reader(easyocr_module: Any) -> easyocr.Reader:
        return easyocr_module.Reader(["ru", "en"], gpu=False, verbose=False)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Select images, run OCR in a background thread, and show Markdown output.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        selected = self.dialogs.get_open_filenames(
            "Select scan images",
            self.config["path_articles"],
            self._IMAGE_FILTER,
        )
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self._markdown_base = default_markdown_base(self._image_paths)
        self._markdown_result = ""
        self.start_thread(self.in_thread, self.thread_after_markdown, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Run EasyOCR on each selected image and assemble Markdown sections.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        try:
            import easyocr  # noqa: PLC0415
        except ImportError:
            self.add_line("❌ easyocr is not installed. Run `uv sync` after updating dependencies.")
            return None

        reader = self._create_reader(easyocr)
        sections: list[str] = []
        total = len(self._image_paths)

        for index, path in enumerate(self._image_paths, 1):
            self.add_line(f"🔵 [{index}/{total}] {path.name}")
            text = ocr_image(path, reader)
            section = ocr_text_to_markdown_section(text, path, self._markdown_base)
            sections.append(section)
            preview = text.strip().replace("\n", " ")
            if len(preview) > self._PREVIEW_MAX_LEN:
                preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
            self.add_line(f"📝 {preview or '(no text recognized)'}")

        self._markdown_result = combine_markdown_sections(sections)
        return f"✅ Recognized text in {len(sections)} image(s)"
```

</details>

### ⚙️ Method `thread_after_markdown`

```python
def thread_after_markdown(self, result: Any) -> None
```

Show Markdown in a dialog, copy to clipboard, and offer to save a `.md` file.

<details>
<summary>Code:</summary>

```python
def thread_after_markdown(self, result: Any) -> None:
        if result:
            self.show_toast(result)

        markdown = self._markdown_result.strip()
        if not markdown:
            self.show_result()
            return

        self.text_to_clipboard(markdown)
        self.add_line("📋 Markdown copied to clipboard")
        self.dialogs.show_text_multiline(markdown, title="Image OCR → Markdown")

        default_name = suggest_markdown_filename(self._image_paths)
        save_path = self.dialogs.get_save_filename(
            "Save Markdown",
            str(self._markdown_base / default_name),
            "Markdown Files (*.md);;All Files (*)",
        )
        if save_path is not None:
            save_path.write_text(markdown + "\n", encoding="utf-8")
            self.add_line(f"💾 Saved: {save_path}")

        self.show_result()
```

</details>
