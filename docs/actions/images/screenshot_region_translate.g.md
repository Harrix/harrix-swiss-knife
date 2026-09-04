---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `screenshot_region_translate.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnScreenshotRegionTranslate`](#%EF%B8%8F-class-onscreenshotregiontranslate)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnScreenshotRegionTranslate`

```python
class OnScreenshotRegionTranslate(ActionBase)
```

Capture a screen region, recognize text with AI, and translate when needed.

Skips the screenshot preview. Uses `apps.local_language` (default `ru`): if
the recognized text is already in that language, only that text is shown;
otherwise original and translation appear side by side.

<details>
<summary>Code:</summary>

```python
class OnScreenshotRegionTranslate(ActionBase):

    icon = "🌐"
    title = "Screenshot region (OCR + translate)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region OCR translate")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Capture (or use `image` / `image_paths`) and show OCR + translation."""
        image = kwargs.get("image")
        image_paths = kwargs.get("image_paths")

        if isinstance(image, QImage) and not image.isNull():
            self._start_from_qimage(image)
            return

        if image_paths:
            paths = [Path(path) for path in image_paths]
            if not paths:
                return
            self._start_from_path(paths[0])
            return

        captured = capture_region(show_preview=False, show_shutter_button=True)
        if captured is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
        self._start_from_qimage(captured)

    def _run_request(self, prompt_text: str, image_data: tuple[bytes, str]) -> None:
        self._bothub_state = BothubRequestState()

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_success(response_text: str) -> None:
            result = parse_ocr_translate_response(
                response_text,
                local_language_code=local_language_code_from_config(self.config),
            )
            show_ocr_translate_result(self, result)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            image=image_data,
            toast_message="OCR + translate…",
            is_busy=lambda: self._bothub_state.worker is not None,
            state=self._bothub_state,
            on_error=on_error,
        )

    def _start_from_path(self, path: Path) -> None:
        max_image_side = get_max_image_side(self.config)
        try:
            image_data = image_bytes_and_mime(path, max_image_side=max_image_side)
            prompt_text = build_image_ocr_translate_prompt(self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return
        self._run_request(prompt_text, image_data)

    def _start_from_qimage(self, image: QImage) -> None:
        max_image_side = get_max_image_side(self.config)
        try:
            image_data = qimage_bytes_and_mime(image, max_image_side=max_image_side)
            prompt_text = build_image_ocr_translate_prompt(self.config)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return
        self._run_request(prompt_text, image_data)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Capture (or use `image` / `image_paths`) and show OCR + translation.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image = kwargs.get("image")
        image_paths = kwargs.get("image_paths")

        if isinstance(image, QImage) and not image.isNull():
            self._start_from_qimage(image)
            return

        if image_paths:
            paths = [Path(path) for path in image_paths]
            if not paths:
                return
            self._start_from_path(paths[0])
            return

        captured = capture_region(show_preview=False, show_shutter_button=True)
        if captured is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
        self._start_from_qimage(captured)
```

</details>
