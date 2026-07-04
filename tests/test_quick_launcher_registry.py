"""Tests for quick launcher registry and global hotkey parsing."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.images.optimize_clipboard import OnOptimizeClipboard
from harrix_swiss_knife.actions.images.optimize_clipboard_dialog import OnOptimizeClipboardDialog
from harrix_swiss_knife.actions.text.fix_speech_with_ai import OnFixSpeechWithAI
from harrix_swiss_knife.actions.text.fix_text_with_ai import OnFixTextWithAI
from harrix_swiss_knife.actions.text.fix_text_with_ai_from_clipboard import OnFixTextWithAIFromClipboard
from harrix_swiss_knife.global_hotkey import MOD_ALT, MOD_CONTROL, parse_hotkey_string
from harrix_swiss_knife.main import get_menu_structure
from harrix_swiss_knife.quick_launcher_registry import collect_quick_launcher_actions, iter_menu_structure


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_collect_quick_launcher_actions_finds_five_marked_actions() -> None:
    actions = collect_quick_launcher_actions(get_menu_structure())
    assert len(actions) == 5
    assert {cls.__name__ for cls in actions} == {
        "OnFixTextWithAI",
        "OnFixSpeechWithAI",
        "OnFixTextWithAIFromClipboard",
        "OnOptimizeClipboard",
        "OnOptimizeClipboardDialog",
    }


def test_collect_quick_launcher_actions_sorted_by_title() -> None:
    actions = collect_quick_launcher_actions(get_menu_structure())
    titles = [cls.title for cls in actions]
    assert titles == sorted(titles)


def test_iter_menu_structure_includes_nested_text_actions() -> None:
    classes = list(iter_menu_structure(get_menu_structure()))
    assert OnFixTextWithAI in classes
    assert OnFixSpeechWithAI in classes
    assert OnOptimizeClipboard in classes


def test_parse_hotkey_string_ctrl_alt_space(qapp: QApplication) -> None:  # noqa: ARG001
    modifiers, vk = parse_hotkey_string("Ctrl+Alt+Space")
    assert modifiers & MOD_CONTROL
    assert modifiers & MOD_ALT
    assert vk == 0x20


def test_parse_hotkey_string_rejects_empty(qapp: QApplication) -> None:  # noqa: ARG001
    with pytest.raises(ValueError, match="empty"):
        parse_hotkey_string("")
