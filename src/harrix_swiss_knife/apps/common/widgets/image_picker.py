"""Unified image picker: single, multi, or compact drop zone."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QImage, QKeyEvent, QPixmap
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
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.avif_manager import load_image_pixmap
from harrix_swiss_knife.apps.common.widgets.image_filename_row import ImageFilenameRow
from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import (
    get_suggested_basename,
    install_url_drop_handlers,
    unique_path_in_folder,
    unique_path_numbered,
)
from harrix_swiss_knife.qt_emoji_icon import COPY_BUTTON_EMOJI, create_emoji_icon, make_emoji_push_button

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from PySide6.QtGui import QFocusEvent, QMouseEvent

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

_THUMB_SIZE = 96
_REMOVE_BTN_SIZE = 24

_DEFAULT_COMPACT_HINT = "🖼️ Drag and drop images here, or paste (Ctrl+V)"
_DEFAULT_SINGLE_HINT = "Drag and drop image here, paste (Ctrl+V), or click button"
_DEFAULT_MULTI_HINT = "Drag and drop images here"

_DROP_NORMAL_STYLE = """
#ImagePickerDropArea {
    border: 2px dashed #ccc;
    border-radius: 5px;
    background-color: #f9f9f9;
}
"""

_DROP_FOCUSED_STYLE = """
#ImagePickerDropArea {
    border: 2px dashed #1565C0;
    border-radius: 5px;
    background-color: #e8f4ff;
}
"""

_DROP_SELECTED_STYLE = """
#ImagePickerDropArea {
    border: 2px solid #4CAF50;
    border-radius: 5px;
    background-color: #f0f8f0;
}
"""

_COMPACT_NORMAL_STYLE = """
#ImagePicker {
    border: 2px dashed #2196F3;
    border-radius: 4px;
    background-color: #f5faff;
}
"""

_COMPACT_FOCUSED_STYLE = """
#ImagePicker {
    border: 2px dashed #1565C0;
    border-radius: 4px;
    background-color: #e8f4ff;
}
"""

_COMPACT_HINT_STYLE = """
    QLabel {
        color: #1976D2;
        padding: 8px 4px 8px 8px;
        background: transparent;
        border: none;
    }
