"""Run BotHub chat with one automatic retry on the other site after API failure."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.integrations.ai.bothub_failover import (
    is_bothub_api_failover_error,
    prepare_bothub_router,
    switch_bothub_router_after_api_failure,
)
from harrix_swiss_knife.integrations.ai.config import is_bothub_router
from harrix_swiss_knife.integrations.bothub.config import get_active_provider, get_connection_params, get_proxy_url
from harrix_swiss_knife.integrations.bothub_client import BotHubApiError, chat_completion

if TYPE_CHECKING:
    from collections.abc import Sequence


def chat_completion_with_bothub_failover(
    config: dict[str, Any],
    prompt_text: str,
    *,
    for_speech: bool = False,
    images: Sequence[tuple[bytes, str]] | None = None,
    audio: tuple[bytes, str] | None = None,
) -> str:
    """Prepare the BotHub router, call chat, and retry once on the other site if needed.

    Raises:

    - `BotHubApiError`: When both attempts fail (or failover does not apply).

    """
    prepare_bothub_router(config, for_speech=for_speech, proxy_url=get_proxy_url(config))
    provider = get_active_provider(config, for_speech=for_speech)
    api_key, base_url, model, proxy_url = get_connection_params(config, for_speech=for_speech)
    try:
        return chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=prompt_text,
            images=images,
            audio=audio,
            proxy_url=proxy_url,
            provider=provider,
        )
    except BotHubApiError as exc:
        if not is_bothub_router(provider) or not is_bothub_api_failover_error(str(exc)):
            raise
        if switch_bothub_router_after_api_failure(config, for_speech=for_speech) is None:
            raise
        provider = get_active_provider(config, for_speech=for_speech)
        api_key, base_url, model, proxy_url = get_connection_params(config, for_speech=for_speech)
        return chat_completion(
            api_key=api_key,
            base_url=base_url,
            model=model,
            text=prompt_text,
            images=images,
            audio=audio,
            proxy_url=proxy_url,
            provider=provider,
        )
