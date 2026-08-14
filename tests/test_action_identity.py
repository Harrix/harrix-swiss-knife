"""Tests for action identity clipboard text (name, class, relative path)."""

from harrix_swiss_knife.action_identity import (
    action_identity_name,
    action_relative_source_path,
    format_action_identity_text,
)
from harrix_swiss_knife.actions.images.recognize_text_with_ai import OnRecognizeTextWithAI


class _TitleOnlyAction:
    title = "Open `config.json`"


def test_action_identity_name_uses_docstring_without_trailing_period() -> None:
    assert action_identity_name(OnRecognizeTextWithAI) == (
        "Recognize text from selected images via AI and show it as Markdown"
    )


def test_action_identity_name_falls_back_to_stripped_title() -> None:
    assert action_identity_name(_TitleOnlyAction) == "Open config.json"


def test_action_relative_source_path_is_posix_under_src() -> None:
    path = action_relative_source_path(OnRecognizeTextWithAI)
    assert path == "src/harrix_swiss_knife/actions/images/recognize_text_with_ai.py"


def test_format_action_identity_text_matches_card_copy_example() -> None:
    assert format_action_identity_text(OnRecognizeTextWithAI) == (
        "Recognize text from selected images via AI and show it as Markdown\n"
        "OnRecognizeTextWithAI\n"
        "src/harrix_swiss_knife/actions/images/recognize_text_with_ai.py"
    )