"""

_IMAGE_FILTER = "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg *.webp *.avif);;All files (*)"


class ImagePicker(QWidget):
    """Configurable image picker for single, multi, or compact drop workflows."""

    image_changed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        mode: ImagePickerMode = ImagePickerMode.SINGLE,
        save_dir: Path | None = None,
        max_image_side: int | None = None,
        fallback_text_edit: QPlainTextEdit | None = None,
        on_paths: Callable[[list[str]], None] | None = None,
        hint_text: str | None = None,
        extra_drop_targets: Sequence[QWidget] = (),
        show_label: bool = False,
        label_text: str = "",
        show_select_button: bool | None = None,
        show_add_button: bool | None = None,
        show_paste_button: bool | None = None,
        show_clear_button: bool | None = None,
    ) -> None:
        """Initialize the image picker.

        Args:

        - `mode`: `SINGLE`, `MULTI`, or `COMPACT`.
        - `save_dir`: When set, images are copied into `save_dir/img/`.
        - `max_image_side`: Optional downscale limit for stored / pasted images.
        - `fallback_text_edit`: Paste text here when clipboard has text (single mode).
        - `on_paths`: Compact-mode callback with dropped/pasted paths.
        - `hint_text`: Override drop-area hint.
        - `extra_drop_targets`: Additional widgets that accept drops (compact).
        - `show_label` / `label_text`: Optional label above the drop area.
        - Button flags: when `None`, defaults follow the mode.

        """
        super().__init__(parent)
        self._mode = mode
        self._save_dir = Path(save_dir) if save_dir else None
        self._max_image_side = max_image_side
        self._fallback_text_edit = fallback_text_edit
        self._on_paths = on_paths
        self._hint_text = hint_text
        self._extra_drop_targets = list(extra_drop_targets)
        self._show_label = show_label
        self._label_text = label_text

        self._show_select_button = (
            show_select_button if show_select_button is not None else mode == ImagePickerMode.SINGLE
        )
        self._show_add_button = show_add_button if show_add_button is not None else mode == ImagePickerMode.MULTI
        self._show_paste_button = (
            show_paste_button if show_paste_button is not None else mode != ImagePickerMode.COMPACT
        )
        self._show_clear_button = show_clear_button if show_clear_button is not None else mode == ImagePickerMode.SINGLE

        self.image_path = ""
        self.image_paths: list[str] = []
        self._filename_line_edit: QLineEdit | None = None
        self._filename_row: ImageFilenameRow | None = None
        self._on_paths_added: Callable[[list[str]], None] | None = None
        self._thumbnail_items: list[ImageThumbnailItem] = []
        self._drop_has_focus = False

        self.setObjectName("ImagePicker")
        if mode == ImagePickerMode.COMPACT:
            self._setup_compact_ui()
        else:
            self._setup_picker_ui()

    def configure_filename_row(
        self,
        date_edit: QDateEdit | None,
        source_widget: QLineEdit | QComboBox | None = None,
        *,
        source_field_name: str | None = None,
        initial_base: str | None = None,
        lock_auto_sync: bool = False,
    ) -> None:
        """Add filename row synced with date and optional linked template field."""
        if self._mode == ImagePickerMode.COMPACT or not date_edit or not self._save_dir:
            return
        if self._filename_line_edit is not None:
            return

        row = ImageFilenameRow(
            multiple=self._mode == ImagePickerMode.MULTI,
            date_edit=date_edit,
            source_widget=source_widget,
            source_field_name=source_field_name,
            initial_base=initial_base,
            lock_auto_sync=lock_auto_sync,
        )
        self._filename_line_edit = row.line_edit
        self._filename_row = row
        layout = self.layout()
        if isinstance(layout, QVBoxLayout):
            # Insert before the button row (last item).
            layout.insertWidget(max(layout.count() - 1, 0), row)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle focus, click-to-focus, and Ctrl+V on drop surfaces."""
        if self._mode == ImagePickerMode.COMPACT:
            if event.type() == QEvent.Type.MouseButtonPress and (
                watched is getattr(self, "_hint_label", None) or watched is getattr(self, "_compact_paste_button", None)
            ):
                self.setFocus(Qt.FocusReason.MouseFocusReason)
            return super().eventFilter(watched, event)

        drop = getattr(self, "_drop_area", None)
        if watched is drop:
            if event.type() == QEvent.Type.FocusIn:
                self._drop_has_focus = True
                self._refresh_drop_style()
            elif event.type() == QEvent.Type.FocusOut:
                self._drop_has_focus = False
                self._refresh_drop_style()
            elif (
                event.type() == QEvent.Type.KeyPress
                and isinstance(event, QKeyEvent)
                and event.key() == Qt.Key.Key_V
                and event.modifiers() == Qt.KeyboardModifier.ControlModifier
            ):
                self._paste_image_from_clipboard()
                return True
            elif event.type() == QEvent.Type.MouseButtonPress:
                drop.setFocus(Qt.FocusReason.MouseFocusReason)
        return super().eventFilter(watched, event)

    def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Show focused styling in compact mode."""
        if self._mode == ImagePickerMode.COMPACT:
            self.setStyleSheet(_COMPACT_FOCUSED_STYLE)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Restore default styling in compact mode."""
        if self._mode == ImagePickerMode.COMPACT:
            self.setStyleSheet(_COMPACT_NORMAL_STYLE)
        super().focusOutEvent(event)

    def get_image_bytes_and_mime(self) -> tuple[bytes, str] | None:
        """Return bytes and MIME for the first selected image, or `None`."""
        images = self.get_images_bytes_and_mime()
        return images[0] if images else None

    def get_image_path(self) -> str:
        """Get the selected image path (relative to save_dir when configured)."""
        if self._mode == ImagePickerMode.MULTI:
            paths = self.get_image_paths()
            return paths[0] if paths else ""
        if not self.image_path:
            return ""
        return self._path_relative_to_save_dir(self.image_path)

    def get_image_paths(self) -> list[str]:
        """Return image paths, relative to `save_dir` when configured."""
        if self._mode == ImagePickerMode.SINGLE:
            path = self.get_image_path()
            return [path] if path else []
        if self._mode == ImagePickerMode.COMPACT:
            return []
        return [self._path_relative_to_save_dir(path) for path in self.image_paths if path]

    def get_images_bytes_and_mime(self) -> list[tuple[bytes, str]]:
        """Read all selected image files as `(bytes, mime)` pairs."""
        paths = [self.image_path] if self._mode == ImagePickerMode.SINGLE else list(self.image_paths)
        result: list[tuple[bytes, str]] = []
        for path_str in paths:
            if not path_str:
                continue
            path = Path(path_str)
            if not path.is_file():
                continue
            mime = _MIME_BY_SUFFIX.get(path.suffix.lower(), "image/png")
            try:
                data = path.read_bytes()
            except OSError:
                continue
            result.append((data, mime))
        return result

    def has_image(self) -> bool:
        """Return `True` if at least one image is selected."""
        if self._mode == ImagePickerMode.MULTI:
            return any(Path(path).is_file() for path in self.image_paths)
        return bool(self.image_path) and Path(self.image_path).is_file()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Ctrl+V to paste image from clipboard."""
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self._mode == ImagePickerMode.COMPACT:
                self._compact_paste_from_clipboard()
            else:
                self._paste_image_from_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    @property
    def mode(self) -> ImagePickerMode:
        """Return the picker mode."""
        return self._mode

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Focus compact zone on click so Ctrl+V works."""
        if self._mode == ImagePickerMode.COMPACT:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
        super().mousePressEvent(event)

    def paste_from_clipboard(self) -> None:
        """Paste text into fallback editor when available, otherwise paste image."""
        self._paste_smart_from_clipboard()

    def paste_image_from_clipboard(self) -> None:
        """Paste image from clipboard into the picker."""
        self._paste_image_from_clipboard()

    def refresh_filename_base(self) -> None:
        """Recompute filename base from linked template fields."""
        if self._filename_row is not None:
            self._filename_row.refresh_auto_base()

    def reset_filename_row(self) -> None:
        """Remove filename row so it can be reconfigured."""
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
        self._filename_row = None

    def set_image_path(self, path: str) -> None:
        """Set a single image path (single mode), or clear when empty."""
        if self._mode == ImagePickerMode.MULTI:
            if path:
                self.set_image_paths([path])
            else:
                self.set_image_paths([])
            return
        if not path:
            self._clear_single_image()
            return
        if Path(path).exists():
            self._set_single_image(path)

    def set_image_paths(self, paths: list[str]) -> None:
        """Replace selected images (multi) or set the first path (single)."""
        if self._mode == ImagePickerMode.SINGLE:
            if paths:
                self.set_image_path(paths[0])
            else:
                self.set_image_path("")
            return
        if self._mode == ImagePickerMode.COMPACT:
            return
        self._clear_all_multi()
        for path in paths:
            resolved = self._resolve_image_path(path)
            if resolved is not None:
                self._add_multi_image_path(str(resolved), skip_copy_if_in_img_dir=True, from_user_add=False)

    def set_on_paths_added(self, callback: Callable[[list[str]], None] | None) -> None:
        """Register callback invoked with original paths when user adds images."""
        self._on_paths_added = callback

    def set_save_dir(self, save_dir: Path | None) -> None:
        """Update target directory for copied images."""
        self._save_dir = Path(save_dir) if save_dir else None

    def _add_images_dialog(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", _IMAGE_FILTER)
        valid_paths = [file_path for file_path in file_paths if is_image_file_path(file_path)]
        self._notify_paths_added(valid_paths)
        if self._mode == ImagePickerMode.SINGLE:
            if valid_paths:
                self._set_single_image(valid_paths[0])
            return
        for file_path in valid_paths:
            self._add_multi_image_path(file_path)

    def _add_multi_image_path(
        self,
        file_path: str,
        *,
        skip_copy_if_in_img_dir: bool = False,
        from_user_add: bool = True,
    ) -> None:
        del from_user_add
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
        thumb = ImageThumbnailItem(
            path_to_store,
            on_remove=self._remove_multi_image_path,
            parent=self._thumbs_container,
        )
        self._thumbnail_items.append(thumb)
        self._thumbs_layout.insertWidget(self._thumbs_layout.count() - 1, thumb)
        self._update_multi_drop_state()
        self.image_changed.emit()

    def _add_user_single_image(self, file_path: str) -> None:
        source = str(Path(file_path).resolve())
        if self._on_paths_added is not None:
            self._on_paths_added([source])
        self._set_single_image(file_path)

    def _browse_single_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", _IMAGE_FILTER)
        if file_path:
            self._add_user_single_image(file_path)

    def _clear_all_multi(self) -> None:
        for thumb in self._thumbnail_items:
            thumb.setParent(None)
            thumb.deleteLater()
        self._thumbnail_items.clear()
        self.image_paths.clear()
        self._update_multi_drop_state()
        self.image_changed.emit()

    def _clear_single_image(self) -> None:
        self.image_path = ""
        if hasattr(self, "_preview_label"):
            self._preview_label.setText(self._hint_text or _DEFAULT_SINGLE_HINT)
            self._preview_label.setPixmap(QPixmap())
        self._refresh_drop_style()
        self.image_changed.emit()

    def _compact_paste_from_clipboard(self) -> None:
        temp_path = save_clipboard_image_to_temp_file(max_image_side=self._max_image_side)
        if temp_path and self._on_paths is not None:
            self._on_paths([temp_path])

    def _copy_to_save_dir_single(self, source: Path) -> Path:
        if self._save_dir is None:
            return source
        img_dir = self._save_dir / "img"
        img_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix.lower()
        base = get_suggested_basename(self._filename_line_edit, source.stem)
        dest = unique_path_in_folder(img_dir, base, suffix)
        shutil.copy2(source, dest)
        return dest

    def _downscale_file_if_needed(self, path: Path) -> None:
        if not self._max_image_side or not path.is_file():
            return
        if path.suffix.lower() == ".svg":
            return
        qimage = QImage(str(path))
        if qimage.isNull():
            return
        scaled = downscale_qimage(qimage, self._max_image_side)
        if scaled.width() == qimage.width() and scaled.height() == qimage.height():
            return
        scaled.save(str(path))

    def _notify_paths_added(self, paths: list[str]) -> None:
        if paths and self._on_paths_added is not None:
            self._on_paths_added(paths)

    def _on_drop_paths(self, paths: list[str]) -> None:
        valid_paths = [file_path for file_path in paths if is_image_file_path(file_path)]
        if not valid_paths:
            return
        if self._mode == ImagePickerMode.COMPACT:
            if self._on_paths is not None:
                self._on_paths(valid_paths)
            return
        self._notify_paths_added(valid_paths)
        if self._mode == ImagePickerMode.SINGLE:
            self._set_single_image(valid_paths[0])
            return
        for file_path in valid_paths:
            self._add_multi_image_path(file_path)

    def _paste_image_from_clipboard(self) -> None:
        if self._mode == ImagePickerMode.COMPACT:
            self._compact_paste_from_clipboard()
            return
        clipboard = QApplication.clipboard()
        qimage = clipboard.image()
        if qimage.isNull():
            return
        qimage = downscale_qimage(qimage, self._max_image_side)
        if self._save_dir:
            img_dir = self._save_dir / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            if self._mode == ImagePickerMode.SINGLE:
                stamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
                base = get_suggested_basename(self._filename_line_edit, f"pasted_{stamp}")
            else:
                base = get_suggested_basename(self._filename_line_edit, "pasted")
            dest = unique_path_in_folder(img_dir, base, ".png")
            if qimage.save(str(dest)):
                if self._mode == ImagePickerMode.SINGLE:
                    self._set_single_image(str(dest))
                else:
                    self._add_multi_image_path(str(dest), skip_copy_if_in_img_dir=True)
            return
        temp_path = save_clipboard_image_to_temp_file(max_image_side=self._max_image_side)
        if not temp_path:
            return
        if self._mode == ImagePickerMode.SINGLE:
            self._set_single_image(temp_path)
        else:
            self._add_multi_image_path(temp_path)

    def _paste_smart_from_clipboard(self) -> None:
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if self._fallback_text_edit is not None and text:
            self._fallback_text_edit.insertPlainText(text)
            return
        self._paste_image_from_clipboard()

    def _path_relative_to_save_dir(self, path: str) -> str:
        if not path or not self._save_dir:
            return path
        try:
            resolved = Path(path).resolve()
            save_resolved = self._save_dir.resolve()
            if str(resolved).startswith(str(save_resolved)):
                return str(resolved.relative_to(save_resolved)).replace("\\", "/")
        except (ValueError, OSError):
            pass
        return path

    def _refresh_drop_style(self) -> None:
        if not hasattr(self, "_drop_area"):
            return
        if self._mode == ImagePickerMode.SINGLE and self.image_path:
            self._drop_area.setStyleSheet(_DROP_SELECTED_STYLE)
        elif self._drop_has_focus:
            self._drop_area.setStyleSheet(_DROP_FOCUSED_STYLE)
        else:
            self._drop_area.setStyleSheet(_DROP_NORMAL_STYLE)

    def _remove_multi_image_path(self, path: str) -> None:
        if path in self.image_paths:
            self.image_paths.remove(path)
        for thumb in list(self._thumbnail_items):
            if thumb.image_path == path:
                self._thumbnail_items.remove(thumb)
                thumb.setParent(None)
                thumb.deleteLater()
                break
        self._update_multi_drop_state()
        self.image_changed.emit()

    def _resolve_image_path(self, path: str) -> Path | None:
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

    def _set_single_image(self, file_path: str) -> None:
        source = Path(file_path).resolve()
        if not source.exists():
            return
        if self._save_dir:
            try:
                img_dir = self._save_dir.resolve() / "img"
                if img_dir in source.parents or source.parent == img_dir:
                    self.image_path = str(source)
                else:
                    dest = self._copy_to_save_dir_single(source)
                    self.image_path = str(dest)
            except (OSError, ValueError):
                self.image_path = file_path
        else:
            self.image_path = file_path
        self._downscale_file_if_needed(Path(self.image_path))
        if hasattr(self, "_preview_label"):
            pixmap = load_image_pixmap(self.image_path)
            if pixmap is not None and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self._preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._preview_label.setPixmap(scaled_pixmap)
                self._preview_label.setText("")
            else:
                self._preview_label.setPixmap(QPixmap())
                self._preview_label.setText(Path(self.image_path).name)
        self._refresh_drop_style()
        self.image_changed.emit()

    def _setup_compact_ui(self) -> None:
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setMinimumHeight(48)
        self.setStyleSheet(_COMPACT_NORMAL_STYLE)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(0)

        hint = self._hint_text or _DEFAULT_COMPACT_HINT
        self._hint_label = QLabel(hint)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint_label.setStyleSheet(_COMPACT_HINT_STYLE)
        self._hint_label.setWordWrap(True)
        self._hint_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._hint_label.installEventFilter(self)
        layout.addWidget(self._hint_label, stretch=1)

        self._compact_paste_button = QPushButton()
        self._compact_paste_button.setIcon(create_emoji_icon(COPY_BUTTON_EMOJI, 18))
        self._compact_paste_button.setFixedSize(32, 32)
        self._compact_paste_button.setToolTip("Paste image from clipboard (Ctrl+V)")
        self._compact_paste_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._compact_paste_button.installEventFilter(self)
        self._compact_paste_button.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            "QPushButton:hover { background-color: #bbdefb; border-radius: 4px; }"
        )
        self._compact_paste_button.clicked.connect(self._compact_paste_from_clipboard)
        layout.addWidget(self._compact_paste_button)

        for target in [self, *self._extra_drop_targets]:
            install_url_drop_handlers(target, self._on_drop_paths, filter_path=is_image_file_path)

    def _setup_picker_ui(self) -> None:
        layout = QVBoxLayout(self)

        if self._show_label and self._label_text:
            layout.addWidget(QLabel(self._label_text))

        self._drop_area = QFrame()
        self._drop_area.setObjectName("ImagePickerDropArea")
        self._drop_area.setFrameShape(QFrame.Shape.NoFrame)
        self._drop_area.setMinimumHeight(100 if self._mode == ImagePickerMode.SINGLE else 120)
        self._drop_area.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._drop_area.installEventFilter(self)
        self._refresh_drop_style()

        drop_layout = QVBoxLayout(self._drop_area)

        if self._mode == ImagePickerMode.SINGLE:
            self._preview_label = QLabel(self._hint_text or _DEFAULT_SINGLE_HINT)
            self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._preview_label.setStyleSheet("border: none; background: transparent;")
            self._preview_label.setMinimumHeight(100)
            drop_layout.addWidget(self._preview_label)
        else:
            self._thumbs_container = QWidget()
            self._thumbs_container.setStyleSheet("background: transparent;")
            self._thumbs_layout = QHBoxLayout(self._thumbs_container)
            self._thumbs_layout.setContentsMargins(4, 4, 4, 4)
            self._thumbs_layout.setSpacing(8)
            self._thumbs_layout.addStretch()

            self._drop_hint = QLabel(self._hint_text or _DEFAULT_MULTI_HINT)
            self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._drop_hint.setStyleSheet("border: none; background: transparent; color: #888;")
            self._thumbs_scroll = QScrollArea()
            self._thumbs_scroll.setFrameShape(QFrame.Shape.NoFrame)
            self._thumbs_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            self._thumbs_scroll.setWidgetResizable(True)
            self._thumbs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self._thumbs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._thumbs_scroll.setWidget(self._thumbs_container)
            self._thumbs_scroll.setMinimumHeight(_THUMB_SIZE + 16)
            drop_layout.addWidget(self._drop_hint, 1)
            drop_layout.addWidget(self._thumbs_scroll, 1)
            self._update_multi_drop_state()

        install_url_drop_handlers(self._drop_area, self._on_drop_paths, filter_path=is_image_file_path)

        if self._mode == ImagePickerMode.MULTI:
            scroll = QScrollArea()
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            scroll.setWidgetResizable(True)
            scroll.setWidget(self._drop_area)
            scroll.setMinimumHeight(140)
            layout.addWidget(scroll)
        else:
            layout.addWidget(self._drop_area)

        button_layout = QHBoxLayout()
        if self._show_select_button:
            browse_button = make_emoji_push_button("Select File", "📁")
            browse_button.clicked.connect(self._browse_single_file)
            button_layout.addWidget(browse_button)
        if self._show_add_button:
            add_button = make_emoji_push_button("Add Images", "➕")  # noqa: RUF001
            add_button.clicked.connect(self._add_images_dialog)
            button_layout.addWidget(add_button)
        if self._show_paste_button:
            paste_button = make_emoji_push_button("Paste", COPY_BUTTON_EMOJI)
            if self._mode == ImagePickerMode.SINGLE:
                paste_button.clicked.connect(self._paste_smart_from_clipboard)
            else:
                paste_button.clicked.connect(self._paste_image_from_clipboard)
            button_layout.addWidget(paste_button)
        if self._show_clear_button:
            clear_button = make_emoji_push_button("Clear", "🗑️")
            clear_button.clicked.connect(self._clear_single_image)
            button_layout.addWidget(clear_button)
        if self._mode == ImagePickerMode.MULTI:
            button_layout.addStretch()
        layout.addLayout(button_layout)

    def _update_multi_drop_state(self) -> None:
        if not hasattr(self, "_drop_hint"):
            return
        has_images = bool(self._thumbnail_items)
        self._drop_hint.setVisible(not has_images)
        self._thumbs_scroll.setVisible(has_images)
        self._refresh_drop_style()


