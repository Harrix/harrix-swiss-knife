---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `worker.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BothubChatWorker`](#️-class-bothubchatworker)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `cancel`](#️-method-cancel)
  - [⚙️ Method `run`](#️-method-run)
  - [⚙️ Method `_store_connection`](#️-method-_store_connection)

</details>

## 🏛️ Class `BothubChatWorker`

```python
class BothubChatWorker(QThread)
```

Worker thread for BotHub chat completion API calls.

Attributes:

- `finished_success` (`Signal`): Emitted with assistant text on success.
- `finished_error` (`Signal`): Emitted with error message on failure.
- `finished_cancelled` (`Signal`): Emitted when the request is cancelled.
- `should_stop` (`bool`): Flag to request early termination.

<details>
<summary>Code:</summary>

```python
class BothubChatWorker(QThread):

    finished_success: Signal = Signal(str)
    finished_error: Signal = Signal(str)
    finished_cancelled: Signal = Signal()

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        prompt_text: str,
        image: tuple[bytes, str] | None = None,
        audio: tuple[bytes, str] | None = None,
        proxy_url: str | None = None,
        cancellable: bool = False,
    ) -> None:
        """Initialize the worker.

        Args:

        - `api_key` (`str`): BotHub API key.
        - `base_url` (`str`): BotHub API base URL.
        - `model` (`str`): Model name.
        - `prompt_text` (`str`): Full prompt text.
        - `image` (`tuple[bytes, str] | None`): Optional image bytes and MIME type.
        - `audio` (`tuple[bytes, str] | None`): Optional audio bytes and MIME type.
        - `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS.
        - `cancellable` (`bool`): Enable cancellable HTTP transport when True.

        """
        super().__init__()
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._prompt_text = prompt_text
        self._image = image
        self._audio = audio
        self._proxy_url = proxy_url
        self._cancellable = cancellable
        self.should_stop = False
        self._conn: http.client.HTTPConnection | None = None

    def cancel(self) -> None:
        """Request cancellation and close the active HTTP connection."""
        self.should_stop = True
        conn = self._conn
        if conn is not None:
            conn.close()

    def run(self) -> None:
        """Execute the API request."""
        if self.should_stop:
            self.finished_cancelled.emit()
            return

        should_cancel = (lambda: self.should_stop) if self._cancellable else None
        on_connection = self._store_connection if self._cancellable else None

        try:
            result = chat_completion(
                api_key=self._api_key,
                base_url=self._base_url,
                model=self._model,
                text=self._prompt_text,
                image=self._image,
                audio=self._audio,
                proxy_url=self._proxy_url,
                should_cancel=should_cancel,
                on_connection=on_connection,
            )
        except RequestCancelledError:
            self.finished_cancelled.emit()
            return
        except BotHubApiError as exc:
            if self.should_stop:
                self.finished_cancelled.emit()
                return
            self.finished_error.emit(str(exc))
            return
        except Exception as exc:
            if self.should_stop:
                self.finished_cancelled.emit()
                return
            self.finished_error.emit(str(exc))
            return
        finally:
            self._conn = None

        if self.should_stop:
            self.finished_cancelled.emit()
            return
        self.finished_success.emit(result)

    def _store_connection(self, conn: http.client.HTTPConnection) -> None:
        self._conn = conn
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Initialize the worker.

Args:

- `api_key` (`str`): BotHub API key.
- `base_url` (`str`): BotHub API base URL.
- `model` (`str`): Model name.
- `prompt_text` (`str`): Full prompt text.
- `image` (`tuple[bytes, str] | None`): Optional image bytes and MIME type.
- `audio` (`tuple[bytes, str] | None`): Optional audio bytes and MIME type.
- `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS.
- `cancellable` (`bool`): Enable cancellable HTTP transport when True.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        prompt_text: str,
        image: tuple[bytes, str] | None = None,
        audio: tuple[bytes, str] | None = None,
        proxy_url: str | None = None,
        cancellable: bool = False,
    ) -> None:
        super().__init__()
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._prompt_text = prompt_text
        self._image = image
        self._audio = audio
        self._proxy_url = proxy_url
        self._cancellable = cancellable
        self.should_stop = False
        self._conn: http.client.HTTPConnection | None = None
```

</details>

### ⚙️ Method `cancel`

```python
def cancel(self) -> None
```

Request cancellation and close the active HTTP connection.

<details>
<summary>Code:</summary>

```python
def cancel(self) -> None:
        self.should_stop = True
        conn = self._conn
        if conn is not None:
            conn.close()
```

</details>

### ⚙️ Method `run`

```python
def run(self) -> None
```

Execute the API request.

<details>
<summary>Code:</summary>

```python
def run(self) -> None:
        if self.should_stop:
            self.finished_cancelled.emit()
            return

        should_cancel = (lambda: self.should_stop) if self._cancellable else None
        on_connection = self._store_connection if self._cancellable else None

        try:
            result = chat_completion(
                api_key=self._api_key,
                base_url=self._base_url,
                model=self._model,
                text=self._prompt_text,
                image=self._image,
                audio=self._audio,
                proxy_url=self._proxy_url,
                should_cancel=should_cancel,
                on_connection=on_connection,
            )
        except RequestCancelledError:
            self.finished_cancelled.emit()
            return
        except BotHubApiError as exc:
            if self.should_stop:
                self.finished_cancelled.emit()
                return
            self.finished_error.emit(str(exc))
            return
        except Exception as exc:
            if self.should_stop:
                self.finished_cancelled.emit()
                return
            self.finished_error.emit(str(exc))
            return
        finally:
            self._conn = None

        if self.should_stop:
            self.finished_cancelled.emit()
            return
        self.finished_success.emit(result)
```

</details>

### ⚙️ Method `_store_connection`

```python
def _store_connection(self, conn: http.client.HTTPConnection) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _store_connection(self, conn: http.client.HTTPConnection) -> None:
        self._conn = conn
```

</details>
