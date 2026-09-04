"""BotHub integration: config, prompts, Qt async runner, and domain helpers."""

from harrix_swiss_knife.integrations.bothub.config import (
    API_KEY_MISSING_MSG,
    get_active_provider,
    get_connection_params,
    get_max_image_side,
    get_speech_model,
    validate_api_key,
)
from harrix_swiss_knife.integrations.bothub.errors import show_bothub_prompt_build_error
from harrix_swiss_knife.integrations.bothub.image import (
    image_bytes_and_mime,
    image_mime_from_suffix,
    qimage_bytes_and_mime,
)
from harrix_swiss_knife.integrations.bothub.image_ocr import (
    PROMPT_MISSING_MSG as IMAGE_OCR_PROMPT_MISSING_MSG,
)
from harrix_swiss_knife.integrations.bothub.image_ocr import (
    build_image_ocr_prompt,
    get_image_ocr_prompt_template,
)
from harrix_swiss_knife.integrations.bothub.image_ocr_translate import (
    PROMPT_MISSING_MSG as IMAGE_OCR_TRANSLATE_PROMPT_MISSING_MSG,
)
from harrix_swiss_knife.integrations.bothub.image_ocr_translate import (
    build_image_ocr_translate_prompt,
    get_image_ocr_translate_prompt_template,
)
from harrix_swiss_knife.integrations.bothub.prompts import build_prompt, get_prompt_template
from harrix_swiss_knife.integrations.bothub.qt_runner import (
    BothubRequestSpec,
    BothubRequestState,
    run_bothub_request,
    run_bothub_request_blocking,
)
from harrix_swiss_knife.integrations.bothub.speech import (
    audio_bytes_and_mime,
    audio_format_from_suffix,
    build_transcription_prompt,
)
from harrix_swiss_knife.integrations.bothub.text_fix import (
    CLIPBOARD_PROMPT_MISSING_MSG,
    PROMPT_MISSING_MSG,
    build_text_fix_from_clipboard_prompt,
    build_text_fix_prompt,
    fix_text_sync,
    get_text_fix_from_clipboard_prompt_template,
    get_text_fix_prompt_template,
)
from harrix_swiss_knife.integrations.bothub.text_rewrite import (
    build_text_rewrite_prompt,
    get_text_rewrite_prompt_template,
    rewrite_text_sync,
)
from harrix_swiss_knife.integrations.bothub.worker import BothubChatWorker

__all__ = [
    "API_KEY_MISSING_MSG",
    "CLIPBOARD_PROMPT_MISSING_MSG",
    "IMAGE_OCR_PROMPT_MISSING_MSG",
    "IMAGE_OCR_TRANSLATE_PROMPT_MISSING_MSG",
    "PROMPT_MISSING_MSG",
    "BothubChatWorker",
    "BothubRequestSpec",
    "BothubRequestState",
    "audio_bytes_and_mime",
    "audio_format_from_suffix",
    "build_image_ocr_prompt",
    "build_image_ocr_translate_prompt",
    "build_prompt",
    "build_text_fix_from_clipboard_prompt",
    "build_text_fix_prompt",
    "build_text_rewrite_prompt",
    "build_transcription_prompt",
    "fix_text_sync",
    "get_active_provider",
    "get_connection_params",
    "get_image_ocr_prompt_template",
    "get_image_ocr_translate_prompt_template",
    "get_max_image_side",
    "get_prompt_template",
    "get_speech_model",
    "get_text_fix_from_clipboard_prompt_template",
    "get_text_fix_prompt_template",
    "get_text_rewrite_prompt_template",
    "image_bytes_and_mime",
    "image_mime_from_suffix",
    "qimage_bytes_and_mime",
    "qnetwork_proxy_to_url",
    "resolve_bothub_proxy_url",
    "rewrite_text_sync",
    "run_bothub_request",
    "run_bothub_request_blocking",
    "show_bothub_prompt_build_error",
    "validate_api_key",
]
