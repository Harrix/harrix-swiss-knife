"""Modal dialog for picking an exercise from AVIF previews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, QRect, QSize, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QCloseEvent, QIcon

    from harrix_swiss_knife.apps.common.avif_manager import AvifManager


class ExerciseSelectionDialog(QDialog):
    """Modal dialog for selecting an exercise via AVIF previews."""

    def __init__(
        self,
        parent: QWidget | None,
        *,
        exercises: list[str],
        icon_provider: Callable[[str], QIcon | None],
        preview_size: QSize,
        current_selection: str | None,
        avif_manager: AvifManager | None = None,
    ) -> None:
        """Initialize the ExerciseSelectionDialog.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `exercises` (`list[str]`): List of exercise names to display.
        - `icon_provider` (`Callable[[str], QIcon | None]`): Returns an icon for a given exercise name.
        - `preview_size` (`QSize`): Size for icon previews.
        - `current_selection` (`str | None`): Currently selected exercise, if any.
        - `avif_manager` (`AvifManager | None`): AVIF manager for loading animations. Defaults to `None`.

        """
        super().__init__(parent)
        self.setWindowTitle("Select Exercise")
        self.setModal(True)
        self.selected_exercise: str | None = current_selection
        self._icon_provider = icon_provider
        self._avif_manager = avif_manager
        self._preview_size = preview_size
        self._item_border_px = 2
        self._item_padding_top_px = 10
        self._item_padding_side_px = 8
        self._item_padding_bottom_px = 6
        self._text_area_height = 36
        self._current_hovered_item: QListWidgetItem | None = None
        self._animation_label: QLabel | None = None
        horizontal_inset = 2 * (self._item_padding_side_px + self._item_border_px)
        vertical_inset = self._item_padding_top_px + self._item_padding_bottom_px + 2 * self._item_border_px
        self._grid_size = QSize(
            preview_size.width() + horizontal_inset,
            preview_size.height() + self._text_area_height + vertical_inset,
        )

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setMovement(QListWidget.Movement.Static)
        self.list_widget.setSpacing(16)
        self.list_widget.setIconSize(preview_size)
        self.list_widget.setGridSize(self._grid_size)
        self.list_widget.setWordWrap(True)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setMouseTracking(True)

        list_palette = self.list_widget.palette()
        text_color = list_palette.color(QPalette.ColorRole.Text)
        text_color_name = text_color.name()
        list_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 0, 0, 0))
        list_palette.setColor(QPalette.ColorRole.HighlightedText, text_color)
        self.list_widget.setPalette(list_palette)

        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                outline: none;
            }}
            QListWidget::item {{
                padding: {self._item_padding_top_px}px {self._item_padding_side_px}px
                    {self._item_padding_bottom_px}px {self._item_padding_side_px}px;
                border: {self._item_border_px}px solid transparent;
                border-radius: 4px;
                background: transparent;
                color: {text_color_name};
                selection-background-color: transparent;
                selection-color: {text_color_name};
            }}
            QListWidget::item:hover {{
                border-color: #0078d4;
                background: transparent;
                color: {text_color_name};
            }}
            QListWidget::item:selected,
            QListWidget::item:selected:hover,
            QListWidget::item:selected:focus,
            QListWidget::item:selected:active {{
                border-color: #4CAF50;
                background: transparent;
                color: {text_color_name};
                selection-background-color: transparent;
                selection-color: {text_color_name};
            }}
            """
        )
        layout.addWidget(self.list_widget)

        for exercise in exercises:
            item = QListWidgetItem(exercise, self.list_widget)
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            item.setSizeHint(self._grid_size)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)

            icon = self._icon_provider(exercise)
            if icon is not None and not icon.isNull():
                item.setIcon(icon)

            if current_selection and exercise == current_selection:
                self.list_widget.setCurrentItem(item)
                item.setSelected(True)

        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.itemEntered.connect(self._on_item_entered)
        self.list_widget.installEventFilter(self)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Handle dialog close event - stop animation."""
        self._stop_animation()
        super().closeEvent(event)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle mouse leave on the list so hover previews stop."""
        if obj == self.list_widget and event.type() == QEvent.Type.Leave:
            self._stop_animation()
            return False

        return super().eventFilter(obj, event)

    def reject(self) -> None:
        """Handle dialog rejection - stop animation."""
        self._stop_animation()
        super().reject()

    def _icon_rect_for_item(self, item: QListWidgetItem) -> QRect:
        """Return the icon preview rectangle centered at the top of the list item."""
        item_rect = self.list_widget.visualItemRect(item)
        icon_w = self._preview_size.width()
        icon_h = self._preview_size.height()
        x = item_rect.x() + max(0, (item_rect.width() - icon_w) // 2)
        y = item_rect.y() + self._item_padding_top_px + self._item_border_px
        return QRect(x, y, icon_w, icon_h)

    def _on_accept(self) -> None:
        self._stop_animation()
        item = self.list_widget.currentItem()
        if item is None:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                item = selected_items[0]
                self.list_widget.setCurrentItem(item)
            elif self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(0)
                item = self.list_widget.currentItem()
        self._update_selected_from_item(item)

        if self.selected_exercise:
            self.accept()
        else:
            self.reject()

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self.list_widget.setCurrentItem(item)
        self._update_selected_from_item(item)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self._stop_animation()
        self.list_widget.setCurrentItem(item)
        self._update_selected_from_item(item)
        self.accept()

    def _on_item_entered(self, item: QListWidgetItem) -> None:
        """Start AVIF animation when the pointer enters a row."""
        if not self._avif_manager:
            return

        exercise_name = item.data(Qt.ItemDataRole.UserRole)
        if not exercise_name:
            return

        if self._current_hovered_item is not None and self._current_hovered_item != item:
            self._stop_animation()

        self._current_hovered_item = item

        icon_rect = self._icon_rect_for_item(item)

        if self._animation_label is None:
            self._animation_label = QLabel(self.list_widget)
            self._animation_label.setScaledContents(False)
            self._animation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._animation_label.setStyleSheet("background-color: transparent;")
            self._animation_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._animation_label.setGeometry(icon_rect)
        self._avif_manager.load_exercise_avif(exercise_name, self._animation_label, AvifLabelKey.DIALOG_PREVIEW)

        self._animation_label.show()

    def _on_selection_changed(self) -> None:
        self._update_selected_from_item(self.list_widget.currentItem())

    def _stop_animation(self) -> None:
        """Stop AVIF animation and hide the overlay label."""
        if self._animation_label and self._animation_label.isVisible():
            if self._avif_manager:
                data = self._avif_manager.avif_data.get(AvifLabelKey.DIALOG_PREVIEW)
                if data:
                    timer = data.get("timer")
                    if timer is not None:
                        timer.stop()
                        data["timer"] = None
                    data["frames"] = []
                    data["current_frame"] = 0

            self._animation_label.hide()
            self._current_hovered_item = None

    def _update_selected_from_item(self, item: QListWidgetItem | None) -> None:
        if item is None:
            self.selected_exercise = None
            return
        exercise = item.data(Qt.ItemDataRole.UserRole)
        self.selected_exercise = exercise if exercise else item.text()
