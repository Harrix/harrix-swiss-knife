"""Single-image picker with drag-and-drop, clipboard paste, and file dialog."""

from __future__ import annotations

import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif"}

_MIME_BY_SUFFIX: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".avif": "image/avif",
}


class ImageDropWidget(QWidget):
    """Widget for single image selection with drag and drop and clipboard paste.

    When save_dir is set (e.g. parent of the target markdown file), dropped or pasted
    images are copied into save_dir/img/ and the returned path is relative (img/...).
    """

    image_changed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        save_dir: Path | None = None,
    ) -> None:
        """Initialize the image drop widget.

        Args:

        - `parent` (`QWidget | None`): Parent widget. Defaults to `None`.
        - `save_dir` (`Path | None`): If set, images are copied into `save_dir/img/`
          and path returned as `img/filename`.

        """
        super().__init__(parent)
        self.image_path = ""
        self._save_dir = Path(save_dir) if save_dir else None
        self._filename_line_edit: QLineEdit | None = None
        self._setup_ui()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle Ctrl+V when focus is on the image label."""
        if (
            watched == self.image_label
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_V
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._paste_from_clipboard()
            return True
        return super().eventFilter(watched, event)

    def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        """Read the selected image file as bytes and return MIME type."""
        if not self.image_path:
            return None
        path = Path(self.image_path)
        if not path.is_file():
            return None
        mime = _MIME_BY_SUFFIX.get(path.suffix.lower(), "image/png")
        try:
            data = path.read_bytes()
        except OSError:
            return None
        return (data, mime)

    def get_image_path(self) -> str:
        """Get the selected image path (relative to save_dir when save_dir was set)."""
        if not self.image_path:
            return ""
        if self._save_dir:
            try:
                p = Path(self.image_path).resolve()
                if str(p).startswith(str(self._save_dir.resolve())):
                    return str(p.relative_to(self._save_dir)).replace("\\", "/")
            except (ValueError, OSError):
                pass
        return self.image_path

    def has_image(self) -> bool:
        """Return True if an image is selected."""
        return bool(self.image_path) and Path(self.image_path).is_file()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Ctrl+V to paste image from clipboard."""
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._paste_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    def set_date_widget(self, date_edit: QDateEdit | None) -> None:
        """Add a Filename row synced with the event date (e.g. for Events template). Call after UI is built."""
        if not date_edit or not self._save_dir:
            return
        if self._filename_line_edit is not None:
            return

        self._filename_line_edit = QLineEdit()
        self._filename_line_edit.setPlaceholderText("Filename (without extension)")
        self._filename_line_edit.setText(date_edit.date().toString("yyyy-MM-dd"))
        date_edit.dateChanged.connect(lambda d, edit=self._filename_line_edit: edit.setText(d.toString("yyyy-MM-dd")))
        filerow = QHBoxLayout()
        filerow.addWidget(QLabel("Filename:"))
        filerow.addWidget(self._filename_line_edit, 1)
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            layout.insertLayout(layout.count() - 1, filerow)

    def set_image_path(self, path: str) -> None:
        """Set the image path."""
        if path and Path(path).exists():
            self._set_image(path)

    def _browse_file(self) -> None:
        """Open file dialog to select image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)",
        )
        if file_path:
            self._set_image(file_path)

    def _clear_image(self) -> None:
        """Clear the selected image."""
        self.image_path = ""
        self.image_label.setText("Drag and drop image here, paste (Ctrl+V), or click button")
        self.image_label.setPixmap(QPixmap())
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)
        self.image_changed.emit()

    def _copy_to_save_dir(self, source: Path) -> Path:
        if self._save_dir is None:
            return source
        img_dir = self._save_dir / "img"
        img_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix.lower()
        base = self._get_suggested_basename(source.stem)
        dest = unique_path_in_folder(img_dir, base, suffix)
        shutil.copy2(source, dest)
        return dest

    def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event: QDropEvent) -> None:
        """Handle drop event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if self._is_image_file(file_path):
                    self._set_image(file_path)
            event.acceptProposedAction()

    def _get_suggested_basename(self, fallback: str) -> str:
        """Return suggested filename stem from internal Filename field or fallback."""
        if self._filename_line_edit:
            text = self._filename_line_edit.text().strip()
            if text:
                size_limit = 200
                safe = re.sub(r'[<>:"/\\|?*]', "_", text).strip(" .") or fallback
                return safe[:size_limit] if len(safe) > size_limit else safe
        return fallback

    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image."""
        return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS

    def _paste_from_clipboard(self) -> None:
        """Set image from clipboard if an image is available."""
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()
        if qimage.isNull():
            return
        if self._save_dir:
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
            base = self._get_suggested_basename(f"pasted_{stamp}")
            dest = unique_path_in_folder(img_dir, base, ".png")
            if qimage.save(str(dest)):
                self._set_image(str(dest))
        else:
            with NamedTemporaryFile(suffix=".png", delete=False) as f:
                tmp = Path(f.name)
            if qimage.save(str(tmp)):
                self._set_image(str(tmp))

    def _set_image(self, file_path: str) -> None:
        """Set the image from file path."""
        source = Path(file_path).resolve()
        if not source.exists():
            return
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                if img_dir in source.parents or source.parent == img_dir:
                    self.image_path = str(source)
                else:
                    dest = self._copy_to_save_dir(source)
                    self.image_path = str(dest)
            except (OSError, ValueError):
                self.image_path = file_path
        else:
            self.image_path = file_path
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    padding: 5px;
                    background-color: #f0f8f0;
                }
            """)
            self.image_changed.emit()
        else:
            self._clear_image()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()

        self.image_label = QLabel("Drag and drop image here, paste (Ctrl+V), or click button")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        """)
        self.image_label.setMinimumHeight(100)
        self.image_label.setAcceptDrops(True)
        self.image_label.installEventFilter(self)
        self.image_label.dragEnterEvent = self._drag_enter_event  # ty: ignore[invalid-assignment]
        self.image_label.dropEvent = self._drop_event  # ty: ignore[invalid-assignment]

        button_layout = QHBoxLayout()

        self.browse_button = QPushButton("Select File")
        self.browse_button.clicked.connect(self._browse_file)
        button_layout.addWidget(self.browse_button)

        self.paste_button = QPushButton("Paste")
        self.paste_button.clicked.connect(self._paste_from_clipboard)
        button_layout.addWidget(self.paste_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_image)
        button_layout.addWidget(self.clear_button)

        layout.addWidget(self.image_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)


def unique_path_in_folder(folder: Path, base_name: str, suffix: str) -> Path:
    """Return a path in folder that does not exist, using base_name and suffix with _1, _2 if needed."""
    path = folder / (base_name + suffix)
    if not path.exists():
        return path
    i = 1
    while True:
        path = folder / (f"{base_name}_{i}{suffix}")
        if not path.exists():
            return path
        i += 1