class ImagePickerMode(Enum):
    """Display and interaction mode for `ImagePicker`."""

    SINGLE = "single"
    MULTI = "multi"
    COMPACT = "compact"


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
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("ImageThumbnailItem { border: none; background: transparent; }")

        grid = QGridLayout(self)
        grid.setContentsMargins(2, 2, 2, 2)
        grid.setSpacing(0)

        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = load_image_pixmap(image_path)
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

        remove_btn = QPushButton("×")  # noqa: RUF001
        remove_btn.setFixedSize(_REMOVE_BTN_SIZE, _REMOVE_BTN_SIZE)
        remove_btn.setStyleSheet(
            "QPushButton { background: #e53935; color: white; border: none; border-radius: 12px; "
            "font-size: 16px; font-weight: bold; padding: 0; min-width: 0; min-height: 0; }"
            "QPushButton:hover { background: #c62828; }"
        )
        remove_btn.clicked.connect(self._handle_remove)
        grid.addWidget(remove_btn, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

    def _handle_remove(self) -> None:
        self._on_remove(self.image_path)


def downscale_qimage(qimage: QImage, max_side: int | None) -> QImage:
    """Return image scaled down so neither side exceeds max_side."""
    if qimage.isNull() or not max_side or max_side <= 0:
        return qimage
    if qimage.width() <= max_side and qimage.height() <= max_side:
        return qimage
    return qimage.scaled(
        max_side,
        max_side,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def is_image_file_path(file_path: str) -> bool:
    """Return `True` if path has a supported image extension."""
    return Path(file_path).suffix.lower() in _IMAGE_EXTENSIONS


def save_clipboard_image_to_temp_file(*, max_image_side: int | None = None) -> str | None:
    """Save clipboard image to a temporary PNG file and return its path."""
    qimage = QApplication.clipboard().image()
    if qimage.isNull():
        return None
    qimage = downscale_qimage(qimage, max_image_side)
    with NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp = Path(f.name)
    if qimage.save(str(tmp)):
        return str(tmp)
    return None
