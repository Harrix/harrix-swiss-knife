---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_runner.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BothubRequestState`](#️-class-bothubrequeststate)
- [🔧 Function `run_bothub_request`](#-function-run_bothub_request)
- [🔧 Function `_release_bothub_worker`](#-function-_release_bothub_worker)
- [🔧 Function `_track_bothub_worker`](#-function-_track_bothub_worker)

</details>

## 🏛️ Class `BothubRequestState`

```python
class BothubRequestState
```

Mutable holder for an in-flight BotHub request (worker + toast).

<details>
<summary>Code:</summary>

```python
class BothubRequestState:

    worker: BothubChatWorker | None = None
    toast: toast_notification_base.ToastNotificationBase | None = None
```

</details>

## 🔧 Function `run_bothub_request`

```python
def run_bothub_request(parent: QWidget | None, config: dict[str, Any], prompt_text: str, on_success: Callable[[str], None]) -> bool
```

Validate config, show toast, start worker. Returns True if the request started.

Args:

- `parent`: Parent widget for message boxes.
- `config`: Application config dict.
- `prompt_text`: Full prompt to send.
- `on_success`: Called with assistant text when the request succeeds.
- `image`: Optional vision input `(bytes, mime_type)`.
- `audio`: Optional speech input `(bytes, mime_type)`.
- `model`: Optional model override; defaults to `bothub.model` from config.
- `toast_message`: Toast label while waiting.
- `is_busy`: If provided and returns True, the request is not started.
- `state`: Optional holder updated with worker/toast refs; cleared on completion.
- `on_error`: If set, called with the error message instead of the default critical dialog.

<details>
<summary>Code:</summary>

```python
def run_bothub_request(
    parent: QWidget | None,
    config: dict[str, Any],
    prompt_text: str,
    on_success: Callable[[str], None],
    *,
    image: tuple[bytes, str] | None = None,
    audio: tuple[bytes, str] | None = None,
    model: str | None = None,
    toast_message: str = "Requesting BotHub…",
    is_busy: Callable[[], bool] | None = None,
    state: BothubRequestState | None = None,
    on_error: Callable[[str], None] | None = None,
) -> bool:
    if is_busy is not None and is_busy():
        return False

    api_key = validate_api_key(config, parent=parent)
    if api_key is None:
        return False

    api_key, base_url, default_model, proxy_url = get_connection_params(config)
    resolved_model = model if model is not None else default_model

    toast = toast_cancellable_http_notification.ToastCancellableHttpNotification(toast_message)
    toast.start_countdown()

    worker = BothubChatWorker(
        api_key=api_key,
        base_url=base_url,
        model=resolved_model,
        prompt_text=prompt_text,
        image=image,
        audio=audio,
        proxy_url=proxy_url,
        cancellable=True,
    )
    _track_bothub_worker(worker)

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
        _release_bothub_worker(worker)
        if state is not None:
            state.worker = None
        on_success(response_text)

    def on_worker_error(message: str) -> None:
        nonlocal request_finished
        if request_finished:
            return
        request_finished = True
        finalize_toast()
        _release_bothub_worker(worker)
        if state is not None:
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
        _release_bothub_worker(worker)
        if state is not None:
            state.worker = None
        print("❌ Request cancelled by user.")

    toast.cancel_requested.connect(worker.cancel)

    worker.finished_success.connect(on_worker_success)
    worker.finished_error.connect(on_worker_error)
    worker.finished_cancelled.connect(on_worker_cancelled)
    worker.start()
    return True
```

</details>

## 🔧 Function `_release_bothub_worker`

```python
def _release_bothub_worker(worker: BothubChatWorker) -> None
```

Drop the tracking ref and schedule safe Qt deletion after the thread stops.

<details>
<summary>Code:</summary>

```python
def _release_bothub_worker(worker: BothubChatWorker) -> None:
    with suppress(ValueError):
        _active_bothub_workers.remove(worker)
    worker.deleteLater()
```

</details>

## 🔧 Function `_track_bothub_worker`

```python
def _track_bothub_worker(worker: BothubChatWorker) -> None
```

Register a worker so it is not garbage-collected while the thread runs.

<details>
<summary>Code:</summary>

```python
def _track_bothub_worker(worker: BothubChatWorker) -> None:
    _active_bothub_workers.append(worker)
```

</details>
