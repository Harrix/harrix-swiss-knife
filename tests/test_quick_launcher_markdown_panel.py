"""Tests for quick launcher markdown panel integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import harrix_pylib as h

from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.actions.quick_launcher.context import QuickLauncherContext
from harrix_swiss_knife.menu_structure import get_menu_structure

if TYPE_CHECKING:
    import pytest


def test_build_picker_choices_includes_templates_and_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        h.dev,
        "config_load",
        lambda _path: {
            "markdown_templates": {
                "☕ Coffee": {},
                "📖 Book": {},
            },
        },
    )

    action = OnNewMarkdown()
    choices, action_map = action.build_picker_choices()
    titles = [title for _icon, title in choices]

    assert "☕ Coffee" in titles
    assert "📖 Book" in titles
    assert "New article" in titles
    assert "Edit from template" in titles
    assert len(choices) == len(action_map)
    assert action_map["New article"] == ("method", "_execute_new_article")
    assert action_map["☕ Coffee"] == ("template", "☕ Coffee")


def test_action_classes_excludes_new_markdown_when_panel_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.quick_launcher.context.load_quick_launcher_markdown_in_panel",
        lambda: True,
    )
    context = QuickLauncherContext(
        output_bus=None,
        hotkey_manager=None,
        menu_structure_provider=get_menu_structure,
    )
    actions = context.action_classes()
    assert OnNewMarkdown not in actions
    assert len(actions) == 8


def test_action_classes_includes_new_markdown_when_panel_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.quick_launcher.context.load_quick_launcher_markdown_in_panel",
        lambda: False,
    )
    context = QuickLauncherContext(
        output_bus=None,
        hotkey_manager=None,
        menu_structure_provider=get_menu_structure,
    )
    actions = context.action_classes()
    assert OnNewMarkdown in actions
    assert len(actions) == 9
