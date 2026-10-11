"""BotHub helper to expand icon keywords from a raster preview."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QThread
from PySide6.QtGui import QImage

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.icons.keywords_update import parse_keywords_text
from harrix_swiss_knife.apps.icons.keywords_workers import KeywordsRasterizeWorker
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
        on_item_success: Callable[..., None],
        on_finished: Callable[..., None],
        request_fn: Callable[..., None] | None = None,
        silent: bool = False,
        await_item_success: bool = False,
    ) -> None:
        """Store batch jobs and callbacks.

        Args:

        - `silent`: When `True`, skip BotHub toasts and do not modal-block the owner
          window (used for background keyword refresh after catalog open).
        - `await_item_success`: When `True`, `on_item_success(family, tags, done)` must
          call `done()` before the next job starts (background catalog commits).

        """
        self._parent = parent
        self._app_config = app_config
        self._jobs = jobs
        self._on_item_success = on_item_success
        self._on_finished = on_finished
        self._request_fn = request_fn or request_keywords_fill
        self._silent = silent
        self._await_item_success = await_item_success
        self._state = BothubRequestState(toast_pin_chain=not silent)
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

    def _after_item_success(self) -> None:
        self._updated += 1
        self._index += 1
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
        if self._await_item_success:
            self._on_item_success(family, tags, self._after_item_success)
            return
        self._on_item_success(family, tags)
        self._after_item_success()

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
            show_toast=not self._silent,
            show_validation_errors=not self._silent,
            offer_retry=not self._silent,
            owner_modal=not self._silent,
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
    show_toast: bool = True,
    show_validation_errors: bool = True,
    offer_retry: bool = True,
    owner_modal: bool = True,
) -> None:
    """Send a raster preview plus category/tags to BotHub and return keywords."""
    if fill_button is not None:
        fill_button.setEnabled(False)

    def restore_button() -> None:
        if fill_button is not None:
            fill_button.setEnabled(True)

    def fail(message: str) -> None:
        restore_button()
        if on_error is not None:
            on_error(message)
        elif show_empty_warning:
            message_box.warning(parent, "Process with AI", message)

    def start_bothub(image: QImage) -> None:
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
            restore_button()
            if on_error is not None:
                on_error(str(exc))
            elif show_validation_errors:
                show_bothub_prompt_build_error(parent, exc)
            return

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
            elif show_validation_errors:
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
            offer_retry=offer_retry,
            owner_modal=owner_modal,
            show_toast=show_toast,
            show_validation_errors=show_validation_errors,
        )
        if not started:
            restore_button()
            if on_not_started is not None:
                on_not_started()

    thread = QThread(parent)
    worker = KeywordsRasterizeWorker(icon_path, side=_RASTER_SIDE)
    worker.moveToThread(thread)

    def on_raster_ok(image: object) -> None:
        if isinstance(image, QImage) and not image.isNull():
            start_bothub(image)
        else:
            fail(f"Could not rasterize icon:\n{icon_path}")

    def on_raster_fail(message: str) -> None:
        fail(message)

    worker.succeeded.connect(on_raster_ok)
    worker.failed.connect(on_raster_fail)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.started.connect(worker.run)
    thread.start()


def _max_image_side(app_config: dict[str, Any]) -> int:
    return get_max_image_side(app_config, default=_RASTER_SIDE)
