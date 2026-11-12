"""Suggest Lucide icon ids via the configured AI provider."""

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
from harrix_swiss_knife.qt_lucide_icon import list_lucide_icon_names

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from PySide6.QtWidgets import QWidget

_MAX_SUGGESTIONS = 8
_ICON_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def parse_lucide_icon_response(
    response_text: str,
    *,
    known_names: Sequence[str] | None = None,
) -> list[str]:
    """Extract unique Lucide ids from an AI response, validated against the catalog."""
    catalog = tuple(known_names) if known_names is not None else list_lucide_icon_names()
    by_cf = {name.casefold(): name for name in catalog}
    found: list[str] = []
    seen: set[str] = set()
    cleaned = response_text.replace("```", "\n")
    for raw_line in cleaned.splitlines():
        line = raw_line.strip().lstrip("-*•").strip().strip("`").strip('"').strip("'")
        if not line or line.startswith("#"):
            continue
        for match in _ICON_ID_RE.finditer(line.casefold()):
            resolved = _resolve_lucide_icon_name(match.group(0), by_cf)
            if resolved is None or resolved in seen:
                continue
            seen.add(resolved)
            found.append(resolved)
            if len(found) >= _MAX_SUGGESTIONS:
                return found
    return found


def request_lucide_icon_suggestions(
    parent: QWidget,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    query: str,
    on_icons: Callable[[list[str]], None],
    on_finished: Callable[[], None],
) -> None:
    """Ask AI for Lucide ids that match `query` and pass them to `on_icons`."""
    text = query.strip()
    if not text:
        on_finished()
        return

    try:
        prompt_text = build_prompt(app_config, "lucide_icon_suggest", {"QUERY": text})
    except ValueError as exc:
        show_bothub_prompt_build_error(parent, exc)
        on_finished()
        return

    def on_success(response_text: str) -> None:
        on_finished()
        icons = parse_lucide_icon_response(response_text)
        if not icons:
            message_box.warning(parent, "Suggest Lucide", "AI returned no valid Lucide icons")
            return
        on_icons(icons)

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
        toast_message="Suggesting Lucide icons…",
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_error,
        on_cancelled=on_cancelled,
    )
    if not started:
        on_finished()


def _resolve_lucide_icon_name(candidate: str, by_cf: dict[str, str]) -> str | None:
    exact = by_cf.get(candidate)
    if exact is not None:
        return exact
    prefix_hits = [name for key, name in by_cf.items() if key.startswith(f"{candidate}-") or key == candidate]
    if len(prefix_hits) == 1:
        return prefix_hits[0]
    contains_hits = [name for key, name in by_cf.items() if candidate in key.split("-")]
    if len(contains_hits) == 1:
        return contains_hits[0]
    return None
