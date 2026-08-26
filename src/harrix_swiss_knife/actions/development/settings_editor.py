"""Settings editor action."""

from __future__ import annotations

import contextlib
import copy
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import harrix_pylib as h
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.action_hotkeys import load_action_hotkeys
from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.dialog_geometry import text_content_height
from harrix_swiss_knife.actions.common.text_result_dialog import OPEN_FOLDER_BUTTON_EMOJI
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.global_hotkey import hotkey_string_from_event
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_emoji_icon import DELETE_BUTTON_EMOJI, SAVE_BUTTON_EMOJI, make_emoji_push_button

if TYPE_CHECKING:
    from PySide6.QtGui import QFocusEvent, QKeyEvent, QResizeEvent, QShowEvent

OPEN_FOLDER_BUTTON_OBJECT_NAME = "settingsOpenFolderButton"
FIELD_SAVE_BUTTON_OBJECT_NAME = "settingsFieldSaveButton"
STATUS_LABEL_OBJECT_NAME = "settingsSaveStatus"
CLOSE_BUTTON_OBJECT_NAME = "settingsCloseButton"
SAVE_ALL_BUTTON_OBJECT_NAME = "settingsSaveAllButton"
HOTKEY_EDIT_OBJECT_NAME = "settingsHotkeyEdit"
HOTKEY_ACTION_OBJECT_NAME = "settingsHotkeyAction"
HOTKEY_BINDINGS_OBJECT_NAME = "settingsHotkeyBindings"
ADD_HOTKEY_BUTTON_OBJECT_NAME = "settingsAddHotkeyButton"
REMOVE_HOTKEY_BUTTON_OBJECT_NAME = "settingsRemoveHotkeyButton"

_MIN_HOTKEY_PARTS = 2
_HOTKEY_MODIFIERS = frozenset({"alt", "cmd", "command", "control", "ctrl", "meta", "shift", "win"})
_HOTKEY_SPECIAL_KEYS = frozenset(
    {
        "backspace",
        "delete",
        "down",
        "end",
        "enter",
        "esc",
        "escape",
        "home",
        "ins",
        "insert",
        "left",
        "minus",
        "pagedown",
        "pageup",
        "plus",
        "return",
        "right",
        "space",
        "tab",
        "up",
    }
)
_MODIFIER_KEYS = frozenset(
    {
        Qt.Key.Key_Alt,
        Qt.Key.Key_Control,
        Qt.Key.Key_Meta,
        Qt.Key.Key_Shift,
        Qt.Key.Key_unknown,
    }
)

_FILE_PATH_KEYS = frozenset({"path_totalcmd_ini"})
_FILE_PATH_KEY_PREFIXES = ("sqlite_", "vscode_workspace")
_FILE_PATH_SUFFIXES = frozenset(
    {
        ".code-workspace",
        ".db",
        ".ini",
        ".json",
        ".md",
        ".sqlite",
        ".txt",
        ".yaml",
        ".yml",
    }
)


