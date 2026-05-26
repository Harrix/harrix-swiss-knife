"""Re-export text-fix BotHub helpers from integrations.bothub (backward compatibility)."""

from harrix_swiss_knife.integrations.bothub.config import API_KEY_MISSING_MSG
from harrix_swiss_knife.integrations.bothub.config import get_connection_params as get_bothub_connection_params
from harrix_swiss_knife.integrations.bothub.text_fix import (
    PROMPT_MISSING_MSG,
    build_text_fix_prompt,
    fix_text_sync,
    get_text_fix_prompt_template,
)

__all__ = [
    "API_KEY_MISSING_MSG",
    "PROMPT_MISSING_MSG",
    "build_text_fix_prompt",
    "fix_text_sync",
    "get_bothub_connection_params",
    "get_text_fix_prompt_template",
]
