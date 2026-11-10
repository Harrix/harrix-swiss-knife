---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ask_screenshot_with_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAskScreenshotWithAI`](#%EF%B8%8F-class-onaskscreenshotwithai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnAskScreenshotWithAI`

```python
class OnAskScreenshotWithAI(ActionBase)
```

Send screenshot image(s) to AI and show the answer.

<details>
<summary>Code:</summary>

```python
class OnAskScreenshotWithAI(ActionBase):

    icon = "💬"
    title = "Ask AI…"
    bold_title = False

    _PREVIEW_MAX_LEN = 120

    @ActionBase.handle_exceptions("asking AI about screenshot")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Select images (or use `image_paths`), ask AI, and show the answer.

        Optional kwargs:

        - `image_paths`: paths to send instead of opening a picker.
        - `note` (`str`): extra instructions included in the prompt.
        - `ask_note` (`bool`): when `True`, prompt for a note before sending.

        """
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select screenshot images")
        if not selected:
            return

        note = str(kwargs.get("note") or "")
        if kwargs.get("ask_note"):
            entered = self.get_text_textarea("Ask AI", "Note for the AI:")
            if entered is None:
                return
            note = entered

        self._image_paths = [Path(path) for path in selected]
        self._note = note.strip()
        self._sections: list[str] = []
        self._bothub_state = BothubRequestState()
        self._process_image(0)

    def _finish_answer(self) -> None:
        answer = "\n\n".join(section for section in self._sections if section.strip()).strip()
        if not answer:
            self.add_line("❌ Empty answer")
            self.show_result()
            return

        self.text_to_clipboard(answer)
        self.add_line("📋 Answer copied to clipboard")
        present_recognized_text(self, answer)
        self.show_toast(f"✅ Answer for {len(self._sections)} image(s)")

    def _process_image(self, index: int) -> None:
        total = len(self._image_paths)
        if index >= total:
            self._finish_answer()
            return

        path = self._image_paths[index]
        self.add_line(f"🔵 [{index + 1}/{total}] {path.name}")

        max_image_side = get_max_image_side(self.config)

        try:
            image_data = image_bytes_and_mime(path, max_image_side=max_image_side)
            prompt_text = build_image_ask_prompt(self.config, self._note)
        except ValueError as exc:
            show_bothub_prompt_build_error(None, exc)
            return

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        def on_success(response_text: str) -> None:
            text = response_text.strip()
            self._sections.append(text)
            preview = text.replace("\n", " ")
            if len(preview) > self._PREVIEW_MAX_LEN:
                preview = preview[: self._PREVIEW_MAX_LEN - 3] + "..."
            self.add_line(f"💬 {preview or '(empty answer)'}")
            self._process_image(index + 1)

        toast = f"Ask AI [{index + 1}/{total}]: {path.name}…"
        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            image=image_data,
            toast_message=toast,
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

Select images (or use `image_paths`), ask AI, and show the answer.

Optional kwargs:

- `image_paths`: paths to send instead of opening a picker.
- `note` (`str`): extra instructions included in the prompt.
- `ask_note` (`bool`): when `True`, prompt for a note before sending.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select screenshot images")
        if not selected:
            return

        note = str(kwargs.get("note") or "")
        if kwargs.get("ask_note"):
            entered = self.get_text_textarea("Ask AI", "Note for the AI:")
            if entered is None:
                return
            note = entered

        self._image_paths = [Path(path) for path in selected]
        self._note = note.strip()
        self._sections: list[str] = []
        self._bothub_state = BothubRequestState()
        self._process_image(0)
```

</details>
