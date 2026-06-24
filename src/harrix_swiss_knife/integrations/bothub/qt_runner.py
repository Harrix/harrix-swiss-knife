"""Qt helpers: toast + background worker for BotHub requests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife import toast_cancellable_http_notification, toast_notification_base
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub.config import get_connection_params, validate_api_key
from harrix_swiss_knife.integrations.bothub.worker import BothubChatWorker

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget


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
    image: tuple[bytes, str] | None = None,
    toast_message: str = "Requesting BotHub…",
    is_busy: Callable[[], bool] | None = None,
    state: BothubRequestState | None = None,
    on_error: Callable[[str], None] | None = None,
) -> bool:
    """Validate config, show toast, start worker. Returns True if the request started.

    Args:

    - `parent`: Parent widget for message boxes.
    - `config`: Application config dict.
    - `prompt_text`: Full prompt to send.
    - `on_success`: Called with assistant text when the request succeeds.
    - `image`: Optional vision input ``(bytes, mime_type)``.
    - `toast_message`: Toast label while waiting.
    - `is_busy`: If provided and returns True, the request is not started.
    - `state`: Optional holder updated with worker/toast refs; cleared on completion.
    - `on_error`: If set, called with the error message instead of the default critical dialog.

    """
    if is_busy is not None and is_busy():
        return False

    api_key = validate_api_key(config, parent=parent)
    if api_key is None:
        return False

    api_key, base_url, model, proxy_url = get_connection_params(config)

    toast = toast_cancellable_http_notification.ToastCancellableHttpNotification(toast_message)
    toast.start_countdown()

    worker = BothubChatWorker(
        api_key=api_key,
        base_url=base_url,
        model=model,
        prompt_text=prompt_text,
        image=image,
        proxy_url=proxy_url,
        cancellable=True,
    )

    if state is not None:
        state.worker = worker
        state.toast = toast

    request_finished = False

    def finalize_toast() -> None:
        toast.mark_completed()
        if state is not None and state.toast is not None:
            state.toast.close()
            state.toast = None
        else:
            toast.close()

    def on_worker_success(response_text: str) -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        if state is not None and state.worker is not None:
            state.worker.deleteLater()
            state.worker = None
        on_success(response_text)

    def on_worker_error(message: str) -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        if state is not None and state.worker is not None:
            state.worker.deleteLater()
            state.worker = None
        if on_error is not None:
            on_error(message)
        else:
            message_box.critical(parent, "BotHub Error", message)

    def on_worker_cancelled() -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        if state is not None and state.worker is not None:
            state.worker.deleteLater()
            state.worker = None
        print("❌ Request cancelled by user.")

    toast.cancel_requested.connect(worker.cancel)

    worker.finished_success.connect(on_worker_success)
    worker.finished_error.connect(on_worker_error)
    worker.finished_cancelled.connect(on_worker_cancelled)
    worker.start()
    return True
