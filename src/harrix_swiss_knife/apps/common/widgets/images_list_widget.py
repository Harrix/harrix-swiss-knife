"""Multi-image drag-and-drop widget for template dialogs."""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.widgets.image_drop_widget import _IMAGE_EXTENSIONS
from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import (
    get_suggested_basename,
    install_url_drop_handlers,
    unique_path_numbered,
)


class ImagesListWidget(QWidget):
    """Widget for multiple image selection with drag and drop support."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self.image_paths: list[str] = []
        self._save_dir = Path(save_dir) if save_dir else None
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()

    def get_image_paths(self) -> list[str]:
        if not self._save_dir:
            return self.image_paths.copy()
        result = []
        for path in self.image_paths:
            if not path:
                continue
            try:
                resolved = Path(path).resolve()
                save_resolved = self._save_dir.resolve()
                if str(resolved).startswith(str(save_resolved)):
                    result.append(str(resolved.relative_to(save_resolved)).replace("\\", "/"))
                else:
                    result.append(path)
            except (ValueError, OSError):
                result.append(path)
        return result

    def set_date_widget(self, date_edit: QDateEdit | None) -> None:
        if not date_edit or not self._save_dir or self._filename_line_edit is not None:
            return
        self._filename_line_edit = QLineEdit()
        self._filename_line_edit.setPlaceholderText("Base name (e.g. date); images will be named base_01, base_02, ...")
        self._filename_line_edit.setText(date_edit.date().toString("yyyy-MM-dd"))
        date_edit.dateChanged.connect(lambda d, edit=self._filename_line_edit: edit.setText(d.toString("yyyy-MM-dd")))
        filerow = QHBoxLayout()
        filerow.addWidget(QLabel("Filename base:"))
        filerow.addWidget(self._filename_line_edit, 1)
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertLayout(layout.count() - 1, filerow)

    def set_image_paths(self, paths: list[str]) -> None:
        self._clear_all()
        for path in paths:
            if Path(path).exists():
                self._add_image_path(path)

    def _add_image_path(self, file_path: str) -> None:
        source = Path(file_path).resolve()
        if not source.exists():
            return
        path_to_store = file_path
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                img_dir.mkdir(parents=True, exist_ok=True)
                if img_dir in source.parents or source.parent == img_dir:
                    path_to_store = str(source)
                else:
                    suffix = source.suffix.lower()
                    base = get_suggested_basename(self._filename_line_edit, source.stem)
                    dest = unique_path_numbered(img_dir, base, suffix)
                    shutil.copy2(source, dest)
                    path_to_store = str(dest)
            except (OSError, ValueError):
                pass
        self.image_paths.append(path_to_store)
        item = QListWidgetItem(Path(path_to_store).name)
        item.setData(Qt.ItemDataRole.UserRole, path_to_store)
        self.list_widget.addItem(item)

    def _add_images(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        for file_path in file_paths:
            if file_path not in self.image_paths:
                self._add_image_path(file_path)

    def _clear_all(self) -> None:
        self.image_paths.clear()
        self.list_widget.clear()

    def _is_image_file(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS

    def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if self._is_image_file(file_path) and file_path not in self.image_paths:
                self._add_image_path(file_path)

    def _remove_selected(self) -> None:
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if file_path in self.image_paths:
                    self.image_paths.remove(file_path)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(150)
        install_url_drop_handlers(self.list_widget, self._on_drop_paths, filter_path=self._is_image_file)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Images")
        self.add_button.clicked.connect(self._add_images)
        button_layout.addWidget(self.add_button)
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self._remove_selected)
        button_layout.addWidget(self.remove_button)
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self._clear_all)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)
