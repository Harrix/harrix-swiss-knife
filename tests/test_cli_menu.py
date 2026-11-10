"""Tests for action-card copy menu labels."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget

from harrix_swiss_knife.action_identity import ActionIdentityParts
from harrix_swiss_knife.cli_menu import (
    COPY_ACTION_CLASS_MENU_PREFIX,
    COPY_ACTION_NAME_MENU_PREFIX,
    COPY_ACTION_NAME_PREVIEW_MAX_LEN,
    COPY_ACTION_PATH_MENU_PREFIX,
    format_copy_action_class_menu_label,
    format_copy_action_name_menu_label,
    format_copy_action_path_menu_label,
    show_action_identity_context_menu,
    truncate_action_name_preview,
)
from harrix_swiss_knife.fluent.theme import FluentTheme, ThemeMode, enable_fluent_theme
from harrix_swiss_knife.fluent.tokens import DARK_PALETTE
from harrix_swiss_knife.fluent.widgets.menus import FluentMenu


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


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_action_identity_context_menu_uses_fluent_dark_chrome(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Overlay copy menus follow Fluent dark popup chrome, not the light system plate."""
    assert qapp is not None
    theme = FluentTheme.instance()
    previous = theme.mode()
    theme.set_mode(ThemeMode.DARK, persist=False)
    host = QWidget()
    enable_fluent_theme(host)
    shown: list[FluentMenu] = []

    def _capture_exec(self: FluentMenu, *_args: object, **_kwargs: object) -> None:
        shown.append(self)

    monkeypatch.setattr(FluentMenu, "exec", _capture_exec)
    try:
        show_action_identity_context_menu(
            parent=host,
            global_pos=QPoint(0, 0),
            identity_parts=ActionIdentityParts(
                name="Fix text",
                class_name="OnFixText",
                path="src/harrix_swiss_knife/actions/text/fix_text.py",
            ),
            host_widget=host,
        )
        assert len(shown) == 1
        sheet = shown[0].styleSheet().casefold()
        assert DARK_PALETTE.popup_bg.name().casefold() in sheet or "rgba(44, 44, 44" in sheet
        assert "rgba(255, 255, 255" in sheet or "#ffffff" in sheet
    finally:
        theme.set_mode(previous, persist=False)
        host.close()
