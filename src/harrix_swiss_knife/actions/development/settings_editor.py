"""Settings editor action."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import harrix_pylib as h
from PySide6.QtCore import Qt
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

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.actions.common.dialog_geometry import text_content_height
from harrix_swiss_knife.actions.common.text_result_dialog import OPEN_FOLDER_BUTTON_EMOJI
from harrix_swiss_knife.apps.common.qt_main_window import apply_app_window_size_and_position
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_emoji_icon import make_emoji_push_button

if TYPE_CHECKING:
    from PySide6.QtGui import QResizeEvent, QShowEvent

OPEN_FOLDER_BUTTON_OBJECT_NAME = "settingsOpenFolderButton"

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

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the settings editor."""
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.config_path = get_config_path_str()
        try:
            self.config_data = h.dev.config_load(self.config_path)
        except Exception:
            self.config_data = {}

        self.categories: dict[str, dict[str, Any]] = self._categorize_config(self.config_data)
        self.input_widgets: dict[str, QWidget] = {}

        self._setup_ui()

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

    def _on_category_changed(self, row: int) -> None:
        if self.search_input.text():
            self.search_input.clear()  # This will trigger _on_search and render the category
            return

        self._save_current_category()
        self._clear_settings_layout()
        self.input_widgets.clear()

        cat_name = self.list_categories.item(row).text()
        self._render_category(cat_name)

    def _on_multiline_text_changed(self) -> None:
        sender = self.sender()
        if isinstance(sender, QTextEdit):
            self._fit_multiline_widget(sender)

    def _on_save(self) -> None:
        self._save_current_category()

        new_config = dict(self.categories["General"])
        new_config.update({k: v for k, v in self.categories.items() if k != "General"})

        try:
            Path(self.config_path).write_text(h.dev.dumps_pretty_json(new_config), encoding="utf-8")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")

    def _on_search(self, text: str) -> None:
        search_term = text.lower()
        self._save_current_category()
        self._clear_settings_layout()
        self.input_widgets.clear()

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
                setting_layout.addWidget(widget)
                self.input_widgets[widget_key] = widget
            elif isinstance(value, (int, float, str)):
                widget = QLineEdit(str(value))
                if isinstance(value, str) and is_folder_path_setting(key, value):
                    row = QHBoxLayout()
                    row.setContentsMargins(0, 0, 0, 0)
                    row.addWidget(widget, 1)
                    open_button = make_emoji_push_button("", OPEN_FOLDER_BUTTON_EMOJI)
                    open_button.setObjectName(OPEN_FOLDER_BUTTON_OBJECT_NAME)
                    open_button.setToolTip("Open folder")
                    open_button.setFixedWidth(36)
                    open_button.clicked.connect(lambda _checked=False, line=widget: self._open_folder_path(line.text()))
                    widget.textChanged.connect(
                        lambda text, button=open_button: button.setEnabled(folder_path_from_text(text) is not None),
                    )
                    open_button.setEnabled(folder_path_from_text(widget.text()) is not None)
                    row.addWidget(open_button)
                    setting_layout.addLayout(row)
                else:
                    setting_layout.addWidget(widget)
                self.input_widgets[widget_key] = widget
            else:
                # Lists or complex objects
                widget = QTextEdit()
                widget.setAcceptRichText(False)
                widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                widget.setPlainText(json.dumps(value, indent=2, ensure_ascii=False))
                widget.textChanged.connect(self._on_multiline_text_changed)
                setting_layout.addWidget(widget)
                self.input_widgets[widget_key] = widget

            self.settings_layout.addLayout(setting_layout)
            self.settings_layout.addSpacing(10)

        self._fit_multiline_widgets()

    def _save_current_category(self) -> None:
        for widget_key, widget in self.input_widgets.items():
            cat_name, key = widget_key.split("::", 1)

            if isinstance(widget, QCheckBox):
                self.categories[cat_name][key] = widget.isChecked()
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
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        if self.list_categories.count() > 0:
            self.list_categories.setCurrentRow(0)


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


def _is_folder_path_key(key: str, value: str) -> bool:
    key_norm = key.lower().replace("-", "_")
    if key_norm in _FILE_PATH_KEYS or key_norm.startswith(_FILE_PATH_KEY_PREFIXES):
        return False
    if Path(value).suffix.lower() in _FILE_PATH_SUFFIXES:
        return False
    return key_norm.startswith("path_") or key_norm.endswith(("_root", "_folder", "_dir")) or "folder" in key_norm
