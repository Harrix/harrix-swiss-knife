"""Build BotHub prompts from config templates."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.integrations.bothub.config import API_KEY_MISSING_MSG, validate_api_key


def build_prompt(
    config: dict[str, Any],
    prompt_key: str,
    replacements: dict[str, str],
    *,
    prompt_display_name: str | None = None,
) -> str:
    """Build full prompt from config template and placeholder replacements.

    Placeholders in the template use ``{{NAME}}``; keys in ``replacements`` are without braces.

    Raises:

    - `ValueError`: If prompt or API key is not configured.

    """
    template = get_prompt_template(config, prompt_key)
    if not template:
        label = prompt_display_name or prompt_key
        msg = f"Prompt {label} is not configured in config.json."
        raise ValueError(msg)

    if validate_api_key(config, show_message=False) is None:
        raise ValueError(API_KEY_MISSING_MSG)

    prompt_text = template
    for key, value in replacements.items():
        prompt_text = prompt_text.replace(f"{{{{{key}}}}}", value)
    return prompt_text


def get_prompt_template(config: dict[str, Any], prompt_key: str) -> str | None:
    """Return stripped prompt template for ``prompt_key``, or None if missing."""
    prompts_cfg = config.get("prompts") or {}
    template = str(prompts_cfg.get(prompt_key, "")).strip()
    return template or None
