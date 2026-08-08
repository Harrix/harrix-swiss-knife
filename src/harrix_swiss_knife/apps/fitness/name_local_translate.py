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
    from collections.abc import Callable

    from PySide6.QtWidgets import QLineEdit, QPushButton, QWidget

_TSV_COLUMN_COUNT = 2


def parse_name_local_batch_response(text: str) -> dict[str, str]:
    """Parse TSV lines `Name<TAB>LocalName` into a name-to-translation map."""
    translations: dict[str, str] = {}
    for line in _iter_data_lines(text):
        parts = line.split("\t")
        if len(parts) != _TSV_COLUMN_COUNT:
            continue
        name = parts[0].strip()
        name_local = parts[1].strip()
        if not name or not name_local:
            continue
        translations[name] = name_local
    return translations


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
    """Translate one name into the local language via BotHub and fill `name_local_edit`."""
    name = name_edit.text().strip()
    if not name:
        message_box.warning(parent, "Translation", "Enter name first")
        return

    try:
        prompt_text = build_prompt(
            app_config,
            "fitness_name_translate_local",
            {
                "NAME": name,
                "LOCAL_LANGUAGE": get_apps_local_language_display_name(app_config),
            },
        )
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
        name_local_edit.setText(translated)

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
        toast_message="Translating name…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        translate_button.setEnabled(True)


def request_names_local_batch_translation(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    names: list[str],
    on_success: Callable[[dict[str, str]], None],
    on_finished: Callable[[], None] | None = None,
) -> None:
    """Translate many names into the local language and pass a map to `on_success`."""
    if not names:
        message_box.information(parent, "Translation", "All names already have a local translation.")
        if on_finished is not None:
            on_finished()
        return

    names_text = "\n".join(names)
    try:
        prompt_text = build_prompt(
            app_config,
            "fitness_names_translate_local",
            {
                "NAMES": names_text,
                "LOCAL_LANGUAGE": get_apps_local_language_display_name(app_config),
            },
        )
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        if on_finished is not None:
            on_finished()
        return

    def success_wrapper(response_text: str) -> None:
        translations = parse_name_local_batch_response(response_text)
        on_success(translations)
        if on_finished is not None:
            on_finished()

    def on_error(error_message: str) -> None:
        message_box.critical(parent, "BotHub Error", error_message)
        if on_finished is not None:
            on_finished()

    def on_cancelled() -> None:
        if on_finished is not None:
            on_finished()

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        success_wrapper,
        toast_message="Translating names…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started and on_finished is not None:
        on_finished()


def _iter_data_lines(text: str) -> list[str]:
    """Return non-empty lines, skipping Markdown code fences."""
    lines: list[str] = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        lines.append(line)
    return lines
