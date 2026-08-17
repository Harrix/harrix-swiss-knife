"""Tests for action-card copy menu labels."""

from harrix_swiss_knife.cli_menu import (
    COPY_ACTION_CLASS_MENU_PREFIX,
    COPY_ACTION_NAME_MENU_PREFIX,
    COPY_ACTION_NAME_PREVIEW_MAX_LEN,
    COPY_ACTION_PATH_MENU_PREFIX,
    format_copy_action_class_menu_label,
    format_copy_action_name_menu_label,
    format_copy_action_path_menu_label,
    truncate_action_name_preview,
)


def test_format_copy_action_class_and_path_show_full_value() -> None:
    assert format_copy_action_class_menu_label("OnRecognizeTextWithAI") == (
        f"{COPY_ACTION_CLASS_MENU_PREFIX}OnRecognizeTextWithAI"
    )
    path = "src/harrix_swiss_knife/actions/images/recognize_text_with_ai.py"
    assert format_copy_action_path_menu_label(path) == f"{COPY_ACTION_PATH_MENU_PREFIX}{path}"


def test_format_copy_action_name_shortens_long_text() -> None:
    name = "Recognize text from selected images via AI and show it as Markdown"
    preview = truncate_action_name_preview(name)
    assert preview.endswith("…")
    assert len(preview) < len(name)
    assert format_copy_action_name_menu_label(name) == f"{COPY_ACTION_NAME_MENU_PREFIX}{preview}"


def test_truncate_action_name_preview_keeps_short_text() -> None:
    name = "Open config.json"
    assert len(name) <= COPY_ACTION_NAME_PREVIEW_MAX_LEN
    assert truncate_action_name_preview(name) == name
    assert format_copy_action_name_menu_label(name) == f"{COPY_ACTION_NAME_MENU_PREFIX}{name}"
