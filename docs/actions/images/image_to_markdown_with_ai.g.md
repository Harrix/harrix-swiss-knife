---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `image_to_markdown_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnImageToMarkdownWithAI`](#️-class-onimagetomarkdownwithai)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnImageToMarkdownWithAI`

```python
class OnImageToMarkdownWithAI(ActionBase)
```

OCR selected images via AI and build Markdown with headings and image links.

<details>
<summary>Code:</summary>

```python
class OnImageToMarkdownWithAI(ActionBase):

    icon = "🤖"
    title = "Image to Markdown (OCR, AI)…"
    bold_title = False

    _IMAGE_FILTER = "Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.avif *.tif *.tiff);;All Files (*)"
    _PREVIEW_MAX_LEN = 120

    @ActionBase.handle_exceptions("image to Markdown OCR (AI)")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Select images, run AI OCR sequentially, and show Markdown output."""
        selected = self.dialogs.get_open_filenames(
            "Select scan images",
            self.config["path_articles"],
            self._IMAGE_FILTER,
        )
        if not selected:
            return

        self._image_paths = [Path(path) for path in selected]
        self._markdown_base = default_markdown_base(self._image_paths)
        self._sections: list[str] = []
        self._bothub_state = BothubRequestState()
        self._process_image(0)

    def _finish_markdown(self) -> None:
        markdown = combine_markdown_sections(self._sections).strip()
        if not markdown:
            self.show_result()
            return

        self.text_to_clipboard(markdown)
        self.add_line("📋 Markdown copied to clipboard")
        self.dialogs.show_text_multiline(markdown, title="Image OCR (AI) → Markdown")

        default_name = suggest_markdown_filename(self._image_paths)
        save_path = self.dialogs.get_save_filename(
            "Save Markdown",
            str(self._markdown_base / default_name),
            "Markdown Files (*.md);;All Files (*)",
        )
        if save_path is not None:
            save_path.write_text(markdown + "\n", encoding="utf-8")
            self.add_line(f"💾 Saved: {save_path}")

        self.show_toast(f"✅ Recognized text in {len(self._sections)} image(s)")
        self.show_result()

    def _process_image(self, index: int) -> None:
        total = len(self._image_paths)
        if index >= total:
            self._finish_markdown()
            return

        path = self._image_paths[index]
        self.add_line(f"🔵 [{index + 1}/{total}] {path.name}")

        bothub_cfg = self.config.get("bothub") or {}
        max_image_side = int(bothub_cfg.get("max_image_side", 1600))

        try:
            image_data = image_bytes_and_mime(path, max_image_side=max_image_side)
            prompt_text = build_image_ocr_prompt(self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_success(response_text: str) -> None:
            section = ocr_text_to_markdown_section(response_text, path, self._markdown_base)
            self._sections.append(section)
            preview = response_text.strip().replace("\n", " ")
            if len(preview) > self._PREVIEW_MAX_LEN:
                preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
            self.add_line(f"📝 {preview or '(no text recognized)'}")
            self._process_image(index + 1)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            image=image_data,
            toast_message=f"OCR [{index + 1}/{total}]: {path.name}…",
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
            on_error=on_error,
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Select images, run AI OCR sequentially, and show Markdown output.

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
        self._sections: list[str] = []
        self._bothub_state = BothubRequestState()
        self._process_image(0)
```

</details>
