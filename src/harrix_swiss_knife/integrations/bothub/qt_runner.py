"""Qt helpers: toast + background worker for BotHub requests."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife import toast_cancellable_http_notification, toast_notification_base
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.ai.config import get_provider_settings
from harrix_swiss_knife.integrations.bothub.config import (
    get_active_provider,
    get_connection_params,
    validate_api_key,
)
from harrix_swiss_knife.integrations.bothub.worker import BothubChatWorker

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class BothubRequestSpec:
    """Everything needed to start or retry one BotHub request."""

    parent: QWidget | None
    config: dict[str, Any]
    prompt_text: str
    on_success: Callable[[str], None]
    images: list[tuple[bytes, str]] | None = None
    audio: tuple[bytes, str] | None = None
    model: str | None = None
    toast_message: str = "Requesting AI…"
    is_busy: Callable[[], bool] | None = None
    state: BothubRequestState | None = None
    on_error: Callable[[str], None] | None = None
    on_cancelled: Callable[[], None] | None = None
    offer_retry: bool = True
    owner_modal: bool = True
    show_toast: bool = True


@dataclass
class BothubRequestState:
    """Mutable holder for an in-flight BotHub request (worker + toast)."""

    worker: BothubChatWorker | None = None
    toast: toast_notification_base.ToastNotificationBase | None = None


def run_bothub_request(
    parent: QWidget | None,
    config: dict[str, Any],
    prompt_text: str,
    on_success: Callable[[str], None],
    *,
    images: list[tuple[bytes, str]] | None = None,
    image: tuple[bytes, str] | None = None,
    audio: tuple[bytes, str] | None = None,
    model: str | None = None,
    toast_message: str = "Requesting AI…",
    is_busy: Callable[[], bool] | None = None,
    state: BothubRequestState | None = None,
    on_error: Callable[[str], None] | None = None,
    on_cancelled: Callable[[], None] | None = None,
    offer_retry: bool = True,
    owner_modal: bool = True,
    show_toast: bool = True,
) -> bool:
    """Validate config, show toast, start worker. Returns `True` if the request started.

    Args:

    - `parent`: Parent widget for message boxes.
    - `config`: Application config dict.
    - `prompt_text`: Full prompt to send.
    - `on_success`: Called with assistant text when the request succeeds.
    - `images`: Optional vision inputs as `(bytes, mime_type)` pairs.
    - `image`: Optional single vision input (merged into `images`).
    - `audio`: Optional speech input `(bytes, mime_type)`.
    - `model`: Optional model override; defaults to provider model from config.
    - `toast_message`: Toast label while waiting.
    - `is_busy`: If provided and returns `True`, the request is not started.
    - `state`: Optional holder updated with worker/toast refs; cleared on completion.
    - `on_error`: If set, called with the error message instead of the default critical dialog.
      When `offer_retry` is `True`, called only after the user closes the retry dialog.
    - `on_cancelled`: If set, called when the user cancels the in-flight request.
      When `offer_retry` is `True`, called only after the user closes the retry dialog.
    - `offer_retry`: When `True` (default), error and cancel show Retry / Close before
      finishing. Defaults to `True`.
    - `owner_modal`: When `True` (default), the toast blocks the owner window.
      Use `False` for background fills so the UI stays interactive.
    - `show_toast`: When `False`, run without a BotHub toast.

    """
    image_list = list(images or [])
    if image is not None:
        image_list.append(image)

    spec = BothubRequestSpec(
        parent=parent,
        config=config,
        prompt_text=prompt_text,
        on_success=on_success,
        images=image_list or None,
        audio=audio,
        model=model,
        toast_message=toast_message,
        is_busy=is_busy,
        state=state,
        on_error=on_error,
        on_cancelled=on_cancelled,
        offer_retry=offer_retry,
        owner_modal=owner_modal,
        show_toast=show_toast,
    )
    return _start_bothub_request(spec)


def run_bothub_request_blocking(
    parent: QWidget | None,
    config: dict[str, Any],
    prompt_text: str,
    *,
    images: list[tuple[bytes, str]] | None = None,
    image: tuple[bytes, str] | None = None,
    audio: tuple[bytes, str] | None = None,
    model: str | None = None,
    toast_message: str = "Requesting AI…",
    state: BothubRequestState | None = None,
    offer_retry: bool = True,
) -> str | None:
    """Run an AI request and block the UI thread until it finishes.

    Returns assistant text on success, or `None` on cancel / validation failure.
    When `offer_retry` is `True`, errors and cancels show a Retry dialog first.
    Errors after Close are not shown again (already shown in the retry dialog).

    """
    loop = QEventLoop()
    outcome: dict[str, str | None] = {"text": None}

    def on_success(response_text: str) -> None:
        outcome["text"] = response_text
        loop.quit()

    def on_error(message: str) -> None:
        # With offer_retry, the message was already shown in the retry dialog.
        if not offer_retry:
            message_box.critical(parent, "AI Error", message)
        loop.quit()

    def on_cancelled() -> None:
        loop.quit()

    started = run_bothub_request(
        parent,
        config,
        prompt_text,
        on_success,
        images=images,
        image=image,
        audio=audio,
        model=model,
        toast_message=toast_message,
        state=state,
        on_error=on_error,
        on_cancelled=on_cancelled,
        offer_retry=offer_retry,
    )
    if not started:
        return None

    loop.exec()
    return outcome["text"]


def _finish_cancelled(spec: BothubRequestSpec) -> None:
    """Invoke the caller's cancel path after retry was declined or disabled."""
    print("❌ Request cancelled by user.")
    if spec.on_cancelled is not None:
        spec.on_cancelled()


