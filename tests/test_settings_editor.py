"""Tests for Settings Editor multiline field height."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication, QTextEdit

from harrix_swiss_knife.actions.common.dialog_geometry import text_content_height
from harrix_swiss_knife.actions.development.settings_editor import SettingsEditorDialog

_LONG_LIST = [f"item-{index}" for index in range(12)]


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _open_settings_dialog(monkeypatch: pytest.MonkeyPatch, config: dict[str, Any]) -> SettingsEditorDialog:
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.development.settings_editor.get_config_path_str",
        lambda: "config.json",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.development.settings_editor.h.dev.config_load",
        lambda _path: config,
    )
    dialog = SettingsEditorDialog()
    dialog.resize(1200, 800)
    dialog.show()
    QApplication.processEvents()
    dialog._fit_multiline_widgets()
    return dialog


def test_multiline_field_height_shows_all_text(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: ARG001
    dialog = _open_settings_dialog(monkeypatch, {"block_drives": _LONG_LIST})
    try:
        widget = dialog.input_widgets["General::block_drives"]
        assert isinstance(widget, QTextEdit)
        needed = text_content_height(widget, width=widget.width())
        assert widget.height() >= needed
        assert widget.height() > 100
        assert widget.verticalScrollBar().maximum() == 0
    finally:
        dialog.close()
