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
- [🔧 Function `_cleanup_state`](#-function-_cleanup_state)

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
    toast: toast_countdown_notification.ToastCountdownNotification | None = None
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

    api_key, base_url, model, proxy_url = get_connection_params(config)

    toast = toast_countdown_notification.ToastCountdownNotification(toast_message)
    toast.start_countdown()

    worker = BothubChatWorker(
        api_key=api_key,
        base_url=base_url,
        model=model,
        prompt_text=prompt_text,
        image=image,
        proxy_url=proxy_url,
    )

    if state is not None:
        state.worker = worker
        state.toast = toast

    def on_worker_success(response_text: str) -> None:
        _cleanup_state(state)
        on_success(response_text)

    def on_worker_error(message: str) -> None:
        _cleanup_state(state)
        if on_error is not None:
            on_error(message)
        else:
            message_box.critical(parent, "BotHub Error", message)

    worker.finished_success.connect(on_worker_success)
    worker.finished_error.connect(on_worker_error)
    worker.start()
    return True
```

</details>

## 🔧 Function `_cleanup_state`

```python
def _cleanup_state(state: BothubRequestState | None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _cleanup_state(state: BothubRequestState | None) -> None:
    if state is None:
        return
    if state.toast is not None:
        state.toast.close()
        state.toast = None
    if state.worker is not None:
        state.worker.deleteLater()
        state.worker = None
```

</details>
