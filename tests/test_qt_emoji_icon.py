"""Tests for emoji menu-icon helpers."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QMenu

from harrix_swiss_knife.qt_emoji_icon import (
    add_emoji_action,
    apply_leading_emoji_icon,
    apply_leading_emoji_icons,
    set_action_text_with_emoji_icon,
    split_leading_emoji,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


@pytest.mark.parametrize(
    ("text", "emoji", "rest"),
    [
        ("🔄 Refresh", "🔄", "Refresh"),
        ("📋 Show Last 10", "📋", "Show Last 10"),
        ("ℹ️ About", "ℹ️", "About"),  # noqa: RUF001
        ("➕ Add habit", "➕", "Add habit"),  # noqa: RUF001
        ("Show current month and year", "", "Show current month and year"),
        ("", "", ""),
    ],
)
def test_split_leading_emoji(text: str, emoji: str, rest: str) -> None:
    found, leftover = split_leading_emoji(text)
    assert found == emoji
    if emoji:
        assert leftover == rest
    else:
        assert leftover == text


def test_apply_leading_emoji_icon_moves_prefix_to_icon(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    action = menu.addAction("🔄 Refresh")
    assert apply_leading_emoji_icon(action)
    assert action.text() == "Refresh"
    assert not action.icon().isNull()


def test_apply_leading_emoji_icons_walks_submenu(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    menu.addAction("💾 Backup habits")
    year_menu = menu.addMenu("📆 Year")
    year_menu.addAction("2026")
    apply_leading_emoji_icons(menu)
    assert menu.actions()[0].text() == "Backup habits"
    assert not menu.actions()[0].icon().isNull()
    year_action = next(action for action in menu.actions() if action.menu() is not None)
    assert year_action.text() == "Year"
    assert not year_action.icon().isNull()


def test_add_emoji_action_keeps_plain_label(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    action = add_emoji_action(menu, "Edit habit", "✏️")
    assert action.text() == "Edit habit"
    assert not action.icon().isNull()


def test_set_action_text_with_emoji_icon_does_not_duplicate_prefix(qapp: QApplication) -> None:
    assert qapp is not None
    menu = QMenu()
    action = menu.addAction("📋 Show All Set Records")
    apply_leading_emoji_icon(action)
    set_action_text_with_emoji_icon(action, "📋 Show Last 10 Set Records")
    assert action.text() == "Show Last 10 Set Records"
    assert not action.icon().isNull()
