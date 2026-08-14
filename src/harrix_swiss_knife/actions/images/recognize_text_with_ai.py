"""Recognize text from scan images with BotHub and format as Markdown."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.ocr_markdown import (
    combine_markdown_sections,
    default_markdown_base,
    ocr_text_to_markdown,
    suggest_markdown_filename,
)
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_image_ocr_prompt,
    image_bytes_and_mime,
    run_bothub_request,
    show_bothub_prompt_build_error,
)


class OnRecognizeTextWithAI(ActionBase):
    """Recognize text from selected images via AI and show it as Markdown."""

    icon = "🤖"
    title = "Recognize text (AI)…"
    bold_title = False

    _PREVIEW_MAX_LEN = 120

    @ActionBase.handle_exceptions("recognizing text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Select images (or use `image_paths`), recognize text with AI, and show Markdown."""
        image_paths = kwargs.get("image_paths")
        if image_paths:
            selected = [Path(path) for path in image_paths]
        else:
            selected = self.dialogs.get_images_from_picker("Select scan images")
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
        default_name = suggest_markdown_filename(self._image_paths)
        self.show_result(
            display_text=markdown,
            save_button=True,
            save_default_path=str(self._markdown_base / default_name),
        )
        self.show_toast(f"✅ Recognized text in {len(self._sections)} image(s)")

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
            self._sections.append(ocr_text_to_markdown(response_text))
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
