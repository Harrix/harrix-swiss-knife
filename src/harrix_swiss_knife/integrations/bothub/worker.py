"""Background worker for BotHub chat completion requests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Signal

from harrix_swiss_knife.integrations.bothub_client import (
    BotHubApiError,
    RequestCancelledError,
    chat_completion,
)

if TYPE_CHECKING:
    import http.client
    from collections.abc import Sequence


class BothubChatWorker(QThread):
    """Worker thread for BotHub chat completion API calls.

    Attributes:

    - `finished_success` (`Signal`): Emitted with assistant text on success.
    - `finished_error` (`Signal`): Emitted with error message on failure.
    - `finished_cancelled` (`Signal`): Emitted when the request is cancelled.
    - `should_stop` (`bool`): Flag to request early termination.

    """

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
        images: Sequence[tuple[bytes, str]] | None = None,
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
        - `images` (`Sequence[tuple[bytes, str]] | None`): Optional vision inputs.
        - `image` (`tuple[bytes, str] | None`): Optional single image (merged into `images`).
        - `audio` (`tuple[bytes, str] | None`): Optional audio bytes and MIME type.
        - `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS.
        - `cancellable` (`bool`): Enable cancellable HTTP transport when `True`.

        """
        super().__init__()
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._prompt_text = prompt_text
        image_list = list(images or [])
        if image is not None:
            image_list.append(image)
        self._images = image_list or None
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
                images=self._images,
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
