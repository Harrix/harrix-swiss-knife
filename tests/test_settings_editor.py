"""Tests for Settings Editor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QTextEdit

from harrix_swiss_knife.actions.common.dialog_geometry import text_content_height
from harrix_swiss_knife.apps.common.settings_editor import (
    ADD_HOTKEY_BUTTON_OBJECT_NAME,
    FIELD_SAVE_BUTTON_OBJECT_NAME,
    HOTKEY_ACTION_OBJECT_NAME,
    HOTKEY_BINDINGS_OBJECT_NAME,
    HOTKEY_EDIT_OBJECT_NAME,
    OPEN_FOLDER_BUTTON_OBJECT_NAME,
    OPEN_SNIPPET_BUTTON_OBJECT_NAME,
    SAVE_ALL_BUTTON_OBJECT_NAME,
    SNIPPET_CONTENT_OBJECT_NAME,
    HotkeyBindingsWidget,
    HotkeyEdit,
    SettingsEditorDialog,
    assemble_config,
    config_key_belongs_to_app,
    filter_config_categories,
    folder_path_from_text,
    is_folder_path_setting,
    is_hotkey_bindings_setting,
    is_hotkey_setting,
    is_hotkey_string,
    is_snippet_setting,
    load_raw_config,
    merge_filtered_config,
    snippet_path_from_text,
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
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: "config.json",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.load_raw_config",
        lambda _path: config,
    )
    dialog = SettingsEditorDialog()
    dialog.resize(1200, 800)
    dialog.show()
    QApplication.processEvents()
    dialog._fit_multiline_widgets()
    return dialog


def test_assemble_config_keeps_key_order_and_nested_objects() -> None:
    categories = {
        "General": {
            "android_build_variant": "release",
            "beginning_of_md": "snippet:config/beginning-of-md.md",
            "editor": "cursor",
        },
        "apps": {"local_language": "ru"},
        "prompts": {"text_fix_ru": "snippet:config/prompts/text-fix-ru.md"},
    }
    order = ["android_build_variant", "apps", "beginning_of_md", "editor", "prompts"]
    assembled = assemble_config(categories, order)
    assert list(assembled) == order
    assert assembled["beginning_of_md"] == "snippet:config/beginning-of-md.md"
    assert assembled["prompts"]["text_fix_ru"] == "snippet:config/prompts/text-fix-ru.md"


def test_load_raw_config_keeps_snippet_references(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(
        '{"beginning_of_md": "snippet:config/beginning-of-md.md", "editor": "cursor"}\n',
        encoding="utf-8",
    )
    loaded = load_raw_config(path)
    assert loaded["beginning_of_md"] == "snippet:config/beginning-of-md.md"


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


def test_is_snippet_setting_and_path(tmp_path: Path) -> None:
    assert is_snippet_setting("snippet:config/prompts/finance-category-translate-local.md")
    assert not is_snippet_setting("cursor")
    assert not is_snippet_setting("snippet:")
    path = snippet_path_from_text(
        "snippet:config/prompts/finance-category-translate-local.md",
        project_root=tmp_path,
    )
    assert path == tmp_path / "config" / "prompts" / "finance-category-translate-local.md"
    assert snippet_path_from_text("cursor", project_root=tmp_path) is None


def test_snippet_setting_shows_open_button_and_content(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    snippet = tmp_path / "config" / "prompts" / "finance-category-translate-local.md"
    snippet.parent.mkdir(parents=True)
    snippet.write_text("Translate categories.\n", encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_project_root",
        lambda: tmp_path,
    )
    dialog = _open_settings_dialog(
        monkeypatch,
        {
            "editor": "cursor",
            "prompts": {
                "finance_category_translate_local": "snippet:config/prompts/finance-category-translate-local.md"
            },
        },
    )
    try:
        for row in range(dialog.list_categories.count()):
            item = dialog.list_categories.item(row)
            if item is not None and item.text() == "prompts":
                dialog.list_categories.setCurrentRow(row)
                break
        QApplication.processEvents()
        path_edit = dialog.input_widgets["prompts::finance_category_translate_local"]
        assert isinstance(path_edit, QLineEdit)
        assert path_edit.text() == "snippet:config/prompts/finance-category-translate-local.md"
        button = dialog.findChild(QPushButton, OPEN_SNIPPET_BUTTON_OBJECT_NAME)
        assert button is not None
        assert button.isEnabled()
        assert button.toolTip() == "Open snippet in editor"
        content = dialog.findChild(QTextEdit, SNIPPET_CONTENT_OBJECT_NAME)
        assert content is not None
        assert content.toPlainText() == "Translate categories.\n"
        assert not content.isWindow()
        assert content.window() is dialog
    finally:
        dialog._dirty.clear()
        dialog.close()


def test_open_snippet_button_opens_file_in_editor(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    snippet = tmp_path / "config" / "prompts" / "note.md"
    snippet.parent.mkdir(parents=True)
    snippet.write_text("Hello\n", encoding="utf-8")
    opened: list[tuple[str, Path, Path]] = []
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.open_in_editor",
        lambda editor, workspace, path: opened.append((editor, Path(workspace), Path(path))),
    )
    dialog = _open_settings_dialog(
        monkeypatch,
        {"editor": "cursor", "beginning_of_md": "snippet:config/prompts/note.md"},
    )
    try:
        button = dialog.findChild(QPushButton, OPEN_SNIPPET_BUTTON_OBJECT_NAME)
        assert button is not None
        button.click()
        QApplication.processEvents()
        assert opened == [("cursor", tmp_path, snippet)]
    finally:
        dialog.close()


def test_snippet_content_save_writes_file(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    snippet = tmp_path / "config" / "prompts" / "note.md"
    snippet.parent.mkdir(parents=True)
    snippet.write_text("Old\n", encoding="utf-8")
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"editor": "cursor", "beginning_of_md": "snippet:config/prompts/note.md"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: str(path),
    )
    dialog = SettingsEditorDialog()
    dialog.show()
    QApplication.processEvents()
    try:
        content = dialog.findChild(QTextEdit, SNIPPET_CONTENT_OBJECT_NAME)
        assert content is not None
        content.setPlainText("New text\n")
        QApplication.processEvents()
        save_all = dialog.findChild(QPushButton, SAVE_ALL_BUTTON_OBJECT_NAME)
        assert save_all is not None
        save_all.click()
        QApplication.processEvents()
        assert snippet.read_text(encoding="utf-8") == "New text\n"
        written = json.loads(path.read_text(encoding="utf-8"))
        assert written["beginning_of_md"] == "snippet:config/prompts/note.md"
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
        "harrix_swiss_knife.apps.common.settings_editor.h.file.open_file_or_folder",
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
        dialog._dirty.clear()
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
        dialog._dirty.clear()
        dialog.close()


def test_save_keeps_snippets_key_order_and_stays_open(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "config.json"
    original = {
        "android_build_variant": "release",
        "apps": {"local_language": "ru"},
        "beginning_of_md": "snippet:config/beginning-of-md.md",
        "bothub_api_key": "snippet:api-keys/bothub-api-key.txt",
        "editor": "cursor",
        "prompts": {"text_fix_ru": "snippet:config/prompts/text-fix-ru.md"},
    }
    path.write_text(json.dumps(original), encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: str(path),
    )
    dialog = SettingsEditorDialog()
    dialog.show()
    QApplication.processEvents()
    try:
        editor = dialog.input_widgets["General::editor"]
        assert isinstance(editor, QLineEdit)
        editor.setText("code")
        QApplication.processEvents()
        save_all = dialog.findChild(QPushButton, SAVE_ALL_BUTTON_OBJECT_NAME)
        assert save_all is not None
        save_all.click()
        QApplication.processEvents()
        assert dialog.isVisible()
        written = json.loads(path.read_text(encoding="utf-8"))
        assert list(written) == list(original)
        assert written["editor"] == "code"
        assert written["beginning_of_md"] == "snippet:config/beginning-of-md.md"
        assert written["bothub_api_key"] == "snippet:api-keys/bothub-api-key.txt"
        assert written["prompts"]["text_fix_ru"] == "snippet:config/prompts/text-fix-ru.md"
        field_saves = dialog.findChildren(QPushButton, FIELD_SAVE_BUTTON_OBJECT_NAME)
        assert field_saves
        assert dialog.status_label.text() == "Saved to config.json"
    finally:
        dialog.close()


def test_save_ui_font_scale_prompts_restart(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"editor": "cursor", "ui_font_scale": 1.0}\n', encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: str(path),
    )
    prompted: list[list[str]] = []
    monkeypatch.setattr(
        SettingsEditorDialog,
        "_show_restart_required",
        lambda _self, keys: prompted.append(list(keys)),
    )
    dialog = SettingsEditorDialog()
    dialog.show()
    QApplication.processEvents()
    try:
        scale = dialog.input_widgets["General::ui_font_scale"]
        assert isinstance(scale, QLineEdit)
        scale.setText("1.2")
        QApplication.processEvents()
        save_all = dialog.findChild(QPushButton, SAVE_ALL_BUTTON_OBJECT_NAME)
        assert save_all is not None
        save_all.click()
        QApplication.processEvents()
        written = json.loads(path.read_text(encoding="utf-8"))
        assert written["ui_font_scale"] == 1.2
        assert prompted == [["ui_font_scale"]]
    finally:
        dialog.close()


def test_save_editor_does_not_prompt_restart(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"editor": "cursor", "ui_font_scale": 1.0}\n', encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: str(path),
    )
    prompted: list[list[str]] = []
    monkeypatch.setattr(
        SettingsEditorDialog,
        "_show_restart_required",
        lambda _self, keys: prompted.append(list(keys)),
    )
    dialog = SettingsEditorDialog()
    dialog.show()
    QApplication.processEvents()
    try:
        editor = dialog.input_widgets["General::editor"]
        assert isinstance(editor, QLineEdit)
        editor.setText("code")
        QApplication.processEvents()
        save_all = dialog.findChild(QPushButton, SAVE_ALL_BUTTON_OBJECT_NAME)
        assert save_all is not None
        save_all.click()
        QApplication.processEvents()
        assert prompted == []
    finally:
        dialog.close()


def test_enter_in_field_saves_without_closing(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "config.json"
    path.write_text('{"editor": "cursor"}\n', encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: str(path),
    )
    dialog = SettingsEditorDialog()
    dialog.show()
    QApplication.processEvents()
    try:
        editor = dialog.input_widgets["General::editor"]
        assert isinstance(editor, QLineEdit)
        editor.setText("code")
        editor.setFocus()
        QApplication.processEvents()
        event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(editor, event)
        QApplication.processEvents()
        assert dialog.isVisible()
        written = json.loads(path.read_text(encoding="utf-8"))
        assert written["editor"] == "code"
    finally:
        dialog.close()


def test_config_key_belongs_to_app_matches_prefixes_and_sqlite() -> None:
    assert config_key_belongs_to_app("sqlite_fitness", "fitness")
    assert config_key_belongs_to_app("fitness_names_translate_local_limit", "fitness")
    assert config_key_belongs_to_app("food_calorie_thresholds", "food")
    assert config_key_belongs_to_app("path_habit_comments", "habits")
    assert config_key_belongs_to_app("habits_sport_habit_name", "habits")
    assert config_key_belongs_to_app("habits_sport_lookback_days", "habits")
    assert config_key_belongs_to_app("path_vector_icons_pinned", "icons")
    assert config_key_belongs_to_app("vector_icons_recent_folders_max", "icons")
    assert not config_key_belongs_to_app("sqlite_food", "fitness")
    assert not config_key_belongs_to_app("editor", "fitness")


def test_filter_config_categories_keeps_app_and_shared_tracker_keys() -> None:
    categories = {
        "General": {
            "editor": "cursor",
            "sqlite_fitness": "fitness.db",
            "sqlite_food": "food.db",
            "fitness_names_translate_local_limit": 250,
        },
        "apps": {
            "fitness_image_max_size": 330,
            "initial_count": 1000,
            "local_language": "ru",
        },
        "prompts": {
            "fitness_workout_generate": "snippet:fitness.md",
            "food_kcal_lookup": "snippet:food.md",
        },
        "food_calorie_thresholds": {"low": 1800, "medium_high": 2500},
    }
    fitness = filter_config_categories(categories, "fitness")
    assert "editor" not in fitness.get("General", {})
    assert fitness["General"]["sqlite_fitness"] == "fitness.db"
    assert "sqlite_food" not in fitness.get("General", {})
    assert fitness["apps"] == {
        "fitness_image_max_size": 330,
        "initial_count": 1000,
        "local_language": "ru",
    }
    assert fitness["prompts"] == {"fitness_workout_generate": "snippet:fitness.md"}
    assert "food_calorie_thresholds" not in fitness

    food = filter_config_categories(categories, "food")
    assert food["food_calorie_thresholds"] == {"low": 1800, "medium_high": 2500}
    assert "fitness_image_max_size" not in food.get("apps", {})
    assert food["apps"]["initial_count"] == 1000

    icons = filter_config_categories(categories, "icons")
    assert icons == {}


def test_merge_filtered_config_updates_app_keys_only() -> None:
    full = {
        "editor": "cursor",
        "apps": {"fitness_image_max_size": 330, "local_language": "ru"},
        "prompts": {"fitness_workout_generate": "a", "food_kcal_lookup": "b"},
        "sqlite_fitness": "old.db",
    }
    assembled = {
        "apps": {"fitness_image_max_size": 640, "local_language": "en"},
        "prompts": {"fitness_workout_generate": "c"},
        "sqlite_fitness": "new.db",
    }
    merged = merge_filtered_config(full, assembled)
    assert merged["editor"] == "cursor"
    assert merged["apps"] == {"fitness_image_max_size": 640, "local_language": "en"}
    assert merged["prompts"] == {"fitness_workout_generate": "c", "food_kcal_lookup": "b"}
    assert merged["sqlite_fitness"] == "new.db"


def test_app_settings_dialog_shows_only_matching_keys(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: "config.json",
    )
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.load_raw_config",
        lambda _path: {
            "editor": "cursor",
            "sqlite_fitness": "fitness.db",
            "sqlite_food": "food.db",
            "apps": {"fitness_image_max_size": 330, "local_language": "ru"},
            "prompts": {"fitness_sets_to_tsv": "snippet:a.md", "food_kcal_lookup": "snippet:b.md"},
        },
    )
    dialog = SettingsEditorDialog(app_id="fitness", window_title="Fitness tracker settings")
    dialog.show()
    QApplication.processEvents()
    try:
        assert dialog.windowTitle() == "Fitness tracker settings"
        assert dialog.categories["General"]["sqlite_fitness"] == "fitness.db"
        assert "editor" not in dialog.categories["General"]
        assert "sqlite_food" not in dialog.categories["General"]
        assert dialog.categories["apps"]["fitness_image_max_size"] == 330
        assert dialog.categories["apps"]["local_language"] == "ru"
        assert dialog.categories["prompts"] == {"fitness_sets_to_tsv": "snippet:a.md"}
        assert "General::sqlite_fitness" in dialog.input_widgets
        assert "General::editor" not in dialog.input_widgets
    finally:
        dialog.close()


def test_app_settings_save_keeps_other_app_keys(
    qapp: QApplication,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "config.json"
    original = {
        "editor": "cursor",
        "apps": {"fitness_image_max_size": 330, "local_language": "ru"},
        "prompts": {"fitness_sets_to_tsv": "snippet:a.md", "food_kcal_lookup": "snippet:b.md"},
        "sqlite_fitness": "fitness.db",
        "sqlite_food": "food.db",
    }
    path.write_text(json.dumps(original), encoding="utf-8")
    monkeypatch.setattr(
        "harrix_swiss_knife.apps.common.settings_editor.get_config_path_str",
        lambda: str(path),
    )
    dialog = SettingsEditorDialog(app_id="fitness")
    dialog.show()
    QApplication.processEvents()
    try:
        for row in range(dialog.list_categories.count()):
            item = dialog.list_categories.item(row)
            if item is not None and item.text() == "apps":
                dialog.list_categories.setCurrentRow(row)
                break
        QApplication.processEvents()
        size = dialog.input_widgets["apps::fitness_image_max_size"]
        assert isinstance(size, QLineEdit)
        size.setText("640")
        QApplication.processEvents()
        save_all = dialog.findChild(QPushButton, SAVE_ALL_BUTTON_OBJECT_NAME)
        assert save_all is not None
        save_all.click()
        QApplication.processEvents()
        written = json.loads(path.read_text(encoding="utf-8"))
        assert written["editor"] == "cursor"
        assert written["sqlite_food"] == "food.db"
        assert written["prompts"]["food_kcal_lookup"] == "snippet:b.md"
        assert written["apps"]["fitness_image_max_size"] == 640
        assert written["apps"]["local_language"] == "ru"
    finally:
        dialog.close()
