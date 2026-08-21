---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_runner.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BothubRequestSpec`](#%EF%B8%8F-class-bothubrequestspec)
- [🏛️ Class `BothubRequestState`](#%EF%B8%8F-class-bothubrequeststate)
- [🔧 Function `run_bothub_request`](#-function-run_bothub_request)
- [🔧 Function `run_bothub_request_blocking`](#-function-run_bothub_request_blocking)

</details>

## 🏛️ Class `BothubRequestSpec`

```python
class BothubRequestSpec
```

Everything needed to start or retry one BotHub request.

<details>
<summary>Code:</summary>

```python
class BothubRequestSpec:

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
```

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
def run_bothub_request(parent: QWidget | None, config: dict[str, Any], prompt_text: str, on_success: Callable[[str], None], *, images: list[tuple[bytes, str]] | None = None, image: tuple[bytes, str] | None = None, audio: tuple[bytes, str] | None = None, model: str | None = None, toast_message: str = 'Requesting AI…', is_busy: Callable[[], bool] | None = None, state: BothubRequestState | None = None, on_error: Callable[[str], None] | None = None, on_cancelled: Callable[[], None] | None = None, offer_retry: bool = True) -> bool
```

Validate config, show toast, start worker. Returns `True` if the request started.

Args:

- `parent`: Parent widget for message boxes.
- [`config`](../../actions/common/base.g.md#%EF%B8%8F-method-config-property): Application config dict.
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

<details>
<summary>Code:</summary>

```python
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
) -> bool:
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
    )
    return _start_bothub_request(spec)
```

</details>

## 🔧 Function `run_bothub_request_blocking`

```python
def run_bothub_request_blocking(parent: QWidget | None, config: dict[str, Any], prompt_text: str, *, images: list[tuple[bytes, str]] | None = None, image: tuple[bytes, str] | None = None, audio: tuple[bytes, str] | None = None, model: str | None = None, toast_message: str = 'Requesting AI…', state: BothubRequestState | None = None, offer_retry: bool = True) -> str | None
```

Run an AI request and block the UI thread until it finishes.

Returns assistant text on success, or `None` on cancel / validation failure.
When `offer_retry` is `True`, errors and cancels show a Retry dialog first.
Errors after Close are not shown again (already shown in the retry dialog).

<details>
<summary>Code:</summary>

```python
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
```

</details>
