"""BotHub helpers for fitness `name_local` translation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.apps_config import get_apps_local_language_display_name
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    run_bothub_request,
    show_bothub_prompt_build_error,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QLineEdit, QPushButton, QWidget


def parse_name_local_response(response_text: str) -> str:
    """Extract a single-line local name from a BotHub response."""
    for line in response_text.splitlines():
        text = line.strip().strip("`").strip('"').strip("'")
        if text:
            return text
    return response_text.strip()


def request_name_local_translation(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    name_edit: QLineEdit,
    name_local_edit: QLineEdit,
    translate_button: QPushButton,
) -> None:
    """Translate between English name and local name via BotHub.

    Prefer English → local when `name_edit` is filled. If English is empty and
    local is filled, translate local → English into `name_edit`.

    """
    name = name_edit.text().strip()
    name_local = name_local_edit.text().strip()
    local_language = get_apps_local_language_display_name(app_config)

    if name:
        prompt_key = "fitness_name_translate_local"
        prompt_vars = {"NAME": name, "LOCAL_LANGUAGE": local_language}
        target_edit = name_local_edit
        toast_message = "Translating name…"
    elif name_local:
        prompt_key = "fitness_name_translate_from_local"
        prompt_vars = {"NAME_LOCAL": name_local, "LOCAL_LANGUAGE": local_language}
        target_edit = name_edit
        toast_message = "Translating local name…"
    else:
        message_box.warning(parent, "Translation", "Enter English name or local name first")
        return

    try:
        prompt_text = build_prompt(app_config, prompt_key, prompt_vars)
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        return

    translate_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        translate_button.setEnabled(True)
        translated = parse_name_local_response(response_text)
        if not translated:
            message_box.warning(parent, "Translation", "BotHub returned an empty translation")
            return
        target_edit.setText(translated)

    def on_error(error_message: str) -> None:
        translate_button.setEnabled(True)
        message_box.critical(parent, "BotHub Error", error_message)

    def on_cancelled() -> None:
        translate_button.setEnabled(True)

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        toast_message=toast_message,
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        translate_button.setEnabled(True)
