"""Tests for Settings Editor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QTextEdit

from harrix_swiss_knife.actions.common.dialog_geometry import text_content_height
from harrix_swiss_knife.actions.development.settings_editor import (
    OPEN_FOLDER_BUTTON_OBJECT_NAME,
    SettingsEditorDialog,
    folder_path_from_text,
    is_folder_path_setting,
)

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


def test_folder_path_from_text_returns_existing_directory(tmp_path: Path) -> None:
    assert folder_path_from_text(str(tmp_path)) == tmp_path
    assert folder_path_from_text("   ") is None
    assert folder_path_from_text(str(tmp_path / "missing")) is None
    assert folder_path_from_text("snippet:config/beginning-of-md.md") is None


def test_is_folder_path_setting_detects_folder_keys_and_existing_dirs(tmp_path: Path) -> None:
    assert is_folder_path_setting("path_notes", str(tmp_path))
    assert is_folder_path_setting("path_notes", "")
    assert is_folder_path_setting("data_for_hsk_root", "")
    assert not is_folder_path_setting("editor", "cursor")
    assert not is_folder_path_setting("path_totalcmd_ini", r"C:\totalcmd\wincmd.ini")
    assert not is_folder_path_setting("sqlite_food", str(tmp_path / "food.db"))
    assert not is_folder_path_setting("paths_notes", [str(tmp_path)])


def test_folder_path_setting_shows_open_button(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    dialog = _open_settings_dialog(
        monkeypatch,
        {"path_notes": str(tmp_path), "editor": "cursor"},
    )
    try:
        buttons = dialog.findChildren(QPushButton, OPEN_FOLDER_BUTTON_OBJECT_NAME)
        assert len(buttons) == 1
        assert buttons[0].isEnabled()
        assert buttons[0].toolTip() == "Open folder"
    finally:
        dialog.close()


def test_open_folder_button_opens_current_path(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    opened: list[Path] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.actions.development.settings_editor.h.file.open_file_or_folder",
        opened.append,
    )
    dialog = _open_settings_dialog(monkeypatch, {"path_notes": str(tmp_path)})
    try:
        button = dialog.findChild(QPushButton, OPEN_FOLDER_BUTTON_OBJECT_NAME)
        assert button is not None
        button.click()
        QApplication.processEvents()
        assert opened == [tmp_path]
    finally:
        dialog.close()


def test_open_folder_button_disabled_when_folder_missing(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    dialog = _open_settings_dialog(monkeypatch, {"path_notes": str(tmp_path / "missing")})
    try:
        button = dialog.findChild(QPushButton, OPEN_FOLDER_BUTTON_OBJECT_NAME)
        assert button is not None
        assert not button.isEnabled()
    finally:
        dialog.close()
