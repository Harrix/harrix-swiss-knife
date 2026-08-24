"""Tests for Settings Editor."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QTextEdit

from harrix_swiss_knife.actions.common.dialog_geometry import text_content_height
from harrix_swiss_knife.actions.development.settings_editor import (
    ADD_HOTKEY_BUTTON_OBJECT_NAME,
    HOTKEY_ACTION_OBJECT_NAME,
    HOTKEY_BINDINGS_OBJECT_NAME,
    HOTKEY_EDIT_OBJECT_NAME,
    OPEN_FOLDER_BUTTON_OBJECT_NAME,
    HotkeyBindingsWidget,
    HotkeyEdit,
    SettingsEditorDialog,
    folder_path_from_text,
    is_folder_path_setting,
    is_hotkey_bindings_setting,
    is_hotkey_setting,
    is_hotkey_string,
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


def test_is_hotkey_string_detects_portable_combinations() -> None:
    assert is_hotkey_string("Ctrl+Shift+F1")
    assert is_hotkey_string("Alt+Space")
    assert not is_hotkey_string("cursor")
    assert not is_hotkey_string("C++")
    assert not is_hotkey_string("F1")
    assert not is_hotkey_string("")


def test_is_hotkey_setting_uses_key_name_or_value() -> None:
    assert is_hotkey_setting("toggle_hotkey", "")
    assert is_hotkey_setting("editor", "Ctrl+Alt+Q")
    assert not is_hotkey_setting("editor", "cursor")
    assert not is_hotkey_setting("hotkey", ["Ctrl+F1"])


def test_is_hotkey_bindings_setting_detects_action_list() -> None:
    assert is_hotkey_bindings_setting("hotkeys", [])
    assert is_hotkey_bindings_setting(
        "hotkeys",
        [{"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1"]}],
    )
    assert not is_hotkey_bindings_setting("block_drives", ["C"])
    assert not is_hotkey_bindings_setting("hotkeys", "Ctrl+F1")


def test_hotkey_string_setting_uses_capture_field(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dialog = _open_settings_dialog(monkeypatch, {"toggle_hotkey": "Ctrl+Shift+F1"})
    try:
        widget = dialog.input_widgets["General::toggle_hotkey"]
        assert isinstance(widget, HotkeyEdit)
        assert widget.objectName() == HOTKEY_EDIT_OBJECT_NAME
        assert widget.text() == "Ctrl+Shift+F1"
    finally:
        dialog.close()


def test_hotkey_edit_records_new_combination(qapp: QApplication) -> None:  # noqa: ARG001
    widget = HotkeyEdit("Ctrl+Shift+F1")
    widget.show()
    widget.setFocus()
    QApplication.processEvents()
    try:
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_F3,
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
        )
        QApplication.sendEvent(widget, event)
        QApplication.processEvents()
        assert widget.text() == "Ctrl+Shift+F3"
    finally:
        widget.close()


def test_hotkey_bindings_setting_uses_capture_rows(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dialog = _open_settings_dialog(
        monkeypatch,
        {
            "hotkeys": [
                {"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1"]},
                {"action": "OnScreenshotRegion", "hotkey": "Ctrl+Shift+F2"},
            ],
        },
    )
    try:
        widget = dialog.input_widgets["General::hotkeys"]
        assert isinstance(widget, HotkeyBindingsWidget)
        assert widget.objectName() == HOTKEY_BINDINGS_OBJECT_NAME
        assert widget.bindings_value() == [
            {"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1"]},
            {"action": "OnScreenshotRegion", "hotkeys": ["Ctrl+Shift+F2"]},
        ]
        action_edits = widget.findChildren(QLineEdit, HOTKEY_ACTION_OBJECT_NAME)
        hotkey_edits = widget.findChildren(HotkeyEdit)
        assert [edit.text() for edit in action_edits] == ["OnQuickLauncher", "OnScreenshotRegion"]
        assert [edit.text() for edit in hotkey_edits] == ["Ctrl+Shift+F1", "Ctrl+Shift+F2"]
        add_button = dialog.findChild(QPushButton, ADD_HOTKEY_BUTTON_OBJECT_NAME)
        assert add_button is not None
        add_button.click()
        QApplication.processEvents()
        assert len(widget.findChildren(HotkeyEdit)) == 3
    finally:
        dialog.close()


def test_hotkey_bindings_save_new_combination(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dialog = _open_settings_dialog(
        monkeypatch,
        {"hotkeys": [{"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Shift+F1"]}]},
    )
    try:
        widget = dialog.input_widgets["General::hotkeys"]
        assert isinstance(widget, HotkeyBindingsWidget)
        hotkey_edit = widget.findChild(HotkeyEdit)
        assert hotkey_edit is not None
        hotkey_edit.setFocus()
        QApplication.processEvents()
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_F9,
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
        )
        QApplication.sendEvent(hotkey_edit, event)
        QApplication.processEvents()
        dialog._save_current_category()
        assert dialog.categories["General"]["hotkeys"] == [
            {"action": "OnQuickLauncher", "hotkeys": ["Ctrl+Alt+F9"]},
        ]
    finally:
        dialog.close()
