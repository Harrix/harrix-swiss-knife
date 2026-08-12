"""Widgets for the Vector Icons browser grid and variant panel."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QMimeData, QPoint, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDrag, QIcon, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.icons.thumb_cache import (
    DEFAULT_THUMB_SIZE,
    placeholder_pixmap,
    render_svg_to_image,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.icons.catalog import IconFamily

VARIANT_THUMB_SIZE = 112


class DraggableIconList(QListWidget):
    """Icon grid/list that drags the underlying SVG file URL outward."""

    family_selected = Signal(object)  # IconFamily | None
    reveal_requested = Signal(str)
    details_requested = Signal(object, str)  # IconFamily, svg_path
    copy_requested = Signal(str)
    open_note_requested = Signal(object)  # IconFamily
    reveal_source_requested = Signal(object, str)  # IconFamily, svg_path
    open_source_requested = Signal(object, str)  # IconFamily, svg_path

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        icon_size: int = DEFAULT_THUMB_SIZE,
        emit_family_selection: bool = True,
    ) -> None:
        """Configure icon mode and drag-only outward behavior."""
        super().__init__(parent)
        self._icon_size = icon_size
        self._emit_family_selection = emit_family_selection
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(8)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(QSize(icon_size + 24, icon_size + 48))
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        if emit_family_selection:
            self.currentItemChanged.connect(self._on_current_item_changed)

    def set_display_icon_size(self, icon_size: int) -> None:
        """Update icon and grid sizes used by the list."""
        self._icon_size = icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(QSize(icon_size + 24, icon_size + 48))

    def set_family_items(
        self,
        families: list[IconFamily],
        *,
        pixmaps: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        """Rebuild the grid from filtered families and available thumbnails."""
        self.blockSignals(True)  # noqa: FBT003
        self.clear()
        for family in families:
            pixmap = pixmaps.get(family.id) or placeholder
            item = QListWidgetItem(QIcon(pixmap), family.title)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setToolTip(f"{family.id}\n{', '.join(family.tags)}")
            item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + 40))
            self.addItem(item)
        self.blockSignals(False)  # noqa: FBT003
        if self._emit_family_selection:
            self.family_selected.emit(None)

    def startDrag(self, supported_actions: Qt.DropAction) -> None:  # noqa: ARG002, N802
        """Start an OS file drag for the selected SVG path."""
        item = self.currentItem()
        if item is None:
            return
        svg_path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not isinstance(svg_path, str) or not svg_path:
            return
        path = Path(svg_path)
        if not path.is_file():
            return
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(str(path.resolve()))])
        drag = QDrag(self)
        drag.setMimeData(mime)
        icon = item.icon()
        if not icon.isNull():
            drag.setPixmap(icon.pixmap(64, 64))
            drag.setHotSpot(QPoint(32, 32))
        drag.exec(Qt.DropAction.CopyAction)

    def update_family_pixmap(self, family_id: str, pixmap: QPixmap) -> None:
        """Update the icon for a family already present in the list."""
        for index in range(self.count()):
            item = self.item(index)
            if item is None:
                continue
            family = item.data(Qt.ItemDataRole.UserRole)
            if getattr(family, "id", None) == family_id:
                item.setIcon(QIcon(pixmap))
                break

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        family = item.data(Qt.ItemDataRole.UserRole)
        path = item.data(Qt.ItemDataRole.UserRole + 1)
        if family is None or not isinstance(path, str) or not path:
            return
        self.setCurrentItem(item)

        menu = QMenu(self)
        reveal_action = menu.addAction("📂 Reveal in File Explorer")
        details_action = menu.addAction("ℹ️ Icon details")  # noqa: RUF001
        copy_action = menu.addAction("📋 Copy")
        open_note_action = menu.addAction("📝 Open note in editor")
        menu.addSeparator()
        reveal_source_action = menu.addAction("📂 Reveal source in File Explorer")
        open_source_action = menu.addAction("🎨 Open source")
        chosen = menu.exec_(self.mapToGlobal(pos))
        if chosen is reveal_action:
            self.reveal_requested.emit(path)
        elif chosen is details_action:
            self.details_requested.emit(family, path)
        elif chosen is copy_action:
            self.copy_requested.emit(path)
        elif chosen is open_note_action:
            self.open_note_requested.emit(family)
        elif chosen is reveal_source_action:
            self.reveal_source_requested.emit(family, path)
        elif chosen is open_source_action:
            self.open_source_requested.emit(family, path)

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            self.family_selected.emit(None)
            return
        family = current.data(Qt.ItemDataRole.UserRole)
        if family is not None and hasattr(family, "variants"):
            self.family_selected.emit(family)
        else:
            self.family_selected.emit(None)


class VariantsPanel(QWidget):
    """Right-side panel showing SVG variants for the selected icon family."""

    def __init__(self, parent: QWidget | None = None, *, thumb_size: int = VARIANT_THUMB_SIZE) -> None:
        """Build header + draggable variants list."""
        super().__init__(parent)
        self._thumb_size = thumb_size
        self._repo_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.header = QLabel("Select an icon to see variants")
        self.header.setWordWrap(True)
        layout.addWidget(self.header)

        self.list = DraggableIconList(icon_size=thumb_size, emit_family_selection=False)
        layout.addWidget(self.list)

    def clear_variants(self) -> None:
        """Clear the variants list and reset the header."""
        self.list.clear()
        self.header.setText("Select an icon to see variants")

    def set_thumb_size(self, thumb_size: int) -> None:
        """Update variant thumbnail size (does not rebuild items)."""
        self._thumb_size = thumb_size
        self.list.set_display_icon_size(thumb_size)

    def show_family(self, family: IconFamily | None, repo_root: Path | None) -> None:
        """Populate the panel with variants of `family`."""
        self._repo_root = repo_root
        self.list.clear()
        if family is None or repo_root is None:
            self.header.setText("Select an icon to see variants")
            return

        tags = ", ".join(family.tags) if family.tags else "—"
        self.header.setText(
            f"{family.title}\n{family.id}\nCategories: {', '.join(family.categories)}\nTags: {tags}",
        )
        for variant in family.variants:
            path = variant.absolute_path(repo_root, family.folder)
            pixmap = self._preview(path, self._thumb_size)
            item = QListWidgetItem(QIcon(pixmap), variant.name)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setData(Qt.ItemDataRole.UserRole + 1, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)

    @staticmethod
    def _preview(path: Path, size: int) -> QPixmap:
        image = render_svg_to_image(path, size)
        if image is None:
            return placeholder_pixmap(size)
        return QPixmap.fromImage(image)
