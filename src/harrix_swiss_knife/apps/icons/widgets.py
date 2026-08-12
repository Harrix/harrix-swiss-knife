"""Widgets for the Vector Icons browser grid and variant panel."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QMimeData, QModelIndex, QPersistentModelIndex, QPoint, QRect, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QDrag, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.icons.thumb_cache import DEFAULT_THUMB_SIZE, placeholder_pixmap, render_icon_to_image

if TYPE_CHECKING:
    from harrix_swiss_knife.apps.icons.catalog import IconFamily
    from harrix_swiss_knife.apps.icons.variant_view import GridEntry

VARIANT_THUMB_SIZE = 112
ROLE_SVG_PATH = int(Qt.ItemDataRole.UserRole) + 1
ROLE_SUBTITLE = int(Qt.ItemDataRole.UserRole) + 2
LABEL_EXTRA_HEIGHT = 56


class DraggableIconList(QListWidget):
    """Icon grid/list that drags the underlying SVG file URL outward."""

    family_selected = Signal(object)  # IconFamily | None
    reveal_requested = Signal(str)
    details_requested = Signal(object, str)  # IconFamily, svg_path
    copy_requested = Signal(str)
    copy_path_requested = Signal(str)
    open_note_requested = Signal(object)  # IconFamily
    reveal_source_requested = Signal(object, str)  # IconFamily, svg_path
    open_source_requested = Signal(object, str)  # IconFamily, svg_path
    set_category_icon_requested = Signal(object)  # IconFamily

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        icon_size: int = DEFAULT_THUMB_SIZE,
        emit_family_selection: bool = True,
        dual_line_labels: bool = False,
    ) -> None:
        """Configure icon mode and drag-only outward behavior."""
        super().__init__(parent)
        self._icon_size = icon_size
        self._emit_family_selection = emit_family_selection
        self._dual_line_labels = dual_line_labels
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Static)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(8)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(self._grid_size_for(icon_size))
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)
        if dual_line_labels:
            self.setItemDelegate(IconLabelDelegate(self))
        if emit_family_selection:
            self.currentItemChanged.connect(self._on_current_item_changed)

    def set_display_icon_size(self, icon_size: int) -> None:
        """Update icon and grid sizes used by the list."""
        self._icon_size = icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setGridSize(self._grid_size_for(icon_size))

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
            item.setData(ROLE_SUBTITLE, family_display_filename(family))
            item.setToolTip(f"{family.id}\n{', '.join(family.tags)}")
            item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + LABEL_EXTRA_HEIGHT))
            self.addItem(item)
        self.blockSignals(False)  # noqa: FBT003
        if self._emit_family_selection:
            self.family_selected.emit(None)

    def set_grid_entries(
        self,
        entries: list[GridEntry],
        *,
        pixmaps_by_path: dict[str, QPixmap],
        placeholder: QPixmap,
    ) -> None:
        """Rebuild the grid from variant-view entries and path→pixmap map."""
        self.blockSignals(True)  # noqa: FBT003
        self.clear()
        for entry in entries:
            key = str(entry.svg_path)
            pixmap = pixmaps_by_path.get(key) or placeholder
            title = entry.family.title
            if entry.is_fallback:
                title = f"{entry.family.title} (no match)"
            item = QListWidgetItem(QIcon(pixmap), title)
            item.setData(Qt.ItemDataRole.UserRole, entry.family)
            item.setData(ROLE_SVG_PATH, key)
            item.setData(ROLE_SUBTITLE, family_display_filename(entry.family, entry.svg_path))
            tip = f"{entry.family.id}\n{entry.svg_path.name}"
            if entry.is_fallback:
                tip = f"{tip}\nFallback: family has no selected variant kind"
            item.setToolTip(tip)
            item.setSizeHint(QSize(self._icon_size + 16, self._icon_size + LABEL_EXTRA_HEIGHT))
            self.addItem(item)
        self.blockSignals(False)  # noqa: FBT003
        if self._emit_family_selection:
            self.family_selected.emit(None)

    def startDrag(self, supported_actions: Qt.DropAction) -> None:  # noqa: ARG002, N802
        """Start an OS file drag for the selected SVG path."""
        item = self.currentItem()
        if item is None:
            return
        svg_path = item.data(ROLE_SVG_PATH)
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

    def _grid_size_for(self, icon_size: int) -> QSize:
        label_h = LABEL_EXTRA_HEIGHT if self._dual_line_labels else 48
        return QSize(icon_size + 24, icon_size + label_h)

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        family = item.data(Qt.ItemDataRole.UserRole)
        path = item.data(ROLE_SVG_PATH)
        if family is None or not isinstance(path, str) or not path:
            return
        self.setCurrentItem(item)

        menu = QMenu(self)
        reveal_action = menu.addAction("📂 Reveal in File Explorer")
        details_action = menu.addAction("ℹ️ Icon details")  # noqa: RUF001
        copy_action = menu.addAction("📋 Copy")
        copy_path_action = menu.addAction("📋 Copy path")
        open_note_action = menu.addAction("📝 Open note in editor")
        set_category_action = menu.addAction("🏷️ Set as category icon")
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
        elif chosen is copy_path_action:
            self.copy_path_requested.emit(path)
        elif chosen is open_note_action:
            self.open_note_requested.emit(family)
        elif chosen is set_category_action:
            self.set_category_icon_requested.emit(family)
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


class IconLabelDelegate(QStyledItemDelegate):
    """Draw title plus a smaller filename under icon-mode items."""

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint icon decoration and two-line label."""
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        title = opt.text
        subtitle = index.data(ROLE_SUBTITLE)
        subtitle_text = subtitle if isinstance(subtitle, str) else ""
        opt.text = ""

        widget = opt.widget
        style = widget.style() if widget is not None else None
        if style is not None:
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, widget)

        text_rect = (
            style.subElementRect(QStyle.SubElement.SE_ItemViewItemText, opt, widget) if style is not None else opt.rect
        )
        if not text_rect.isValid():
            text_rect = QRect(
                opt.rect.left(),
                opt.rect.bottom() - LABEL_EXTRA_HEIGHT,
                opt.rect.width(),
                LABEL_EXTRA_HEIGHT,
            )

        painter.save()
        if opt.state & QStyle.StateFlag.State_Selected:
            painter.setPen(opt.palette.color(opt.palette.ColorRole.HighlightedText))
        else:
            painter.setPen(opt.palette.color(opt.palette.ColorRole.Text))

        title_font = QFont(opt.font)
        subtitle_font = QFont(opt.font)
        subtitle_font.setPointSizeF(max(8.0, title_font.pointSizeF() * 0.85))
        subtitle_font.setBold(False)

        painter.setFont(title_font)
        title_height = painter.fontMetrics().height()
        title_rect = QRect(text_rect.left(), text_rect.top(), text_rect.width(), title_height)
        painter.drawText(
            title_rect,
            int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
            title,
        )

        if subtitle_text:
            if opt.state & QStyle.StateFlag.State_Selected:
                muted = opt.palette.color(opt.palette.ColorRole.HighlightedText)
                muted.setAlpha(200)
            else:
                muted = opt.palette.color(opt.palette.ColorRole.PlaceholderText)
                if not muted.isValid() or muted.alpha() == 0:
                    muted = QColor(opt.palette.color(opt.palette.ColorRole.Text))
                    muted.setAlpha(160)
            painter.setPen(muted)
            painter.setFont(subtitle_font)
            subtitle_rect = QRect(
                text_rect.left(),
                title_rect.bottom() + 1,
                text_rect.width(),
                text_rect.bottom() - title_rect.bottom(),
            )
            painter.drawText(
                subtitle_rect,
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap),
                subtitle_text,
            )
        painter.restore()

    def sizeHint(  # noqa: N802
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        """Keep room for icon plus two text lines."""
        base = super().sizeHint(option, index)
        icon_h = option.decorationSize.height() if option.decorationSize.isValid() else DEFAULT_THUMB_SIZE
        width = max(base.width(), icon_h + 16)
        return QSize(width, icon_h + LABEL_EXTRA_HEIGHT)


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
            item.setData(ROLE_SVG_PATH, str(path))
            item.setToolTip(str(path))
            self.list.addItem(item)

    @staticmethod
    def _preview(path: Path, size: int) -> QPixmap:
        image = render_icon_to_image(path, size)
        if image is None:
            return placeholder_pixmap(size)
        return QPixmap.fromImage(image)


def family_display_filename(family: IconFamily, svg_path: Path | None = None) -> str:
    """Return the filename shown under the family title in the main grid."""
    if svg_path is not None and svg_path.name.casefold() != "featured-image.svg":
        return svg_path.name
    if family.variants:
        return Path(family.variants[0].file).name
    return f"{family.id}.svg"
