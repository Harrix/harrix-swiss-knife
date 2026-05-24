"""Background worker for BotHub chat completion requests."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from harrix_swiss_knife.integrations.bothub_client import BotHubApiError, chat_completion


class BothubChatWorker(QThread):
    """Worker thread for BotHub chat completion API calls.

    Attributes:

    - `finished_success` (`Signal`): Emitted with assistant text on success.
    - `finished_error` (`Signal`): Emitted with error message on failure.
    - `should_stop` (`bool`): Flag to request early termination before HTTP call.

    """

    finished_success: Signal = Signal(str)
    finished_error: Signal = Signal(str)

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        prompt_text: str,
        image: tuple[bytes, str] | None = None,
    ) -> None:
        """Initialize the worker.

        Args:

        - `api_key` (`str`): BotHub API key.
        - `base_url` (`str`): BotHub API base URL.
        - `model` (`str`): Model name.
        - `prompt_text` (`str`): Full prompt text.
        - `image` (`tuple[bytes, str] | None`): Optional image bytes and MIME type.

        """
        super().__init__()
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._prompt_text = prompt_text
        self._image = image
        self.should_stop = False

    def run(self) -> None:
        """Execute the API request."""
        if self.should_stop:
            return
        try:
            result = chat_completion(
                api_key=self._api_key,
                base_url=self._base_url,
                model=self._model,
                text=self._prompt_text,
                image=self._image,
            )
        except BotHubApiError as exc:
            self.finished_error.emit(str(exc))
            return
        except Exception as exc:
            self.finished_error.emit(str(exc))
            return
        if not self.should_stop:
            self.finished_success.emit(result)
