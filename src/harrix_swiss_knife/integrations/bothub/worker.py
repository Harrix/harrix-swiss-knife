"""Background worker for AI chat completion requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QThread, Signal

from harrix_swiss_knife.integrations.ai.bothub_failover import prepare_bothub_router
from harrix_swiss_knife.integrations.ai.config import get_provider_settings
from harrix_swiss_knife.integrations.bothub.config import (
    get_active_provider,
    get_connection_params,
    get_proxy_url,
)
from harrix_swiss_knife.integrations.bothub_client import (
    BotHubApiError,
    RequestCancelledError,
    chat_completion,
)

if TYPE_CHECKING:
    import http.client
    from collections.abc import Sequence

    from harrix_swiss_knife.integrations.ai.config import ProviderName


class BothubChatWorker(QThread):
    """Worker thread for AI chat completion API calls.

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
        provider: ProviderName = "bothub",
        max_tokens: int | None = None,
        config: dict[str, Any] | None = None,
        for_speech: bool = False,
        model_override: str | None = None,
    ) -> None:
        """Initialize the worker.

        Args:

        - `api_key` (`str`): Provider API key.
        - `base_url` (`str`): Provider API base URL.
        - `model` (`str`): Model name.
        - `prompt_text` (`str`): Full prompt text.
        - `images` (`Sequence[tuple[bytes, str]] | None`): Optional vision inputs.
        - `image` (`tuple[bytes, str] | None`): Optional single image (merged into `images`).
        - `audio` (`tuple[bytes, str] | None`): Optional audio bytes and MIME type.
        - `proxy_url` (`str | None`): Optional HTTP proxy URL for HTTPS.
        - `cancellable` (`bool`): Enable cancellable HTTP transport when `True`.
        - `provider`: Active AI provider ID.
        - `max_tokens`: Anthropic max tokens override.
        - `config`: When set, probe the BotHub router and refresh connection
          params on this thread before the request.
        - `for_speech`: Use the speech provider when `config` is set.
        - `model_override`: Keep this model after router failover. Defaults to `None`.

        """
        super().__init__()
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._model_override = model_override
        self._prompt_text = prompt_text
        image_list = list(images or [])
        if image is not None:
            image_list.append(image)
        self._images = image_list or None
        self._audio = audio
        self._proxy_url = proxy_url
        self._cancellable = cancellable
        self._provider = provider
        self._max_tokens = max_tokens
        self._config = config
        self._for_speech = for_speech
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

        self._prepare_router_connection()
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
                provider=self._provider,
                max_tokens=self._max_tokens,
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

    def _prepare_router_connection(self) -> None:
        """Probe BotHub failover and refresh keys/URLs off the UI thread."""
        config = self._config
        if config is None:
            return
        prepare_bothub_router(config, for_speech=self._for_speech, proxy_url=get_proxy_url(config))
        api_key, base_url, default_model, proxy_url = get_connection_params(config, for_speech=self._for_speech)
        self._api_key = api_key
        self._base_url = base_url
        self._model = self._model_override if self._model_override is not None else default_model
        self._proxy_url = proxy_url
        self._provider = get_active_provider(config, for_speech=self._for_speech)
        settings = get_provider_settings(config, self._provider)
        max_tokens_raw = settings.get("max_tokens")
        self._max_tokens = int(max_tokens_raw) if max_tokens_raw is not None else None

    def _store_connection(self, conn: http.client.HTTPConnection) -> None:
        self._conn = conn