class HotkeyBindingsWidget(QWidget):
    """Editor for `config.json` `hotkeys`: action name plus a capturable shortcut."""

    changed = Signal()

    def __init__(self, bindings: list[Any], parent: QWidget | None = None) -> None:
        """Create rows from existing action-hotkey bindings."""
        super().__init__(parent)
        self.setObjectName(HOTKEY_BINDINGS_OBJECT_NAME)
        self._rows: list[tuple[QWidget, QLineEdit, HotkeyEdit]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        hint = QLabel("Click a shortcut field and press a new key combination.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Action</b>"), 1)
        header.addWidget(QLabel("<b>Shortcut</b>"), 1)
        header.addSpacing(36)
        layout.addLayout(header)

        self._rows_layout = QVBoxLayout()
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._rows_layout)

        for binding in load_action_hotkeys({"hotkeys": bindings}):
            self._add_row(binding.action, binding.hotkey)
        if not self._rows:
            self._add_row("", "")

        add_button = make_emoji_push_button("Add", "➕")  # noqa: RUF001
        add_button.setObjectName(ADD_HOTKEY_BUTTON_OBJECT_NAME)
        add_button.setToolTip("Add hotkey")
        add_button.setAutoDefault(False)
        add_button.setDefault(False)
        add_button.clicked.connect(lambda: self._add_row("", ""))
        layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignLeft)

    def bindings_value(self) -> list[dict[str, Any]]:
        """Return bindings grouped by action, skipping empty rows."""
        grouped: dict[str, list[str]] = {}
        order: list[str] = []
        for _row, action_edit, hotkey_edit in self._rows:
            action = action_edit.text().strip()
            hotkey = hotkey_edit.text().strip()
            if not action or not hotkey:
                continue
            if action not in grouped:
                grouped[action] = []
                order.append(action)
            grouped[action].append(hotkey)
        return [{"action": action, "hotkeys": grouped[action]} for action in order]

    def _add_row(self, action: str, hotkey: str) -> None:
        row = QWidget(self)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        action_edit = QLineEdit(action)
        action_edit.setObjectName(HOTKEY_ACTION_OBJECT_NAME)
        action_edit.setPlaceholderText("OnActionName")
        action_edit.returnPressed.connect(self.changed.emit)
        action_edit.textChanged.connect(self.changed.emit)
        row_layout.addWidget(action_edit, 1)

        hotkey_edit = HotkeyEdit(hotkey)
        hotkey_edit.textChanged.connect(self.changed.emit)
        row_layout.addWidget(hotkey_edit, 1)

        remove_button = make_emoji_push_button("", DELETE_BUTTON_EMOJI)
        remove_button.setObjectName(REMOVE_HOTKEY_BUTTON_OBJECT_NAME)
        remove_button.setToolTip("Remove hotkey")
        remove_button.setAutoDefault(False)
        remove_button.setDefault(False)
        remove_button.setFixedWidth(36)
        remove_button.clicked.connect(lambda _checked=False, current=row: self._remove_row(current))
        row_layout.addWidget(remove_button)

        self._rows_layout.addWidget(row)
        self._rows.append((row, action_edit, hotkey_edit))
        self.changed.emit()

    def _remove_row(self, row: QWidget) -> None:
        for index, (current, _action_edit, _hotkey_edit) in enumerate(self._rows):
            if current is row:
                self._rows.pop(index)
                self._rows_layout.removeWidget(row)
                row.deleteLater()
                self.changed.emit()
                return


class HotkeyEdit(QLineEdit):
    """Read-only field that records a key combination when focused."""

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a hotkey capture field with the current combination `text`."""
        super().__init__(text, parent)
        self.setObjectName(HOTKEY_EDIT_OBJECT_NAME)
        self.setReadOnly(True)
        self.setPlaceholderText("Press a key combination")
        self.setToolTip("Click and press a new key combination. Backspace clears.")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Select the current combination so a new press replaces it."""
        super().focusInEvent(event)
        self.selectAll()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Replace the value with the pressed combination, or clear it."""
        if event.isAutoRepeat():
            event.accept()
            return

        modifiers = event.modifiers()
        key = event.key()
        has_non_shift = bool(modifiers & ~Qt.KeyboardModifier.ShiftModifier)
        if key in {Qt.Key.Key_Backtab, Qt.Key.Key_Tab} and not has_non_shift:
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Escape and not modifiers:
            event.accept()
            return

        if key in {Qt.Key.Key_Backspace, Qt.Key.Key_Delete} and not modifiers:
            self.clear()
            event.accept()
            return

        if key in _MODIFIER_KEYS:
            event.accept()
            return

        text = hotkey_string_from_event(int(key), modifiers)
        if text:
            self.setText(text)
        event.accept()


class OnSettingsEditor(ActionBase):
    """Open settings editor."""

    icon = "⚙️"
    title = "Settings Editor"
    description = "Edit config.json in a VS Code style settings editor."

    @ActionBase.handle_exceptions("settings editor")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the settings editor action."""
        dialog = SettingsEditorDialog()
        # Same sizing as food/finance/habits main windows (maximize or ~1920 wide).
        apply_app_window_size_and_position(dialog)
        dialog.exec()


