"""Suggest a habit emoji via the configured AI provider."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    run_bothub_request,
    show_bothub_prompt_build_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QPushButton, QWidget

_EMOJI_RE = re.compile(
    r"(?:"
    r"[\U0001F1E6-\U0001F1FF]{2}"
    r"|[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF\U0001F900-\U0001F9FF]"
    r"(?:\uFE0F)?"
    r"(?:\u200D[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F900-\U0001F9FF](?:\uFE0F)?)*"
    r")"
)


def parse_habit_emoji_response(response_text: str) -> str:
    """Extract a single emoji from an AI response."""
    for raw_line in response_text.strip().splitlines():
        line = raw_line.strip().strip("`").strip('"').strip("'")
        if not line or line.startswith("```"):
            continue
        match = _EMOJI_RE.search(line)
        if match:
            return match.group(0)
        token = line.split()[0]
        if token and not re.search(r"[A-Za-z]", token):
            return token
    return ""


def request_habit_emoji_suggestion(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    habit_name: str,
    suggest_button: QPushButton,
    on_emoji: Callable[[str], None],
    on_finished: Callable[[], None],
) -> None:
    """Ask AI for an emoji that matches `habit_name` and pass it to `on_emoji`."""
    name = habit_name.strip()
    if not name:
        on_finished()
        return

    try:
        prompt_text = build_prompt(app_config, "habits_emoji_suggest", {"HABIT_NAME": name})
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        on_finished()
        return

    suggest_button.setEnabled(False)

    def on_success(response_text: str) -> None:
        on_finished()
        emoji = parse_habit_emoji_response(response_text)
        if not emoji:
            message_box.warning(parent, "Suggest emoji", "AI returned no emoji")
            return
        on_emoji(emoji)

    def on_error(error_message: str) -> None:
        on_finished()
        message_box.critical(parent, "AI Error", error_message)

    def on_cancelled() -> None:
        on_finished()

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        toast_message="Suggesting emoji…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        on_finished()
