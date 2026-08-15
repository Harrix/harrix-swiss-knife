"""BotHub helper to expand icon keywords from a raster preview."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.icons.keywords_update import parse_keywords_text
from harrix_swiss_knife.apps.icons.vector_render import render_icon_to_image
from harrix_swiss_knife.integrations.bothub import (
    BothubRequestState,
    build_prompt,
    get_max_image_side,
    qimage_bytes_and_mime,
    run_bothub_request,
    show_bothub_prompt_build_error,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from PySide6.QtWidgets import QPushButton, QWidget

    from harrix_swiss_knife.apps.icons.catalog import IconFamily

PROMPT_KEY = "vector_icons_keywords"
_RASTER_SIDE = 768


class KeywordsBatchRunner:
    """Process selected icon families with AI, one request at a time."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        app_config: dict[str, Any],
        jobs: list[tuple[IconFamily, Path]],
        on_item_success: Callable[[IconFamily, list[str]], None],
        on_finished: Callable[..., None],
        request_fn: Callable[..., None] | None = None,
    ) -> None:
        """Store batch jobs and callbacks."""
        self._parent = parent
        self._app_config = app_config
        self._jobs = jobs
        self._on_item_success = on_item_success
        self._on_finished = on_finished
        self._request_fn = request_fn or request_keywords_fill
        self._state = BothubRequestState()
        self._index = 0
        self._updated = 0
        self._failed = 0
        self._cancelled = False
        self._running = False

    def cancel(self) -> None:
        """Stop after the current request and cancel it when possible."""
        self._cancelled = True
        worker = self._state.worker
        if worker is not None:
            worker.cancel()

    @property
    def is_running(self) -> bool:
        """Return whether a batch is still in progress."""
        return self._running

    def start(self) -> None:
        """Start the first remaining job."""
        if self._running:
            return
        self._running = True
        self._process_next()

    def _finish(self) -> None:
        self._running = False
        self._on_finished(self._updated, self._failed, cancelled=self._cancelled)

    def _on_error(self, _error_message: str) -> None:
        self._failed += 1
        self._index += 1
        self._process_next()

    def _on_not_started(self) -> None:
        self._cancelled = True
        self._finish()

    def _on_request_cancelled(self) -> None:
        self._cancelled = True
        self._finish()

    def _on_tags(self, tags: list[str]) -> None:
        family, _icon_path = self._jobs[self._index]
        self._on_item_success(family, tags)
        self._updated += 1
        self._index += 1
        self._process_next()

    def _process_next(self) -> None:
        if self._cancelled or self._index >= len(self._jobs):
            self._finish()
            return
        family, icon_path = self._jobs[self._index]
        self._request_fn(
            self._parent,
            app_config=self._app_config,
            bothub_state=self._state,
            icon_path=icon_path,
            category=", ".join(family.categories) or family.id,
            tags=list(family.tags),
            fill_button=None,
            on_tags=self._on_tags,
            on_error=self._on_error,
            on_cancelled=self._on_request_cancelled,
            on_not_started=self._on_not_started,
            toast_message=f"Processing keywords… {self._index + 1}/{len(self._jobs)} — {family.id}",
            show_empty_warning=False,
        )


def request_keywords_fill(
    parent: QWidget | None,
    *,
    app_config: dict[str, Any],
    bothub_state: BothubRequestState,
    icon_path: Path,
    category: str,
    tags: list[str],
    fill_button: QPushButton | None,
    on_tags: Callable[[list[str]], None],
    on_error: Callable[[str], None] | None = None,
    on_cancelled: Callable[[], None] | None = None,
    on_not_started: Callable[[], None] | None = None,
    toast_message: str = "Processing keywords…",
    show_empty_warning: bool = True,
) -> None:
    """Send a raster preview plus category/tags to BotHub and return keywords."""
    image = render_icon_to_image(icon_path, _RASTER_SIDE)
    if image is None or image.isNull():
        message = f"Could not rasterize icon:\n{icon_path}"
        if on_error is not None:
            on_error(message)
        else:
            message_box.warning(parent, "Process with AI", message)
        return

    try:
        image_data = qimage_bytes_and_mime(image, max_image_side=_max_image_side(app_config))
        prompt_text = build_prompt(
            app_config,
            PROMPT_KEY,
            {
                "CATEGORY": category,
                "TAGS": "\n".join(tags),
            },
            prompt_display_name="vector_icons_keywords",
        )
    except ValueError as exc:
        if on_error is not None:
            on_error(str(exc))
        else:
            show_bothub_prompt_build_error(parent, exc)
        return

    if fill_button is not None:
        fill_button.setEnabled(False)

    def restore_button() -> None:
        if fill_button is not None:
            fill_button.setEnabled(True)

    def on_success(response_text: str) -> None:
        restore_button()
        parsed = parse_keywords_text(response_text)
        if not parsed:
            message = "BotHub returned no keywords."
            if show_empty_warning:
                message_box.warning(parent, "Process with AI", message)
            if on_error is not None:
                on_error(message)
            return
        on_tags(parsed)

    def on_request_error(error_message: str) -> None:
        restore_button()
        if on_error is not None:
            on_error(error_message)
        else:
            message_box.critical(parent, "BotHub Error", error_message)

    def on_request_cancelled() -> None:
        restore_button()
        if on_cancelled is not None:
            on_cancelled()

    started = run_bothub_request(
        parent,
        app_config,
        prompt_text,
        on_success,
        image=image_data,
        toast_message=toast_message,
        is_busy=lambda: bothub_state.worker is not None,
        state=bothub_state,
        on_error=on_request_error,
        on_cancelled=on_request_cancelled,
    )
    if not started:
        restore_button()
        if on_not_started is not None:
            on_not_started()


def _max_image_side(app_config: dict[str, Any]) -> int:
    return get_max_image_side(app_config, default=_RASTER_SIDE)
