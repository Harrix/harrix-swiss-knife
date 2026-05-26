"""BotHub integration: config, prompts, Qt async runner, and domain helpers."""

from harrix_swiss_knife.integrations.bothub.config import (
    API_KEY_MISSING_MSG,
    get_connection_params,
    validate_api_key,
)
from harrix_swiss_knife.integrations.bothub.network import qnetwork_proxy_to_url, resolve_bothub_proxy_url
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template
from harrix_swiss_knife.integrations.bothub.qt_runner import BothubRequestState, run_bothub_request
from harrix_swiss_knife.integrations.bothub.text_fix import (
    PROMPT_MISSING_MSG,
    build_text_fix_prompt,
    fix_text_sync,
    get_text_fix_prompt_template,
)
from harrix_swiss_knife.integrations.bothub.worker import BothubChatWorker

__all__ = [
    "API_KEY_MISSING_MSG",
    "PROMPT_MISSING_MSG",
    "BothubChatWorker",
    "BothubRequestState",
    "build_prompt",
    "build_text_fix_prompt",
    "fix_text_sync",
    "get_connection_params",
    "get_prompt_template",
    "get_text_fix_prompt_template",
    "qnetwork_proxy_to_url",
    "resolve_bothub_proxy_url",
    "run_bothub_request",
    "validate_api_key",
]
