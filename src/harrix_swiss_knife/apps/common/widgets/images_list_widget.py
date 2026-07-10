"""Multi-image drag-and-drop widget for template dialogs."""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.widgets.image_drop_widget import (
    _IMAGE_EXTENSIONS,
    _downscale_qimage,
    unique_path_in_folder,
)
from harrix_swiss_knife.apps.common.widgets.image_filename_row import ImageFilenameRow
from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import (
    get_suggested_basename,
    install_url_drop_handlers,
    unique_path_numbered,
)
from harrix_swiss_knife.qt_emoji_icon import COPY_BUTTON_EMOJI, make_emoji_push_button

if TYPE_CHECKING:
    from collections.abc import Callable

_THUMB_SIZE = 96
_REMOVE_BTN_SIZE = 18


class ImageThumbnailItem(QFrame):
    """Single image thumbnail with a remove button in the top-right corner."""

    def __init__(
        self,
        image_path: str,
        *,
        on_remove: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        """Build a thumbnail tile with a remove button."""
        super().__init__(parent)
        self.image_path = image_path
        self._on_remove = on_remove
        self.setFixedSize(_THUMB_SIZE, _THUMB_SIZE)
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet("ImageThumbnailItem { border: 1px solid #ccc; border-radius: 4px; background: #f9f9f9; }")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            thumb_label.setPixmap(
                pixmap.scaled(
                    _THUMB_SIZE - 8,
                    _THUMB_SIZE - 8,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            thumb_label.setText(Path(image_path).name)
        grid.addWidget(thumb_label, 0, 0)

        remove_btn = QPushButton("-")
        remove_btn.setFixedSize(_REMOVE_BTN_SIZE, _REMOVE_BTN_SIZE)
        remove_btn.setStyleSheet(
            "QPushButton { background: #e53935; color: white; border: none; border-radius: 9px; "
            "font-weight: bold; padding: 0; min-width: 0; min-height: 0; }"
            "QPushButton:hover { background: #c62828; }"
        )
        remove_btn.clicked.connect(self._handle_remove)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def _handle_remove(self) -> None:
        self._on_remove(self.image_path)


class ImagesListWidget(QWidget):
    """Widget for multiple image selection with drag and drop support."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
    ) -> None:
        """Initialize multi-image drop widget."""
        super().__init__(parent)
        self.image_paths: list[str] = []
        self._save_dir = Path(save_dir) if save_dir else None
        self._filename_line_edit: QLineEdit | None = None
        self._thumbnail_items: list[ImageThumbnailItem] = []
        self._setup_ui()

    def configure_filename_row(
        self,
        date_edit: QDateEdit | None,
        source_widget: QLineEdit | QComboBox | None = None,
        *,
        source_field_name: str | None = None,
        initial_base: str | None = None,
        lock_auto_sync: bool = False,
    ) -> None:
        """Add filename base row synced with date and optional linked template field."""
        if not date_edit or not self._save_dir or self._filename_line_edit is not None:
            return
        row = ImageFilenameRow(
            multiple=True,
            date_edit=date_edit,
            source_widget=source_widget,
            source_field_name=source_field_name,
            initial_base=initial_base,
            lock_auto_sync=lock_auto_sync,
        )
        self._filename_line_edit = row.line_edit
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertWidget(layout.count() - 1, row)

    def get_image_paths(self) -> list[str]:
        """Return image paths, relative to ``save_dir`` when configured."""
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

    def reset_filename_row(self) -> None:
        """Remove filename row so it can be reconfigured (e.g. when switching entries)."""
        if self._filename_line_edit is None:
            return
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            for index in range(layout.count()):
                item = layout.itemAt(index)
                widget = item.widget() if item is not None else None
                if isinstance(widget, ImageFilenameRow):
                    layout.removeWidget(widget)
                    widget.deleteLater()
                    break
        self._filename_line_edit = None

    def set_image_paths(self, paths: list[str]) -> None:
        """Replace selected images with existing paths from ``paths``."""
        self._clear_all()
        for path in paths:
            resolved = self._resolve_image_path(path)
            if resolved is not None:
                self._add_image_path(str(resolved), skip_copy_if_in_img_dir=True)

    def set_save_dir(self, save_dir: Path | None) -> None:
        """Update target directory for copied images."""
        self._save_dir = Path(save_dir) if save_dir else None

    def _add_image_path(self, file_path: str, *, skip_copy_if_in_img_dir: bool = False) -> None:
        resolved = self._resolve_image_path(file_path)
        if resolved is None:
            return
        source = resolved.resolve()
        if file_path in self.image_paths or str(source) in self.image_paths:
            return

        path_to_store = str(source)
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                img_dir.mkdir(parents=True, exist_ok=True)
                if (
                    (skip_copy_if_in_img_dir and (img_dir in source.parents or source.parent == img_dir))
                    or img_dir in source.parents
                    or source.parent == img_dir
                ):
                    path_to_store = str(source)
                else:
                    suffix = source.suffix.lower()
                    base = get_suggested_basename(self._filename_line_edit, source.stem)
                    dest = unique_path_numbered(img_dir, base, suffix)
                    shutil.copy2(source, dest)
                    path_to_store = str(dest)
            except (OSError, ValueError):
                return

        self.image_paths.append(path_to_store)
        thumb = ImageThumbnailItem(path_to_store, on_remove=self._remove_image_path, parent=self._thumbs_container)
        self._thumbnail_items.append(thumb)
        self._thumbs_layout.insertWidget(self._thumbs_layout.count() - 1, thumb)
        self._update_drop_area_state()

    def _add_images(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        for file_path in file_paths:
            self._add_image_path(file_path)

    def _clear_all(self) -> None:
        for thumb in self._thumbnail_items:
            thumb.setParent(None)
            thumb.deleteLater()
        self._thumbnail_items.clear()
        self.image_paths.clear()
        self._update_drop_area_state()

    def _is_image_file(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS

    def _on_drop_paths(self, paths: list[str]) -> None:
        for file_path in paths:
            if self._is_image_file(file_path):
                self._add_image_path(file_path)

    def _paste_image_from_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()
        if qimage.isNull():
            return
        qimage = _downscale_qimage(qimage, None)
        if self._save_dir:
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            base = get_suggested_basename(self._filename_line_edit, "pasted")
            dest = unique_path_in_folder(img_dir, base, ".png")
            if qimage.save(str(dest)):
                self._add_image_path(str(dest), skip_copy_if_in_img_dir=True)
        else:
            with NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = Path(f.name)
            if qimage.save(str(tmp)):
                self._add_image_path(str(tmp))

    def _remove_image_path(self, path: str) -> None:
        if path in self.image_paths:
            self.image_paths.remove(path)
        for thumb in list(self._thumbnail_items):
            if thumb.image_path == path:
                self._thumbnail_items.remove(thumb)
                thumb.setParent(None)
                thumb.deleteLater()
                break
        self._update_drop_area_state()

    def _resolve_image_path(self, path: str) -> Path | None:
        """Resolve absolute or relative image path against save_dir when needed."""
        if not path.strip():
            return None
        candidate = Path(path)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        if candidate.exists():
            return candidate.resolve()
        if self._save_dir is not None:
            for base in (self._save_dir, self._save_dir.parent):
                joined = (base / path).resolve()
                if joined.exists():
                    return joined
        return None

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        self._thumbs_container = QWidget()
        self._thumbs_layout = QHBoxLayout(self._thumbs_container)
        self._thumbs_layout.setContentsMargins(4, 4, 4, 4)
        self._thumbs_layout.setSpacing(8)
        self._thumbs_layout.addStretch()

        self._drop_area = QFrame()
        self._drop_area.setMinimumHeight(120)
        self._drop_area.setStyleSheet(
            "QFrame { border: 2px dashed #ccc; border-radius: 5px; background-color: #f9f9f9; }"
        )
        drop_layout = QVBoxLayout(self._drop_area)
        self._drop_hint = QLabel("Drag and drop images here")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint.setStyleSheet("border: none; background: transparent; color: #888;")
        self._thumbs_scroll = QScrollArea()
        self._thumbs_scroll.setWidgetResizable(True)
        self._thumbs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._thumbs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._thumbs_scroll.setWidget(self._thumbs_container)
        self._thumbs_scroll.setMinimumHeight(_THUMB_SIZE + 16)
        drop_layout.addWidget(self._drop_hint, 1)
        drop_layout.addWidget(self._thumbs_scroll, 1)
        install_url_drop_handlers(self._drop_area, self._on_drop_paths, filter_path=self._is_image_file)
        self._update_drop_area_state()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._drop_area)
        scroll.setMinimumHeight(140)

        button_layout = QHBoxLayout()
        self.add_button = make_emoji_push_button("Add Images", "➕")  # noqa: RUF001
        self.add_button.clicked.connect(self._add_images)
        button_layout.addWidget(self.add_button)
        self.paste_button = make_emoji_push_button("Paste", COPY_BUTTON_EMOJI)
        self.paste_button.clicked.connect(self._paste_image_from_clipboard)
        button_layout.addWidget(self.paste_button)
        button_layout.addStretch()

        layout.addWidget(scroll)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _update_drop_area_state(self) -> None:
        has_images = bool(self._thumbnail_items)
        self._drop_hint.setVisible(not has_images)
        self._thumbs_scroll.setVisible(has_images)
