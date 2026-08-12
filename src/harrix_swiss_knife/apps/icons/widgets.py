"""Widgets for the Vector Icons browser grid and variant panel."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QMimeData, QPoint, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDrag, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.icons.thumb_cache import DEFAULT_THUMB_SIZE, render_svg_to_image

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.icons.catalog import IconFamily


class DraggableIconList(QListWidget):
    """Icon grid/list that drags the underlying SVG file URL outward."""

    family_activated = Signal(object)  # IconFamily
    copy_path_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None, *, icon_size: int = DEFAULT_THUMB_SIZE) -> None:
        """Configure icon mode and drag-only outward behavior."""
        super().__init__(parent)
        self._icon_size = icon_size
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
        self.itemDoubleClicked.connect(self._on_item_activated)
        self.itemActivated.connect(self._on_item_activated)

    def set_family_items(
        self,
        families: list[IconFamily],
        *,
        pixmaps: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        """Rebuild the grid from filtered families and available thumbnails."""
        self.clear()
        for family in families:
            pixmap = pixmaps.get(family.id) or placeholder
            item = QListWidgetItem(QIcon(pixmap), family.title)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setToolTip(f"{family.id}\n{', '.join(family.tags)}")
            item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + 40))
            self.addItem(item)

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
        path = item.data(Qt.ItemDataRole.UserRole + 1)
        if not isinstance(path, str) or not path:
            return
        menu = QMenu(self)
        copy_action = menu.addAction("Copy path")
        chosen = menu.exec_(self.mapToGlobal(pos))
        if chosen is copy_action:
            QApplication.clipboard().setText(path)
            self.copy_path_requested.emit(path)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        family = item.data(Qt.ItemDataRole.UserRole)
        if family is not None and hasattr(family, "variants"):
            # Only emit for family grid items (variants dialog stores path in UserRole+1 only)
            if item.data(Qt.ItemDataRole.UserRole + 2) == "variant":
                return
            self.family_activated.emit(family)


class VariantsDialog(QDialog):
    """Dialog listing SVG variants for one icon family with drag support."""

    def __init__(
        self,
        family: IconFamily,
        repo_root: Path,
        parent: QWidget | None = None,
        *,
        thumb_size: int = 128,
    ) -> None:
        """Build a list of variants with rendered previews."""
        super().__init__(parent)
        self.setWindowTitle(f"{family.title} — variants")
        self.resize(640, 480)
        layout = QVBoxLayout(self)
        header = QLabel(f"{family.id}\nCategories: {', '.join(family.categories)}")
        header.setWordWrap(True)
        layout.addWidget(header)

        self.list = DraggableIconList(icon_size=thumb_size)
        layout.addWidget(self.list)

        for variant in family.variants:
            path = variant.absolute_path(repo_root, family.folder)
            pixmap = self._preview(path, thumb_size)
            item = QListWidgetItem(QIcon(pixmap), variant.name)
            item.setData(Qt.ItemDataRole.UserRole, family)
            item.setData(Qt.ItemDataRole.UserRole + 1, str(path))
            item.setData(Qt.ItemDataRole.UserRole + 2, "variant")
            item.setToolTip(str(path))
            self.list.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_btn is not None:
            close_btn.clicked.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _preview(path: Path, size: int) -> QPixmap:
        image = render_svg_to_image(path, size)
        if image is None:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.lightGray)
            return pixmap
        return QPixmap.fromImage(image)
