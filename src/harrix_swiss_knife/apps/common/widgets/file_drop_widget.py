"""Single-file and multi-file drag-and-drop widgets."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import install_url_drop_handlers
from harrix_swiss_knife.qt_emoji_icon import DELETE_BUTTON_EMOJI, make_emoji_push_button

if TYPE_CHECKING:
    from collections.abc import Callable


class FileDropWidget(QWidget):
    """Widget for single file selection with drag and drop support."""

    file_changed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        name_filter: str = "All files (*)",
        allowed_extensions: frozenset[str] | None = None,
        hint_text: str = "Drag and drop file here or click button",
        dialog_title: str = "Select file",
        path_filter: Callable[[str], bool] | None = None,
    ) -> None:
        """Initialize single-file drop widget.

        Args:

        - `name_filter` (`str`): Qt file dialog filter string.
        - `allowed_extensions` (`frozenset[str] | None`): Lowercase extensions with a leading
          dot. When set, dropped/browsed files outside this set are ignored.
        - `hint_text` (`str`): Placeholder text when no file is selected.
        - `dialog_title` (`str`): Title for the browse dialog.
        - `path_filter` (`Callable[[str], bool] | None`): Optional extra path validator.

        """
        super().__init__(parent)
        self.file_path = ""
        self._name_filter = name_filter
        self._allowed_extensions = allowed_extensions
        self._hint_text = hint_text
        self._dialog_title = dialog_title
        self._path_filter = path_filter
        self._setup_ui()

    def clear(self) -> None:
        """Clear the selected file."""
        self._clear_file()

    def get_file_path(self) -> str:
        """Return selected file path."""
        return self.file_path

    def set_file_path(self, path: str) -> None:
        """Set file path when the file exists and passes filters."""
        if path and Path(path).exists() and self._is_allowed_path(path):
            self._set_file(path)

    def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, self._dialog_title, "", self._name_filter)
        if file_path and self._is_allowed_path(file_path):
            self._set_file(file_path)

    def _clear_file(self) -> None:
        changed = bool(self.file_path)
        self.file_path = ""
        self.file_label.setText(self._hint_text)
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        if changed:
            self.file_changed.emit()

    def _is_allowed_path(self, file_path: str) -> bool:
        path = Path(file_path)
        if self._allowed_extensions is not None and path.suffix.lower() not in self._allowed_extensions:
            return False
        return self._path_filter is None or self._path_filter(file_path)

    def _on_drop_paths(self, paths: list[str]) -> None:
        if not paths:
            return
        if self._is_allowed_path(paths[0]):
            self._set_file(paths[0])

    def _set_file(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_label.setText(f"File: {Path(file_path).name}")
        self.file_label.setStyleSheet(_SELECTED_DROP_STYLE)
        self.file_changed.emit()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.file_label = QLabel(self._hint_text)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet(_EMPTY_DROP_STYLE)
        self.file_label.setMinimumHeight(60)
        self.file_label.setWordWrap(True)
        install_url_drop_handlers(
            self.file_label,
            self._on_drop_paths,
            filter_path=self._is_allowed_path if self._allowed_extensions or self._path_filter else None,
        )

        button_layout = QHBoxLayout()
        self.browse_button = make_emoji_push_button("Select File", "📁")
        self.browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(self.browse_button)
        self.clear_button = make_emoji_push_button("Clear", DELETE_BUTTON_EMOJI)
        self.clear_button.clicked.connect(self._clear_file)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.file_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)


class FilesListWidget(QWidget):
    """Widget for multiple file selection with drag and drop support."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize multi-file drop widget."""
        super().__init__(parent)
        self.file_paths: list[str] = []
        self._setup_ui()

    def get_file_paths(self) -> list[str]:
        """Return copy of selected file paths."""
        return self.file_paths.copy()

    def set_file_paths(self, paths: list[str]) -> None:
        """Replace selected files with existing paths from `paths`."""
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_file_path(path)

    def _add_file_path(self, file_path: str) -> None:
        self.file_paths.append(file_path)
        item = QListWidgetItem(Path(file_path).name)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.list_widget.addItem(item)

    def _add_files(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select files", "", "All files (*)")
        for file_path in file_paths:
            if file_path not in self.file_paths:
                self._add_file_path(file_path)

    def _clear_all(self) -> None:
        self.file_paths.clear()
        self.list_widget.clear()

    def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if file_path not in self.file_paths:
                self._add_file_path(file_path)

    def _remove_selected(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.file_paths:
                    self.file_paths.remove(file_path)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(150)
        install_url_drop_handlers(self.list_widget, self._on_drop_paths)

        button_layout = QHBoxLayout()
        self.add_button = make_emoji_push_button("Add Files", "➕")  # noqa: RUF001
        self.add_button.clicked.connect(self._add_files)
        button_layout.addWidget(self.add_button)
        self.remove_button = make_emoji_push_button("Remove Selected", "➖")  # noqa: RUF001
        self.remove_button.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_button)
        self.clear_button = make_emoji_push_button("Clear All", DELETE_BUTTON_EMOJI)
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)


_EMPTY_DROP_STYLE = """
    QLabel {
        border: 2px dashed #ccc;
        border-radius: 5px;
        padding: 20px;
        background-color: #f9f9f9;
    }
"""

_SELECTED_DROP_STYLE = """
    QLabel {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
        background-color: #f0f8f0;
    }
"""