class SettingsEditorDialog(QDialog):
    """A VS Code style settings editor for `config.json`."""

    _FALLBACK_MULTILINE_WIDTH = 700
    _MIN_MULTILINE_WIDTH = 50
    status_label: QLabel

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the settings editor."""
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.config_path = get_config_path_str()
        try:
            self.config_data = load_raw_config(self.config_path)
        except Exception:
            self.config_data = {}

        self._key_order = list(self.config_data)
        self.categories: dict[str, dict[str, Any]] = self._categorize_config(self.config_data)
        self.input_widgets: dict[str, QWidget] = {}
        self._field_save_buttons: dict[str, QPushButton] = {}
        self._dirty: set[str] = set()
        self._saved_snapshot = copy.deepcopy(self.config_data)

        self._setup_ui()

    def reject(self) -> None:
        """Close after confirming when there are unsaved edits."""
        self._save_current_category()
        if self._dirty and not self._confirm_discard():
            return
        super().reject()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit multiline fields when the dialog width changes."""
        super().resizeEvent(event)
        self._fit_multiline_widgets()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Refit multiline fields when the dialog is shown."""
        super().showEvent(event)
        self._fit_multiline_widgets()

    def _categorize_config(self, data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        categories: dict[str, dict[str, Any]] = {"General": {}}
        for key, value in data.items():
            if isinstance(value, dict) and value:
                categories[key] = value
            else:
                categories["General"][key] = value
        return categories

    def _clear_layout(self, layout: Any) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_settings_layout(self) -> None:
        while self.settings_layout.count():
            item = self.settings_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _confirm_discard(self) -> bool:
        answer = QMessageBox.question(
            self,
            "Unsaved changes",
            "Discard unsaved changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def _connect_dirty(self, widget_key: str, widget: QWidget) -> None:
        if isinstance(widget, QCheckBox):
            widget.stateChanged.connect(lambda _state=0, key=widget_key: self._mark_dirty(key))
        elif isinstance(widget, HotkeyBindingsWidget):
            widget.changed.connect(lambda key=widget_key: self._mark_dirty(key))
        elif isinstance(widget, QLineEdit):
            widget.textChanged.connect(lambda _text="", key=widget_key: self._mark_dirty(key))
            if not isinstance(widget, HotkeyEdit):
                widget.returnPressed.connect(lambda key=widget_key: self._on_field_save(key))
        elif isinstance(widget, QTextEdit):
            widget.textChanged.connect(lambda key=widget_key: self._mark_dirty(key))

    def _fit_multiline_widget(self, widget: QTextEdit) -> None:
        width = widget.width()
        if width < self._MIN_MULTILINE_WIDTH:
            width = max(self.scroll_area.viewport().width(), self._FALLBACK_MULTILINE_WIDTH)
        height = text_content_height(widget, width=width)
        extra = widget.fontMetrics().lineSpacing()
        widget.setFixedHeight(height + extra)

    def _fit_multiline_widgets(self) -> None:
        for widget in self.input_widgets.values():
            if isinstance(widget, QTextEdit):
                self._fit_multiline_widget(widget)

    def _make_field_save_button(self, widget_key: str) -> QPushButton:
        button = make_emoji_push_button("Save", SAVE_BUTTON_EMOJI)
        button.setObjectName(FIELD_SAVE_BUTTON_OBJECT_NAME)
        button.setToolTip("Save this setting to config.json")
        button.setAutoDefault(False)
        button.setDefault(False)
        button.setEnabled(False)
        button.clicked.connect(lambda _checked=False, key=widget_key: self._on_field_save(key))
        self._field_save_buttons[widget_key] = button
        return button

    def _mark_dirty(self, widget_key: str) -> None:
        self._dirty.add(widget_key)
        self._refresh_save_ui()

    def _on_category_changed(self, row: int) -> None:
        if self.search_input.text():
            self.search_input.clear()  # This will trigger _on_search and render the category
            return

        self._save_current_category()
        self._clear_settings_layout()
        self.input_widgets.clear()
        self._field_save_buttons.clear()

        cat_name = self.list_categories.item(row).text()
        self._render_category(cat_name)

    def _on_field_save(self, widget_key: str) -> None:  # noqa: ARG002
        self._on_save()

    def _on_multiline_text_changed(self) -> None:
        sender = self.sender()
        if isinstance(sender, QTextEdit):
            self._fit_multiline_widget(sender)

    def _on_save(self) -> None:
        if not self._persist_config():
            return
        self._dirty.clear()
        self._refresh_save_ui()

    def _on_search(self, text: str) -> None:
        search_term = text.lower()
        self._save_current_category()
        self._clear_settings_layout()
        self.input_widgets.clear()
        self._field_save_buttons.clear()

        if not search_term:
            # If search is cleared, show current category
            row = self.list_categories.currentRow()
            if row >= 0:
                self._render_category(self.list_categories.item(row).text())
            return

        # Show matching settings across all categories
        for cat_name, settings in self.categories.items():
            matching_settings = {k: v for k, v in settings.items() if search_term in k.lower()}
            if matching_settings:
                title = QLabel(f"<h2>{cat_name}</h2>")
                self.settings_layout.addWidget(title)
                self._render_settings(cat_name, matching_settings)

    def _open_folder_path(self, path_text: str) -> None:
        folder = folder_path_from_text(path_text)
        if folder is None:
            QMessageBox.warning(self, "Open folder", "Folder does not exist.")
            return
        h.file.open_file_or_folder(folder)

    def _persist_config(self) -> bool:
        self._save_current_category()
        new_config = assemble_config(self.categories, self._key_order)
        try:
            Path(self.config_path).write_text(h.dev.dumps_pretty_json(new_config), encoding="utf-8")
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")
            return False
        self.config_data = copy.deepcopy(new_config)
        self._saved_snapshot = copy.deepcopy(new_config)
        self._key_order = list(new_config)
        if hasattr(self, "status_label"):
            self.status_label.setText("Saved to config.json")
        return True

    def _refresh_save_ui(self) -> None:
        for key, button in self._field_save_buttons.items():
            button.setEnabled(key in self._dirty)
        if not hasattr(self, "status_label"):
            return
        if self._dirty:
            self.status_label.setText("Unsaved changes")
        elif self.status_label.text() != "Saved to config.json":
            self.status_label.setText("")

    def _render_category(self, cat_name: str) -> None:
        title = QLabel(f"<h2>{cat_name}</h2>")
        self.settings_layout.addWidget(title)
        self._render_settings(cat_name, self.categories[cat_name])

    def _render_settings(self, cat_name: str, settings: dict[str, Any]) -> None:
        for key, value in settings.items():
            setting_layout = QVBoxLayout()
            label = QLabel(f"<b>{key}</b>")
            setting_layout.addWidget(label)

            widget_key = f"{cat_name}::{key}"

            if isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
                self.input_widgets[widget_key] = widget
                setting_layout.addLayout(self._setting_value_row(widget_key, widget))
            elif is_hotkey_bindings_setting(key, value):
                widget = HotkeyBindingsWidget(value if isinstance(value, list) else [])
                self.input_widgets[widget_key] = widget
                setting_layout.addWidget(widget)
                setting_layout.addWidget(self._make_field_save_button(widget_key), alignment=Qt.AlignmentFlag.AlignLeft)
            elif is_hotkey_setting(key, value):
                widget = HotkeyEdit(str(value))
                self.input_widgets[widget_key] = widget
                setting_layout.addLayout(self._setting_value_row(widget_key, widget))
            elif isinstance(value, (int, float, str)):
                widget = QLineEdit(str(value))
                self.input_widgets[widget_key] = widget
                if isinstance(value, str) and is_folder_path_setting(key, value):
                    row = QHBoxLayout()
                    row.setContentsMargins(0, 0, 0, 0)
                    row.addWidget(widget, 1)
                    open_button = make_emoji_push_button("", OPEN_FOLDER_BUTTON_EMOJI)
                    open_button.setObjectName(OPEN_FOLDER_BUTTON_OBJECT_NAME)
                    open_button.setToolTip("Open folder")
                    open_button.setAutoDefault(False)
                    open_button.setDefault(False)
                    open_button.setFixedWidth(36)
                    open_button.clicked.connect(lambda _checked=False, line=widget: self._open_folder_path(line.text()))
                    widget.textChanged.connect(
                        lambda text, button=open_button: button.setEnabled(folder_path_from_text(text) is not None),
                    )
                    open_button.setEnabled(folder_path_from_text(widget.text()) is not None)
                    row.addWidget(open_button)
                    row.addWidget(self._make_field_save_button(widget_key))
                    setting_layout.addLayout(row)
                else:
                    setting_layout.addLayout(self._setting_value_row(widget_key, widget))
            else:
                # Lists or complex objects
                widget = QTextEdit()
                widget.setAcceptRichText(False)
                widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                widget.setPlainText(json.dumps(value, indent=2, ensure_ascii=False))
                widget.textChanged.connect(self._on_multiline_text_changed)
                self.input_widgets[widget_key] = widget
                setting_layout.addWidget(widget)
                setting_layout.addWidget(self._make_field_save_button(widget_key), alignment=Qt.AlignmentFlag.AlignLeft)

            self._connect_dirty(widget_key, widget)
            self.settings_layout.addLayout(setting_layout)
            self.settings_layout.addSpacing(10)

        self._fit_multiline_widgets()

    def _save_current_category(self) -> None:
        for widget_key, widget in self.input_widgets.items():
            cat_name, key = widget_key.split("::", 1)

            if isinstance(widget, QCheckBox):
                self.categories[cat_name][key] = widget.isChecked()
            elif isinstance(widget, HotkeyBindingsWidget):
                self.categories[cat_name][key] = widget.bindings_value()
            elif isinstance(widget, QLineEdit):
                old_val = self.categories[cat_name][key]
                text = widget.text()
                if isinstance(old_val, int):
                    try:
                        self.categories[cat_name][key] = int(text)
                    except ValueError:
                        self.categories[cat_name][key] = text
                elif isinstance(old_val, float):
                    try:
                        self.categories[cat_name][key] = float(text)
                    except ValueError:
                        self.categories[cat_name][key] = text
                else:
                    self.categories[cat_name][key] = text
            elif isinstance(widget, QTextEdit):
                with contextlib.suppress(json.JSONDecodeError):
                    self.categories[cat_name][key] = json.loads(widget.toPlainText())

    def _setting_value_row(self, widget_key: str, widget: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(widget, 1)
        row.addWidget(self._make_field_save_button(widget_key))
        return row

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search settings...")
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left pane: Categories
        self.list_categories = QListWidget()
        for cat in self.categories:
            self.list_categories.addItem(cat)
        self.list_categories.currentRowChanged.connect(self._on_category_changed)
        splitter.addWidget(self.list_categories)

        # Right pane: Settings
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.settings_container = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_container)
        self.settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.settings_container)
        splitter.addWidget(self.scroll_area)

        splitter.setSizes([200, 700])

        # Bottom buttons
        btn_layout = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setObjectName(STATUS_LABEL_OBJECT_NAME)
        btn_layout.addWidget(self.status_label, 1)
        btn_save = make_emoji_push_button("Save all", SAVE_BUTTON_EMOJI)
        btn_save.setObjectName(SAVE_ALL_BUTTON_OBJECT_NAME)
        btn_save.setAutoDefault(False)
        btn_save.setDefault(False)
        btn_save.clicked.connect(self._on_save)
        btn_close = QPushButton("Close")
        btn_close.setObjectName(CLOSE_BUTTON_OBJECT_NAME)
        btn_close.setAutoDefault(False)
        btn_close.setDefault(False)
        btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        if self.list_categories.count() > 0:
            self.list_categories.setCurrentRow(0)


def assemble_config(categories: dict[str, dict[str, Any]], key_order: list[str]) -> dict[str, Any]:
    """Rebuild a top-level config object, keeping `key_order` and snippet strings."""
    general = categories.get("General", {})
    result: dict[str, Any] = {}
    seen: set[str] = set()
    for key in key_order:
        if key in general:
            result[key] = general[key]
            seen.add(key)
        elif key in categories and key != "General":
            result[key] = categories[key]
            seen.add(key)
    for key, value in general.items():
        if key not in seen:
            result[key] = value
            seen.add(key)
    result.update({key: value for key, value in categories.items() if key != "General" and key not in seen})
    return result


def folder_path_from_text(text: str) -> Path | None:
    """Return an existing directory for `text`, or `None` if it is not a folder."""
    stripped = text.strip()
    if not stripped or stripped.startswith("snippet:"):
        return None
    path = Path(stripped).expanduser()
    try:
        if path.is_dir():
            return path
    except OSError:
        return None
    return None


def is_folder_path_setting(key: str, value: object) -> bool:
    """Return whether a setting is a folder path (by value or by key name)."""
    if not isinstance(value, str):
        return False
    if folder_path_from_text(value) is not None:
        return True
    return _is_folder_path_key(key, value)


def is_hotkey_bindings_setting(key: str, value: object) -> bool:
    """Return whether a setting is a list of action-hotkey bindings."""
    if not isinstance(value, list):
        return False
    key_norm = key.lower().replace("-", "_")
    if key_norm == "hotkeys":
        return not value or all(isinstance(item, dict) for item in value)
    return bool(value) and all(_is_hotkey_binding_item(item) for item in value)


def is_hotkey_setting(key: str, value: object) -> bool:
    """Return whether a setting is a keyboard shortcut string."""
    if not isinstance(value, str):
        return False
    if _is_hotkey_key_name(key):
        return True
    return is_hotkey_string(value)


def is_hotkey_string(value: object) -> bool:
    """Return whether `value` looks like a portable key combination (`Ctrl+Shift+F1`)."""
    if not isinstance(value, str):
        return False
    parts = [part.strip().lower() for part in value.strip().split("+") if part.strip()]
    if len(parts) < _MIN_HOTKEY_PARTS:
        return False
    key = parts[-1]
    modifiers = parts[:-1]
    if not modifiers or not all(part in _HOTKEY_MODIFIERS for part in modifiers):
        return False
    if key in _HOTKEY_MODIFIERS:
        return False
    if key in _HOTKEY_SPECIAL_KEYS:
        return True
    if len(key) == 1 and key.isalnum():
        return True
    return key.startswith("f") and key[1:].isdigit()


def load_raw_config(path: str | Path) -> dict[str, Any]:
    """Load `config.json` without expanding `snippet:` values."""
    loaded = h.dev.config_load(path, resolve_snippets=False)
    if not isinstance(loaded, dict):
        msg = f"Config root must be a JSON object: {path}"
        raise TypeError(msg)
    return loaded


def _is_folder_path_key(key: str, value: str) -> bool:
    key_norm = key.lower().replace("-", "_")
    if key_norm in _FILE_PATH_KEYS or key_norm.startswith(_FILE_PATH_KEY_PREFIXES):
        return False
    if Path(value).suffix.lower() in _FILE_PATH_SUFFIXES:
        return False
    return key_norm.startswith("path_") or key_norm.endswith(("_root", "_folder", "_dir")) or "folder" in key_norm


def _is_hotkey_binding_item(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    if not str(item.get("action") or "").strip():
        return False
    return item.get("hotkeys") is not None or item.get("hotkey") is not None


def _is_hotkey_key_name(key: str) -> bool:
    key_norm = key.lower().replace("-", "_")
    return key_norm == "hotkey" or key_norm.endswith("_hotkey")
