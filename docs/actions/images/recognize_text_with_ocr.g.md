---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `recognize_text_with_ocr.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRecognizeTextWithOcr`](#%EF%B8%8F-class-onrecognizetextwithocr)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after_markdown`](#%EF%B8%8F-method-thread_after_markdown)

</details>

## 🏛️ Class `OnRecognizeTextWithOcr`

```python
class OnRecognizeTextWithOcr(ActionBase)
```

Recognize text from selected images with local OCR and show it as Markdown.

<details>
<summary>Code:</summary>

```python
class OnRecognizeTextWithOcr(ActionBase):

    icon = "🔤"
    title = "Recognize text (OCR, local)…"
    bold_title = False

    _PREVIEW_MAX_LEN = 120

    @ActionBase.handle_exceptions("recognizing text with OCR")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Select images (or use `image_paths`), recognize text with OCR, and show Markdown."""
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select scan images")
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self._markdown_base = default_markdown_base(self._image_paths)
        self._markdown_result = ""
        self._ocr_texts: list[str] = []
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
        ocr_texts: list[str] = []
        total = len(self._image_paths)

        for index, path in enumerate(self._image_paths, 1):
            self.add_line(f"🔵 [{index}/{total}] {path.name}")
            text = ocr_image(path, reader)
            ocr_texts.append(text)
            section = ocr_text_to_markdown_section(text, path, self._markdown_base)
            sections.append(section)
            preview = text.strip().replace("\n", " ")
            if len(preview) > self._PREVIEW_MAX_LEN:
                preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
            self.add_line(f"📝 {preview or '(no text recognized)'}")

        self._ocr_texts = ocr_texts
        self._markdown_result = combine_markdown_sections(sections)
        return f"✅ Recognized text in {len(sections)} image(s)"

    @ActionBase.handle_exceptions("image to Markdown OCR completion")
    def thread_after_markdown(self, result: Any) -> None:
        """Show Markdown in a dialog, copy to clipboard, and offer to save a `.md` file."""
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
            note_dir, saved_images = save_ocr_markdown_with_images(save_path, self._image_paths, self._ocr_texts)
            self.add_line(f"💾 Saved note folder: {note_dir}")
            self.add_line(f"📝 {note_dir / (note_dir.name + '.md')}")
            self.add_line(f"🖼️ Images: {note_dir / 'img'} ({len(saved_images)})")

        self.show_result()

    @staticmethod
    def _create_reader(easyocr_module: Any) -> easyocr.Reader:
        # EasyOCR/torch emit noisy CPU-only warnings (pin_memory, quantized tensors).
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=r".*pin_memory.*", category=UserWarning)
            warnings.filterwarnings(
                "ignore",
                message=r".*torch\.quantize_per_tensor.*",
                category=UserWarning,
            )
            return easyocr_module.Reader(["ru", "en"], gpu=False, verbose=False)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Select images (or use `image_paths`), recognize text with OCR, and show Markdown.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select scan images")
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self._markdown_base = default_markdown_base(self._image_paths)
        self._markdown_result = ""
        self._ocr_texts: list[str] = []
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
        ocr_texts: list[str] = []
        total = len(self._image_paths)

        for index, path in enumerate(self._image_paths, 1):
            self.add_line(f"🔵 [{index}/{total}] {path.name}")
            text = ocr_image(path, reader)
            ocr_texts.append(text)
            section = ocr_text_to_markdown_section(text, path, self._markdown_base)
            sections.append(section)
            preview = text.strip().replace("\n", " ")
            if len(preview) > self._PREVIEW_MAX_LEN:
                preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
            self.add_line(f"📝 {preview or '(no text recognized)'}")

        self._ocr_texts = ocr_texts
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
            note_dir, saved_images = save_ocr_markdown_with_images(save_path, self._image_paths, self._ocr_texts)
            self.add_line(f"💾 Saved note folder: {note_dir}")
            self.add_line(f"📝 {note_dir / (note_dir.name + '.md')}")
            self.add_line(f"🖼️ Images: {note_dir / 'img'} ({len(saved_images)})")

        self.show_result()
```

</details>
