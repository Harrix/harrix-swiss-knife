"""Parse and present OCR + translate results for screenshots."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common.apps_config import get_apps_local_language

if TYPE_CHECKING:
    from harrix_swiss_knife.actions.common.base import ActionBase

_JSON_OBJECT = re.compile(r"\{[\s\S]*\}")


@dataclass(frozen=True, slots=True)
class OcrTranslateResult:
    """Recognized text plus optional translation into the local language."""

    language: str
    is_local: bool
    original: str
    translation: str

    @property
    def display_text(self) -> str:
        """Text to copy: translation when present, otherwise original."""
        if not self.is_local and self.translation.strip():
            return self.translation
        return self.original


def local_language_code_from_config(config: dict[str, Any]) -> str:
    """Return `apps.local_language` for OCR/translate parsers."""
    return get_apps_local_language(config)


def parse_ocr_translate_response(text: str, *, local_language_code: str | None = None) -> OcrTranslateResult:
    """Parse a BotHub OCR+translate JSON response into `OcrTranslateResult`."""
    payload = _extract_json_object(text)
    if payload is None:
        original = text.strip()
        return OcrTranslateResult(
            language="und",
            is_local=True,
            original=original,
            translation="",
        )

    original = str(payload.get("original") or "").strip()
    translation = str(payload.get("translation") or "").strip()
    language = str(payload.get("language") or "und").strip().lower() or "und"
    raw_local = payload.get("is_local")
    if isinstance(raw_local, bool):
        is_local = raw_local
    else:
        code = (local_language_code or "").strip().lower()
        is_local = not translation or (bool(code) and language == code) or translation == original

    if not original and not translation:
        return OcrTranslateResult(language=language, is_local=True, original="", translation="")

    if is_local or not translation or translation == original:
        return OcrTranslateResult(
            language=language,
            is_local=True,
            original=original or translation,
            translation="",
        )

    return OcrTranslateResult(
        language=language,
        is_local=False,
        original=original,
        translation=translation,
    )


def show_ocr_translate_result(action: ActionBase, result: OcrTranslateResult) -> None:
    """Show original-only or original+translation dialog and copy the primary text."""
    display = result.display_text.strip()
    if not display and not result.original.strip():
        action.add_line("No text recognized")
        action.show_toast("No text recognized")
        action.show_result(display_text="")
        return

    action.text_to_clipboard(display)
    action.add_line("📋 Text copied to clipboard")

    if result.is_local or not result.translation.strip():
        action.dialogs.show_text_multiline(
            result.original,
            title="Recognized text",
            remove_paragraphs_button=True,
        )
        action.show_toast("✅ Recognized text")
        return

    action.dialogs.show_text_diff_side_by_side(
        result.original,
        result.translation,
        title="Recognized text + translation",
        remove_paragraphs_button=True,
        before_label="Original",
        after_label="Translation",
        highlight_changes=False,
    )
    action.show_toast("✅ Recognized and translated")


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = _JSON_OBJECT.search(cleaned)
        if match is None:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, dict) else None