def _finish_error(spec: BothubRequestSpec, message: str) -> None:
    """Invoke the caller's error path after retry was declined or disabled."""
    if spec.on_error is not None:
        spec.on_error(message)
    else:
        message_box.critical(spec.parent, "AI Error", message)


def _offer_retry_or_finish(spec: BothubRequestSpec, *, cancelled: bool, message: str) -> None:
    """Show Retry / Close, then either restart the same request or finish.

    Args:

    - `spec` (`BothubRequestSpec`): Original request payload and callbacks.
    - `cancelled` (`bool`): `True` when the user cancelled; otherwise an API/network error.
    - `message` (`str`): Error text, or a cancel explanation.

    """
    if not spec.offer_retry:
        if cancelled:
            _finish_cancelled(spec)
        else:
            _finish_error(spec, message)
        return

    title = "Request cancelled" if cancelled else "AI Error"
    body = message if message.strip() else ("Request cancelled by user." if cancelled else "Unknown error.")
    body = f"{body}\n\nSend the same request again?"
    if message_box.ask_retry(spec.parent, title, body, critical=not cancelled):
        # Keep call-site busy checks (`worker is not None`) true until the new
        # worker is assigned: clear only right before restart.
        if spec.state is not None:
            spec.state.worker = None
        if not _start_bothub_request(spec):
            if cancelled:
                _finish_cancelled(spec)
            else:
                _finish_error(spec, message)
        return

    if spec.state is not None:
        spec.state.worker = None
    if cancelled:
        _finish_cancelled(spec)
    else:
        _finish_error(spec, message)


def _release_bothub_worker(worker: BothubChatWorker) -> None:
    """Drop the tracking ref and schedule safe Qt deletion after the thread stops."""
    with suppress(ValueError):
        _active_bothub_workers.remove(worker)
    worker.finished.connect(worker.deleteLater)
    if not worker.isRunning():
        worker.deleteLater()


def _resolve_toast_parent(parent: QWidget | None) -> QWidget | None:
    """Parent the cancel toast under the active modal dialog when possible.

    Parenting the toast under the modal (with WindowModal on the toast) lets
    Escape / close cancel the request during Fill with AI and similar flows,
    without blocking sibling app Windows in the same process.

    """
    if parent is not None:
        return parent
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return None
    modal = app.activeModalWidget()
    return modal if isinstance(modal, QWidget) else None


def _start_bothub_request(spec: BothubRequestSpec) -> bool:
    """Validate config, show toast, and start a worker for `spec`."""
    if spec.is_busy is not None and spec.is_busy():
        return False

    for_speech = spec.audio is not None
    api_key = validate_api_key(spec.config, parent=spec.parent, for_speech=for_speech)
    if api_key is None:
        return False

    provider = get_active_provider(spec.config, for_speech=for_speech)
    api_key, base_url, default_model, proxy_url = get_connection_params(spec.config, for_speech=for_speech)
    resolved_model = spec.model if spec.model is not None else default_model
    settings = get_provider_settings(spec.config, provider)
    max_tokens_raw = settings.get("max_tokens")
    max_tokens = int(max_tokens_raw) if max_tokens_raw is not None else None

    toast = None
    if spec.show_toast:
        toast_parent = _resolve_toast_parent(spec.parent)
        toast = toast_cancellable_http_notification.ToastCancellableHttpNotification(
            spec.toast_message,
            parent=toast_parent,
            owner_modal=spec.owner_modal,
        )
        toast.start_countdown()

    worker = BothubChatWorker(
        api_key=api_key,
        base_url=base_url,
        model=resolved_model,
        prompt_text=spec.prompt_text,
        images=spec.images,
        audio=spec.audio,
        proxy_url=proxy_url,
        cancellable=True,
        provider=provider,
        max_tokens=max_tokens,
        config=spec.config,
        for_speech=for_speech,
        model_override=spec.model,
    )
    _track_bothub_worker(worker)

    if spec.state is not None:
        spec.state.worker = worker
        spec.state.toast = toast

    request_finished = False

    def finalize_toast() -> None:
        if toast is None:
            return
        toast.mark_completed()
        if spec.state is not None and spec.state.toast is not None:
            spec.state.toast.close()
            spec.state.toast = None
        else:
            toast.close()

    def on_worker_success(response_text: str) -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        _release_bothub_worker(worker)
        if spec.state is not None:
            spec.state.worker = None
        spec.on_success(response_text)

    def on_worker_error(message: str) -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        _release_bothub_worker(worker)
        # Leave state.worker set until retry dialog closes so is_busy stays true.
        _offer_retry_or_finish(spec, cancelled=False, message=message)

    def on_worker_cancelled() -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        _release_bothub_worker(worker)
        _offer_retry_or_finish(
            spec,
            cancelled=True,
            message="Request cancelled by user.",
        )

    if toast is not None:
        toast.cancel_requested.connect(worker.cancel)

    worker.finished_success.connect(on_worker_success)
    worker.finished_error.connect(on_worker_error)
    worker.finished_cancelled.connect(on_worker_cancelled)
    worker.start()
    return True


def _track_bothub_worker(worker: BothubChatWorker) -> None:
    """Register a worker so it is not garbage-collected while the thread runs."""
    _active_bothub_workers.append(worker)


# Keep strong refs until the thread finishes; otherwise Python GC can destroy QThread early.
_active_bothub_workers: list[BothubChatWorker] = []
