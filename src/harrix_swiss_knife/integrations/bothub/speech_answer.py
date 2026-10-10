"""BotHub speech Ask AI answer (prompt speech_answer)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.chat_failover import chat_completion_with_bothub_failover
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template

PROMPT_MISSING_MSG = "Prompt speech_answer is not configured in config.json."


def answer_speech_question_sync(input_text: str, config: dict[str, Any]) -> str:
    """Send a spoken question to BotHub synchronously and return the answer.

    Raises:

    - `ValueError`: Configuration errors (prompt or API key).
    - `BotHubApiError`: API or network failure.

    """
    return chat_completion_with_bothub_failover(config, build_speech_answer_prompt(input_text, config))


def build_speech_answer_prompt(input_text: str, config: dict[str, Any]) -> str:
    """Build BotHub prompt that answers a spoken question.

    Raises:

    - `ValueError`: If prompt template or API key is not configured.

    """
    return build_prompt(
        config,
        "speech_answer",
        {"TEXT": input_text},
        prompt_display_name="speech_answer",
    )


def get_speech_answer_prompt_template(config: dict[str, Any]) -> str | None:
    """Return stripped `prompts.speech_answer` template, or `None` if missing."""
    return get_prompt_template(config, "speech_answer")
