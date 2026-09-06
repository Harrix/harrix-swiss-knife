"""Suggest Quick paste emoji via the configured AI provider."""

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

    from PySide6.QtWidgets import QWidget

_MAX_SUGGESTIONS = 8
_EMOJI_RE = re.compile(
    r"(?:"
    r"[\U0001F1E6-\U0001F1FF]{2}"
    r"|[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF\U0001F900-\U0001F9FF]"
    r"(?:\uFE0F)?"
    r"(?:\u200D[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F900-\U0001F9FF](?:\uFE0F)?)*"
    r")"
)


def parse_snippets_emoji_response(response_text: str) -> list[str]:
    """Extract unique emoji from an AI response, keeping first-seen order."""
    found: list[str] = []
    seen: set[str] = set()
    cleaned = response_text.replace("```", " ")
    for match in _EMOJI_RE.finditer(cleaned):
        emoji = match.group(0)
        if emoji in seen:
            continue
        seen.add(emoji)
        found.append(emoji)
        if len(found) >= _MAX_SUGGESTIONS:
            break
    return found


def request_snippets_emoji_suggestions(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    query: str,
    on_emojis: Callable[[list[str]], None],
    on_finished: Callable[[], None],
) -> None:
    """Ask AI for emoji that match `query` and pass them to `on_emojis`."""
    text = query.strip()
    if not text:
        on_finished()
        return

    try:
        prompt_text = build_prompt(app_config, "snippets_emoji_suggest", {"QUERY": text})
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        on_finished()
        return

    def on_success(response_text: str) -> None:
        on_finished()
        emojis = parse_snippets_emoji_response(response_text)
        if not emojis:
            message_box.warning(parent, "Pick emoji", "AI returned no emoji")
            return
        on_emojis(emojis)

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
        toast_message="Picking emoji…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        on_finished()
