"""Shared dialog and row for choosing a Lucide icon by ID."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.lucide_icon_ai import request_lucide_icon_suggestions
from harrix_swiss_knife.fluent.tokens import ICON_SIZE
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.qt_lucide_icon import (
    LUCIDE_COLOR_DARK,
    apply_lucide_dialog_buttons,
    create_lucide_icon,
    install_line_edit_search_chrome,
    list_lucide_icon_names,
    lucide_svg_path,
    make_ai_lucide_push_button,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_SEARCH_DEBOUNCE_MS = 250
_GRID_ICON_SIZE = 28
_MAX_SEARCH_RESULTS = 400
_EMPTY_HINT = "Type to search all Lucide icons…"


class LucideChoiceRow(QWidget):
    """Preview button plus Choose that opens `LucidePickerDialog`."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        current_name: str = "",
        presets: Sequence[str] | None = None,
        allow_empty: bool = True,
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        suggest_query_provider: Callable[[], str] | None = None,
    ) -> None:
        """Create a compact Lucide chooser row."""
        super().__init__(parent)
        self._presets = tuple(presets) if presets is not None else ()
        self._allow_empty = allow_empty
        self._name = current_name.strip()
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._suggest_query_provider = suggest_query_provider

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._preview = QPushButton(self)
        self._preview.setFixedSize(44, 44)
        self._preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self._preview.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self._preview.setToolTip("Choose Lucide icon")
        self._preview.clicked.connect(self._choose)

        self._label = QLabel(self)
        self._label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        choose_button = QPushButton("Choose Lucide…")
        choose_button.clicked.connect(self._choose)

        layout.addWidget(self._preview)
        layout.addWidget(self._label, 1)
        layout.addWidget(choose_button)
        self._refresh_preview()

    def lucide_name(self) -> str:
        """Return the selected Lucide ID, possibly empty for auto-from-emoji."""
        return self._name

    def set_lucide_name(self, name: str) -> None:
        """Update the preview and stored Lucide ID."""
        self._name = name.strip()
        self._refresh_preview()

    def _choose(self) -> None:
        suggest_query = ""
        if self._suggest_query_provider is not None:
            suggest_query = self._suggest_query_provider().strip()
        dialog = LucidePickerDialog(
            self,
            current_name=self._name,
            presets=self._presets,
            allow_empty=self._allow_empty,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            suggest_query=suggest_query,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.set_lucide_name(dialog.selected_name())

    def _refresh_preview(self) -> None:
        if self._name and lucide_svg_path(self._name) is not None:
            self._preview.setIcon(create_lucide_icon(self._name, ICON_SIZE, color=LUCIDE_COLOR_DARK))
            self._label.setText(self._name)
            return
        self._preview.setIcon(QIcon())
        self._label.setText("Auto (from emoji)" if self._allow_empty else "")


class LucidePickerDialog(QDialog):
    """Searchable Lucide icon grid with optional preset strip when the query is empty."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        current_name: str = "",
        presets: Sequence[str] | None = None,
        allow_empty: bool = True,
        title: str = "Choose Lucide icon",
        app_config: dict[str, Any] | None = None,
        bothub_state: BothubRequestState | None = None,
        suggest_query: str = "",
    ) -> None:
        """Initialize the Lucide picker dialog."""
        super().__init__(parent)
        qt_modality.set_owner_window_modal(self)
        self.setWindowTitle(title)
        self.resize(560, 520)
        self._allow_empty = allow_empty
        self._presets = tuple(dict.fromkeys(name.strip() for name in (presets or ()) if name.strip()))
        self._ai_suggestions: tuple[str, ...] = ()
        self._all_names = list_lucide_icon_names()
        self._selected = current_name.strip()
        self._app_config = app_config or {}
        self._bothub_state = bothub_state or BothubRequestState()
        self._suggest_query = suggest_query.strip()
        self._ai_request_in_progress = False
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(_SEARCH_DEBOUNCE_MS)
        self._filter_timer.timeout.connect(self._rebuild_grid)

        root = QVBoxLayout(self)
        root.setSpacing(10)

        preview_row = QHBoxLayout()
        preview_row.addWidget(QLabel("Selected:"))
        self._preview = QLabel()
        self._preview.setFixedSize(48, 48)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_name = QLabel()
        self._preview_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        preview_row.addWidget(self._preview)
        preview_row.addWidget(self._preview_name, 1)
        if allow_empty:
            clear_button = QPushButton("Clear (auto)")
            clear_button.setToolTip("Use emoji→Lucide mapping instead of a fixed Lucide id")
            clear_button.clicked.connect(lambda: self._select_name(""))
            preview_row.addWidget(clear_button)
        root.addLayout(preview_row)

        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search Lucide id…")
        install_line_edit_search_chrome(self._search, clear_tooltip="Clear search")
        self._search.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self._search, 1)
        self._ai_button = make_ai_lucide_push_button("")
        self._ai_button.setToolTip("Suggest Lucide icons with AI")
        self._ai_button.setFixedWidth(36)
        self._ai_button.clicked.connect(self._suggest_with_ai)
        search_row.addWidget(self._ai_button)
        root.addLayout(search_row)

        self._hint = QLabel(_EMPTY_HINT)
        root.addWidget(self._hint)

        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setWrapping(True)
        self._list.setUniformItemSizes(True)
        self._list.setIconSize(QSize(_GRID_ICON_SIZE, _GRID_ICON_SIZE))
        self._list.setGridSize(QSize(88, 72))
        self._list.setWordWrap(True)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        root.addWidget(self._list, 1)

        id_row = QHBoxLayout()
        id_row.addWidget(QLabel("Or Lucide id:"))
        self._id_edit = QLineEdit(self._selected)
        self._id_edit.setPlaceholderText("e.g. utensils")
        self._id_edit.textChanged.connect(self._on_id_changed)
        id_row.addWidget(self._id_edit, 1)
        root.addLayout(id_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._sync_preview()
        self._update_ai_button()
        self._rebuild_grid()

    def selected_name(self) -> str:
        """Return the chosen Lucide ID, possibly empty when auto-from-emoji is allowed."""
        return self._selected.strip()

    def _ai_query_text(self) -> str:
        search = self._search.text().strip()
        if search:
            return search
        return self._suggest_query

    def _apply_ai_suggestions(self, icons: list[str]) -> None:
        valid = tuple(dict.fromkeys(name for name in icons if lucide_svg_path(name) is not None))
        if not valid:
            message_box.warning(self, "Suggest Lucide", "AI returned no valid Lucide icons")
            return
        self._ai_suggestions = valid
        self._search.blockSignals(True)  # noqa: FBT003
        self._search.clear()
        self._search.blockSignals(False)  # noqa: FBT003
        self._select_name(valid[0])
        self._rebuild_grid()

    def _on_ai_finished(self) -> None:
        self._ai_request_in_progress = False
        self._update_ai_button()

    def _on_id_changed(self, text: str) -> None:
        value = text.strip()
        if value:
            self._select_name(value, sync_id=False)
            return
        if self._allow_empty:
            self._select_name("", sync_id=False)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(name, str):
            self._select_name(name)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self._on_item_clicked(item)
        if self._selected:
            self.accept()

    def _on_search_changed(self, _text: str) -> None:
        self._filter_timer.start()
        self._update_ai_button()

    def _rebuild_grid(self) -> None:
        query = self._search.text().strip().casefold()
        self._list.clear()
        if not query:
            if self._ai_suggestions:
                names = [name for name in self._ai_suggestions if lucide_svg_path(name) is not None]
                self._hint.setText("AI suggestions below. " + _EMPTY_HINT)
            else:
                names = [name for name in self._presets if lucide_svg_path(name) is not None]
                self._hint.setText("Presets below. " + _EMPTY_HINT)
        else:
            names = [name for name in self._all_names if query in name.casefold()]
            if len(names) > _MAX_SEARCH_RESULTS:
                names = names[:_MAX_SEARCH_RESULTS]
            self._hint.setText(
                f"Showing {len(names)} match(es)" + (" (truncated)" if len(names) == _MAX_SEARCH_RESULTS else "")
            )

        selected_row = -1
        for index, name in enumerate(names):
            item = QListWidgetItem(create_lucide_icon(name, _GRID_ICON_SIZE, color=LUCIDE_COLOR_DARK), name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(name)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            self._list.addItem(item)
            if name == self._selected:
                selected_row = index
        if selected_row >= 0:
            self._list.setCurrentRow(selected_row)

    def _select_name(self, name: str, *, sync_id: bool = True) -> None:
        self._selected = name.strip()
        self._sync_preview()
        if not sync_id:
            return
        self._id_edit.blockSignals(True)  # noqa: FBT003
        self._id_edit.setText(self._selected)
        self._id_edit.blockSignals(False)  # noqa: FBT003

    def _suggest_with_ai(self) -> None:
        query = self._ai_query_text()
        if not query or self._ai_request_in_progress:
            return
        self._ai_request_in_progress = True
        self._update_ai_button()
        request_lucide_icon_suggestions(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            query=query,
            on_icons=self._apply_ai_suggestions,
            on_finished=self._on_ai_finished,
        )

    def _sync_preview(self) -> None:
        if self._selected and lucide_svg_path(self._selected) is not None:
            self._preview.setPixmap(create_lucide_icon(self._selected, 28, color=LUCIDE_COLOR_DARK).pixmap(28, 28))
            self._preview_name.setText(self._selected)
            return
        self._preview.clear()
        self._preview_name.setText("Auto (from emoji)" if not self._selected else self._selected)

    def _update_ai_button(self) -> None:
        self._ai_button.setEnabled(bool(self._ai_query_text()) and not self._ai_request_in_progress)
