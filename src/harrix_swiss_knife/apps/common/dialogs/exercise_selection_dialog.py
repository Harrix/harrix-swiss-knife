"""Modal dialog for picking an exercise from AVIF previews."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QItemSelectionModel, QObject, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPalette, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey
from harrix_swiss_knife.keyboard_layout_search import text_matches_autocomplete
from harrix_swiss_knife.qt_emoji_icon import apply_emoji_dialog_buttons

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QCloseEvent, QEnterEvent, QMouseEvent, QShowEvent

    from harrix_swiss_knife.apps.common.avif_manager import AvifManager

_NAME_LOCAL_COLOR = QColor("#888888")
_NAME_LOCAL_FONT_SCALE = 0.85
_NAME_LOCAL_MIN_PIXEL_SIZE = 12
_NAME_LOCAL_MIN_POINT_SIZE = 7.0
_NAME_LOCAL_FALLBACK_POINT_SIZE = 9.0
# How long one deferred-preview batch may block the event loop.
_PREVIEW_DECODE_BUDGET_S = 0.02


class ExerciseSelectionDialog(QDialog):
    """Modal dialog for selecting an exercise via AVIF previews."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        pixmap_provider: Callable[[str], QPixmap | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
        name_locals: dict[str, str] | None = None,
        display_names: dict[str, str] | None = None,
        multi_select: bool = False,
    ) -> None:
        """Initialize the ExerciseSelectionDialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `exercises` (`list[str]`): List of exercise names to display.
        - `pixmap_provider` (`Callable[[str], QPixmap | None]`): Returns a still
          preview pixmap for a given exercise name.
        - `preview_size` (`QSize`): Size for icon previews.
        - `current_selection` (`str | None`): Currently selected exercise, if any.
        - `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.
        - `name_locals` (`dict[str, str] | None`): Optional English→local name map.
        - `display_names` (`dict[str, str] | None`): Optional English→display label map
          (for example a dumbbell icon prefix).
        - `multi_select` (`bool`): Allow Ctrl/Shift selection of several exercises.
          Defaults to `False`.

        """
        super().__init__(parent)
        self.setWindowTitle("Select Exercises" if multi_select else "Select Exercise")
        qt_modality.set_owner_window_modal(self)
        self._multi_select = multi_select
        self.selected_exercise: str | None = current_selection
        self.selected_exercises: list[str] = [current_selection] if current_selection else []
        self._pixmap_provider = pixmap_provider
        self._avif_manager = avif_manager
        self._name_locals = name_locals or {}
        self._display_names = display_names or {}
        self._preview_size = preview_size
        self._hovered_tile: _ExercisePreviewTile | None = None
        self._pending_preview_rows: list[int] = []
        self._preview_load_started = False
        has_any_local = any(self._name_locals.get(name, "").strip() for name in exercises)
        text_area_height = 54 if has_any_local else 36

        layout = QVBoxLayout(self)

        self.filter_edit = QLineEdit(self)
        self.filter_edit.setPlaceholderText(
            "Filter exercises…  Ctrl+click or Shift+click to select several" if multi_select else "Filter exercises…",
        )
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.textChanged.connect(self._filter_exercises)
        layout.addWidget(self.filter_edit)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
            if multi_select
            else QAbstractItemView.SelectionMode.SingleSelection,
        )
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setSpacing(16)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setMouseTracking(True)
        self.list_widget.setStyleSheet(
            """
            QListWidget {
                outline: none;
            }
            QListWidget::item {
                border: none;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
            QListWidget::item:selected {
                background: transparent;
            }
            QFrame#exercisePreviewTile {
                border: 2px solid transparent;
                border-radius: 4px;
                background: transparent;
            }
            QFrame#exercisePreviewTile:hover {
                border-color: #0078d4;
            }
            QFrame#exercisePreviewTile[selected="true"],
            QFrame#exercisePreviewTile[selected="true"]:hover {
                border-color: #4CAF50;
            }
            """
        )
        layout.addWidget(self.list_widget)

        self.list_widget.setUpdatesEnabled(False)
        try:
            for exercise in exercises:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, exercise)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

                name_local = self._name_locals.get(exercise, "").strip()
                tile = _ExercisePreviewTile(
                    exercise_name=exercise,
                    display_name=self._display_names.get(exercise, exercise),
                    name_local=name_local,
                    static_pixmap=None,
                    preview_size=preview_size,
                    text_area_height=text_area_height,
                    pixmap_pending=True,
                )
                item.setSizeHint(tile.sizeHint())
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, tile)
                self._pending_preview_rows.append(self.list_widget.count() - 1)

                tile.clicked.connect(lambda modifiers, row_item=item: self._on_tile_clicked(row_item, modifiers))
                tile.double_clicked.connect(lambda row_item=item: self._on_tile_double_clicked(row_item))
                tile.hover_entered.connect(lambda row_tile=tile: self._on_tile_hover_entered(row_tile))
                tile.hover_left.connect(lambda row_tile=tile: self._on_tile_hover_left(row_tile))

                if current_selection and exercise == current_selection:
                    self.list_widget.setCurrentItem(item)
                    item.setSelected(True)
                    tile.set_selected(selected=True)
        finally:
            self.list_widget.setUpdatesEnabled(True)

        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.verticalScrollBar().valueChanged.connect(self._on_list_scrolled)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        apply_emoji_dialog_buttons(button_box)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.filter_edit.setFocus()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle dialog close event — stop animation."""
        self._stop_animation()
        super().closeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle mouse leave on the list so hover previews stop."""
        if obj == self.list_widget and event.type() == QEvent.Type.Leave:
            self._stop_animation()
            return False

        return super().eventFilter(obj, event)

    def reject(self) -> None:
        """Handle dialog rejection — stop animation."""
        self._stop_animation()
        super().reject()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Start deferred preview loading after the dialog is visible."""
        super().showEvent(event)
        if not self._preview_load_started and self._pending_preview_rows:
            self._preview_load_started = True
            QTimer.singleShot(0, self._decode_next_preview_batch)

    def _decode_next_preview_batch(self) -> None:
        """Decode a time-budgeted batch of still previews, visible rows first."""
        if not self._pending_preview_rows:
            return

        self._prioritize_visible_preview_rows()
        deadline = time.perf_counter() + _PREVIEW_DECODE_BUDGET_S
        while self._pending_preview_rows:
            row = self._pending_preview_rows.pop(0)
            item = self.list_widget.item(row)
            tile = self._tile_for_item(item)
            if tile is None or not tile.pixmap_pending:
                continue
            exercise = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
            name = str(exercise) if exercise else tile.exercise_name
            pixmap = self._pixmap_provider(name)
            tile.set_static_pixmap(pixmap)
            if time.perf_counter() >= deadline:
                break

        if self._pending_preview_rows:
            QTimer.singleShot(0, self._decode_next_preview_batch)

    def _filter_exercises(self, text: str) -> None:
        """Show only tiles whose English or local name matches the query."""
        query = text.strip()
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is None:
                continue
            exercise = item.data(Qt.ItemDataRole.UserRole)
            name = str(exercise) if exercise else ""
            name_local = self._name_locals.get(name, "").strip()
            matches = (not query) or text_matches_autocomplete(name, query)
            if not matches and name_local:
                matches = text_matches_autocomplete(name_local, query)
            item.setHidden(not matches)
            if not matches:
                tile = self._tile_for_item(item)
                if tile is not None and self._hovered_tile is tile:
                    self._stop_animation()
        if self._pending_preview_rows:
            self._prioritize_visible_preview_rows()

    def _on_accept(self) -> None:
        self._stop_animation()
        self._sync_selected_exercises()
        if not self.selected_exercises:
            item = self.list_widget.currentItem()
            if item is None and self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
                item = self.list_widget.currentItem()
            if item is not None:
                item.setSelected(True)
                self._sync_selected_exercises()

        if self.selected_exercises:
            self.accept()
        else:
            self.reject()

    def _on_list_scrolled(self, *_args: object) -> None:
        """Prefer decoding previews that just scrolled into view."""
        if self._pending_preview_rows:
            self._prioritize_visible_preview_rows()

    def _on_selection_changed(self) -> None:
        selected_items = set(self.list_widget.selectedItems())
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            tile = self._tile_for_item(item)
            if tile is not None and item is not None:
                tile.set_selected(selected=item in selected_items)
        self._sync_selected_exercises()

    def _on_tile_clicked(self, item: QListWidgetItem, modifiers: object = Qt.KeyboardModifier.NoModifier) -> None:
        flags = Qt.KeyboardModifier(modifiers) if modifiers is not None else Qt.KeyboardModifier.NoModifier
        if not self._multi_select:
            self.list_widget.setCurrentItem(item)
            item.setSelected(True)
            self._sync_selected_exercises()
            return
        ctrl = bool(flags & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier))
        shift = bool(flags & Qt.KeyboardModifier.ShiftModifier)
        no_update = QItemSelectionModel.SelectionFlag.NoUpdate
        if shift:
            anchor = self.list_widget.currentItem()
            start = self.list_widget.row(anchor) if anchor is not None else self.list_widget.row(item)
            end = self.list_widget.row(item)
            lo, hi = min(start, end), max(start, end)
            if not ctrl:
                self.list_widget.clearSelection()
            for row in range(lo, hi + 1):
                row_item = self.list_widget.item(row)
                if row_item is not None and not row_item.isHidden():
                    row_item.setSelected(True)
            self.list_widget.setCurrentItem(item, no_update)
        elif ctrl:
            item.setSelected(not item.isSelected())
            self.list_widget.setCurrentItem(item, no_update)
        else:
            self.list_widget.clearSelection()
            item.setSelected(True)
            self.list_widget.setCurrentItem(item)
        self._sync_selected_exercises()

    def _on_tile_double_clicked(self, item: QListWidgetItem) -> None:
        self._stop_animation()
        if self._multi_select:
            item.setSelected(True)
            self.list_widget.setCurrentItem(item, QItemSelectionModel.SelectionFlag.NoUpdate)
        else:
            self.list_widget.setCurrentItem(item)
            item.setSelected(True)
        self._sync_selected_exercises()
        if self.selected_exercises:
            self.accept()

    def _on_tile_hover_entered(self, tile: _ExercisePreviewTile) -> None:
        """Play animation inside the same QLabel that shows the still preview."""
        if not self._avif_manager:
            return

        if tile.pixmap_pending:
            pixmap = self._pixmap_provider(tile.exercise_name)
            tile.set_static_pixmap(pixmap)
            row = self._row_for_tile(tile)
            if row is not None:
                self._pending_preview_rows = [pending for pending in self._pending_preview_rows if pending != row]

        if self._hovered_tile is not None and self._hovered_tile is not tile:
            self._stop_animation()

        self._hovered_tile = tile
        # Geometry is fixed on the label; no overlay positioning.
        self._avif_manager.load_exercise_avif(
            tile.exercise_name,
            tile.preview_label,
            AvifLabelKey.DIALOG_PREVIEW,
        )

    def _on_tile_hover_left(self, tile: _ExercisePreviewTile) -> None:
        if self._hovered_tile is tile:
            self._stop_animation()

    def _prioritize_visible_preview_rows(self) -> None:
        """Move rows intersecting the viewport to the front of the decode queue."""
        if not self._pending_preview_rows:
            return
        viewport = self.list_widget.viewport().rect()
        visible: list[int] = []
        hidden: list[int] = []
        for row in self._pending_preview_rows:
            item = self.list_widget.item(row)
            if item is None or item.isHidden():
                hidden.append(row)
                continue
            rect = self.list_widget.visualItemRect(item)
            if rect.intersects(viewport):
                visible.append(row)
            else:
                hidden.append(row)
        self._pending_preview_rows = visible + hidden

    def _row_for_tile(self, tile: _ExercisePreviewTile) -> int | None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if self._tile_for_item(item) is tile:
                return row
        return None

    def _stop_animation(self) -> None:
        """Stop AVIF animation and restore the still preview in the hovered tile."""
        tile = self._hovered_tile
        if self._avif_manager:
            data = self._avif_manager.avif_data.get(AvifLabelKey.DIALOG_PREVIEW)
            if data:
                timer = data.get("timer")
                if timer is not None:
                    timer.stop()
                    data["timer"] = None
                data["frames"] = []
                data["current_frame"] = 0
                data["exercise"] = None

        if tile is not None:
            tile.restore_static_pixmap()
        self._hovered_tile = None

    def _sync_selected_exercises(self) -> None:
        names: list[str] = []
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is None or not item.isSelected():
                continue
            exercise = item.data(Qt.ItemDataRole.UserRole)
            if exercise:
                names.append(str(exercise))
        self.selected_exercises = names
        self.selected_exercise = names[0] if names else None

    def _tile_for_item(self, item: QListWidgetItem | None) -> _ExercisePreviewTile | None:
        if item is None:
            return None
        widget = self.list_widget.itemWidget(item)
        return widget if isinstance(widget, _ExercisePreviewTile) else None


class _ExercisePreviewTile(QFrame):
    """One exercise cell: fixed preview slot plus name lines under it."""

    clicked = Signal(object)
    double_clicked = Signal()
    hover_entered = Signal()
    hover_left = Signal()

    def __init__(
        self,
        *,
        exercise_name: str,
        display_name: str | None = None,
        name_local: str,
        static_pixmap: QPixmap | None,
        preview_size: QSize,
        text_area_height: int,
        pixmap_pending: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """Build a tile with a fixed-size preview label shared by static and animated frames."""
        super().__init__(parent)
        self.exercise_name = exercise_name
        self._static_pixmap = static_pixmap
        self._selected = False
        self.pixmap_pending = pixmap_pending

        self.setObjectName("exercisePreviewTile")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 6)
        layout.setSpacing(4)

        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(preview_size)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white; border: none;")
        self.preview_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self.restore_static_pixmap()
        layout.addWidget(self.preview_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.name_label = QLabel(display_name or exercise_name, self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.name_label.setWordWrap(True)
        self.name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        layout.addWidget(self.name_label)

        self.local_label = QLabel(self)
        self.local_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.local_label.setWordWrap(True)
        self.local_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        local_font = QFont(self.local_label.font())
        pixel = local_font.pixelSize()
        if pixel > 0:
            local_font.setPixelSize(max(_NAME_LOCAL_MIN_PIXEL_SIZE, round(pixel * _NAME_LOCAL_FONT_SCALE)))
        else:
            base_size = local_font.pointSizeF()
            if base_size <= 0:
                base_size = float(local_font.pointSize())
            if base_size <= 0:
                base_size = _NAME_LOCAL_FALLBACK_POINT_SIZE
            local_font.setPointSizeF(max(_NAME_LOCAL_MIN_POINT_SIZE, base_size * _NAME_LOCAL_FONT_SCALE))
        self.local_label.setFont(local_font)
        palette = self.local_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, _NAME_LOCAL_COLOR)
        self.local_label.setPalette(palette)
        if name_local:
            self.local_label.setText(name_local)
        else:
            self.local_label.hide()
        layout.addWidget(self.local_label)

        # Keep vertical rhythm even when local name is missing.
        text_height = max(text_area_height, self.name_label.sizeHint().height())
        if name_local:
            text_height = max(text_height, self.name_label.sizeHint().height() + self.local_label.sizeHint().height())
        self.name_label.setMinimumHeight(self.name_label.sizeHint().height())
        if name_local:
            self.local_label.setMinimumHeight(self.local_label.sizeHint().height())
        layout.addStretch(1)
        self.setFixedSize(
            preview_size.width() + 16 + 4,
            preview_size.height() + text_height + 16 + 4,
        )
        self._apply_chrome()

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Notify dialog that the pointer entered this tile's preview."""
        self.hover_entered.emit()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Notify dialog that the pointer left this tile."""
        self.hover_left.emit()
        super().leaveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Accept exercise on double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select this exercise on click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(event.modifiers())
        super().mousePressEvent(event)

    def restore_static_pixmap(self) -> None:
        """Show the original still preview in the same label used for animation."""
        if self.pixmap_pending:
            self.preview_label.clear()
            return
        if self._static_pixmap is not None and not self._static_pixmap.isNull():
            self.preview_label.setPixmap(self._static_pixmap)
        else:
            self.preview_label.clear()
            self.preview_label.setText("No preview")

    def set_selected(self, *, selected: bool) -> None:
        """Update selection border without changing preview geometry."""
        if self._selected == selected:
            return
        self._selected = selected
        self._apply_chrome()

    def set_static_pixmap(self, pixmap: QPixmap | None) -> None:
        """Apply a still preview after deferred decode."""
        self.pixmap_pending = False
        self._static_pixmap = pixmap if pixmap is not None and not pixmap.isNull() else None
        self.restore_static_pixmap()

    def _apply_chrome(self) -> None:
        self.setProperty("selected", self._selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
