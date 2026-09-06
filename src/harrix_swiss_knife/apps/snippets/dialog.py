"""Frameless Quick paste overlay with phrases, emoji, symbols, and colors."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

import harrix_pylib as h
from PySide6.QtCore import QEvent, QObject, QPoint, QSize, Qt
from PySide6.QtGui import QFont, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import isValid

from harrix_swiss_knife.actions.common.dialog_geometry import center_widget_on_available_screen
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.db_init import init_tracker_database
from harrix_swiss_knife.apps.common.dialogs.text_input_dialog import TextInputDialog
from harrix_swiss_knife.apps.snippets import database_manager
from harrix_swiss_knife.apps.snippets.constants import (
    SORT_ADDED,
    SORT_ALPHA,
    SORT_USED,
    ZONE_COLOR,
    ZONE_EMOJI,
    ZONE_PHRASE,
    ZONE_SYMBOL,
    ZONES,
    SortMode,
    ZoneName,
)
from harrix_swiss_knife.apps.snippets.emoji_ai import request_snippets_emoji_suggestions
from harrix_swiss_knife.apps.snippets.item_edit_dialog import ItemEditDialog
from harrix_swiss_knife.apps.snippets.parse import filter_new_snippet_items, parse_bulk_lines, serialize_items
from harrix_swiss_knife.apps.snippets.paste import clone_clipboard_mime, paste_text_then_restore_clipboard
from harrix_swiss_knife.apps.snippets.seed import ensure_seed_emojis
from harrix_swiss_knife.apps.snippets.sort import sort_items
from harrix_swiss_knife.apps.snippets.zone_panel import ZonePanel, add_sort_menu_actions
from harrix_swiss_knife.integrations.bothub import BothubRequestState
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_app_font import apply_mono_font
from harrix_swiss_knife.qt_command_section import apply_opaque_white, grow_qfont
from harrix_swiss_knife.qt_emoji_icon import add_emoji_action, create_emoji_icon
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags, try_handle_frameless_resize_native_event
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from harrix_swiss_knife.apps.snippets.database_manager import SnippetItem

_EMOJI_SPLIT_RATIO = 4
_EMOJI_SYMBOL_SPLIT_UNIT = 140
_OVERLAY_MIN_SIZE = QSize(1100, 640)
_OVERLAY_DEFAULT_SIZE = QSize(1280, 760)
_SYMBOL_SPLIT_RATIO = 1
_WINDOW_FLAGS = frameless_stay_on_top_flags()
_DIALOG_BORDER_STYLE = "#snippetsDialog { background-color: #ffffff; border: 1px solid #c0c0c0;}"
_DUPLICATE_PREVIEW_LIMIT = 8
_INPUT_FONT_DELTA = 4
_INPUT_STYLE = "QLineEdit { padding: 10px 14px; }"
_ZONE_TITLES = {
    ZONE_PHRASE: "Phrases",
    ZONE_EMOJI: "Emoji",
    ZONE_SYMBOL: "Symbols",
    ZONE_COLOR: "Colors",
}
_ZONE_ADD_TITLES = {
    ZONE_PHRASE: "Add phrase",
    ZONE_EMOJI: "Add emoji",
    ZONE_SYMBOL: "Add symbol",
    ZONE_COLOR: "Add color",
}
_ZONE_KIND = {
    ZONE_PHRASE: "phrase",
    ZONE_EMOJI: "emoji",
    ZONE_SYMBOL: "symbol",
    ZONE_COLOR: "color",
}


class SnippetsDialog(QDialog):
    """Resizable always-on-top window for quick text paste."""

    _instance: ClassVar[SnippetsDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the overlay and open the snippets database."""
        super().__init__(parent)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._dragging = False
        self._drag_position = QPoint()
        self._saved_clipboard = None
        self.db_manager: database_manager.DatabaseManager | None = None
        self._app_config: dict[str, Any] = {}
        self._bothub_state = BothubRequestState()
        self._ai_request_in_progress = False

        apply_opaque_white(self)
        self.setObjectName("snippetsDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_DIALOG_BORDER_STYLE)

        self._active_zone: ZoneName = ZONE_PHRASE
        self._zone_input_text = dict.fromkeys(ZONES, "")
        self._syncing_input = False
        self._input = QLineEdit(self)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)
        self._build_header()
        self._build_shared_input()
        self._build_body()
        self._build_resize_row()
        self.setMouseTracking(True)
        self._init_database()
        self.reload_all()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Hide the overlay instead of destroying it."""
        event.ignore()
        self.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Start window drag from the title, and navigate from the shared input."""
        if watched is self._input:
            if event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent):
                if event.key() in {Qt.Key.Key_Down, Qt.Key.Key_Up}:
                    if self._active_panel().move_visible(1 if event.key() == Qt.Key.Key_Down else -1):
                        self._show_current_value_in_input()
                    return True
                if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                    self._active_panel().activate_current_or_first()
                    return True
            return super().eventFilter(watched, event)
        return self._handle_title_drag(watched, event)

    def focusNextPrevChild(self, next: bool) -> bool:  # noqa: A002, FBT001, N802
        """Cycle Tab between phrases, emoji, symbols, and colors in the shared input."""
        index = ZONES.index(self._active_zone)
        index = (index + (1 if next else -1)) % len(ZONES)
        self._activate_zone(ZONES[index])
        return True

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Move the overlay while dragging from the background."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging from empty chrome."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stop dragging the overlay."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Allow edge resize for this frameless window on Windows."""
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def present(self) -> None:
        """Show the overlay and focus the shared input on phrases."""
        self.reload_all()
        self._zone_input_text = dict.fromkeys(ZONES, "")
        for panel in self._panels.values():
            panel.reset_keyboard_session()
            panel.clear_filter()
        self._emoji.clear_ai_candidates()
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        self._activate_zone(ZONE_PHRASE, select_item=False)
        self._update_ai_pick_button()

    def reload_all(self) -> None:
        """Reload every zone from the database."""
        if self.db_manager is None:
            return
        for zone, panel in self._panels.items():
            self._reload_zone(zone, panel)

    @classmethod
    def toggle(cls, parent: QWidget | None = None) -> None:
        """Show or hide the singleton overlay."""
        if cls._instance is not None and isValid(cls._instance):
            if cls._instance.isVisible():
                cls._instance.hide()
                return
            cls._instance.present()
            return
        dialog = cls(parent)
        cls._instance = dialog
        dialog.present()

    def _activate_zone(self, zone: ZoneName, *, select_item: bool = True) -> None:
        """Switch the shared input to `zone` and show that zone's current value."""
        previous = self._active_zone
        if previous != zone:
            self._zone_input_text[previous] = ""
            self._panels[previous].clear_filter()
        self._active_zone = zone
        self._input.setPlaceholderText(_ZONE_TITLES[zone])
        panel = self._panels[zone]
        if select_item:
            panel.prepare_keyboard_focus()
        stored = self._zone_input_text[zone]
        if stored:
            self._set_input_text(stored)
            self._input.setCursorPosition(len(stored))
        elif select_item:
            self._show_current_value_in_input()
        else:
            self._set_input_text("")
        self._input.setFocus()

    def _active_panel(self) -> ZonePanel:
        """Return the zone panel that the shared input currently filters."""
        return self._panels[self._active_zone]

    def _add_ai_emoji(self, emoji: str) -> None:
        if self.db_manager is None or not emoji.strip():
            return
        if self.db_manager.has_item_value(ZONE_EMOJI, emoji):
            self._refresh_ai_candidates()
            return
        self.db_manager.add_item(ZONE_EMOJI, emoji, "")
        self._reload_zone(ZONE_EMOJI, self._emoji)
        self._refresh_ai_candidates()

    def _add_item(self, zone: str) -> None:
        dialog = ItemEditDialog(self, title=f"Add {_ZONE_TITLES[zone].lower()}", zone=zone)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        value, hint = dialog.values()
        if not value or self.db_manager is None:
            return
        if self.db_manager.has_item_value(zone, value):
            self._warn_duplicate(zone, value)
            return
        self.db_manager.add_item(zone, value, hint)
        self._reload_zone(zone, self._panels[zone])

    def _add_many(self, zone: str) -> None:
        dialog = TextInputDialog(
            self,
            title=f"Add many {_ZONE_TITLES[zone].lower()}",
            description="One item per line. Symbols and colors use `value | hint`.",
            placeholder="Item",
            min_height=320,
        )
        apply_mono_font(dialog.text_edit)
        if dialog.exec() != QDialog.DialogCode.Accepted or self.db_manager is None:
            return
        items = parse_bulk_lines(dialog.get_text() or "", zone)
        if not items:
            return
        existing = [item.value for item in self.db_manager.list_items(zone)]
        new_items, duplicates = filter_new_snippet_items(zone, items, existing)
        if duplicates:
            self._warn_duplicates(zone, duplicates)
        if not new_items:
            return
        self.db_manager.add_items(zone, new_items)
        self._reload_zone(zone, self._panels[zone])

    def _build_body(self) -> None:
        self._phrases = ZonePanel(self, zone=ZONE_PHRASE, title=_ZONE_TITLES[ZONE_PHRASE])
        self._emoji = ZonePanel(self, zone=ZONE_EMOJI, title=_ZONE_TITLES[ZONE_EMOJI])
        self._symbols = ZonePanel(self, zone=ZONE_SYMBOL, title=_ZONE_TITLES[ZONE_SYMBOL])
        self._colors = ZonePanel(self, zone=ZONE_COLOR, title=_ZONE_TITLES[ZONE_COLOR])
        self._panels = {
            ZONE_PHRASE: self._phrases,
            ZONE_EMOJI: self._emoji,
            ZONE_SYMBOL: self._symbols,
            ZONE_COLOR: self._colors,
        }
        for panel in self._panels.values():
            panel.item_activated.connect(self._paste_item)
            panel.add_requested.connect(lambda zone_panel=panel: self._add_item(zone_panel.zone))
            panel.add_many_requested.connect(lambda zone_panel=panel: self._add_many(zone_panel.zone))
            panel.edit_requested.connect(self._edit_item)
            panel.edit_all_requested.connect(lambda zone_panel=panel: self._edit_all(zone_panel.zone))
            panel.delete_requested.connect(self._delete_item)
            panel.sort_requested.connect(lambda mode, zone_panel=panel: self._sort_zone(zone_panel.zone, mode))
        self._emoji.ai_pick_requested.connect(self._suggest_emoji_with_ai)
        self._emoji.ai_add_requested.connect(self._add_ai_emoji)

        right_split = QSplitter(Qt.Orientation.Vertical, self)
        right_split.addWidget(self._emoji)
        right_split.addWidget(self._symbols)
        right_split.setStretchFactor(0, _EMOJI_SPLIT_RATIO)
        right_split.setStretchFactor(1, _SYMBOL_SPLIT_RATIO)
        right_split.setSizes(
            [_EMOJI_SPLIT_RATIO * _EMOJI_SYMBOL_SPLIT_UNIT, _SYMBOL_SPLIT_RATIO * _EMOJI_SYMBOL_SPLIT_UNIT],
        )

        columns = QSplitter(Qt.Orientation.Horizontal, self)
        columns.addWidget(self._phrases)
        columns.addWidget(right_split)
        columns.addWidget(self._colors)
        columns.setStretchFactor(0, 2)
        columns.setStretchFactor(1, 2)
        columns.setStretchFactor(2, 2)
        self._layout.addWidget(columns, stretch=1)

    def _build_header(self) -> None:
        menu_button = QToolButton(self)
        menu_button.setIcon(create_emoji_icon("☰", 18))
        menu_button.setIconSize(QSize(18, 18))
        menu_button.setFixedSize(28, 28)
        menu_button.setAutoRaise(True)
        menu_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        menu_button.setToolTip("Menu")
        menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        header_menu = QMenu(menu_button)
        header_menu.aboutToShow.connect(self._fill_header_menu)
        menu_button.setMenu(header_menu)
        self._menu_button = menu_button
        self._header_menu = header_menu

        title = QLabel("Quick paste")
        title_font = QFont(title.font())
        grow_qfont(title_font)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)
        title.installEventFilter(self)

        close_button = QPushButton("X")
        close_button.setFixedSize(28, 28)
        close_button.setFlat(True)
        close_button.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        close_button.setToolTip("Close")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide)
        self._close_button = close_button

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)
        header_spacer.installEventFilter(self)

        header = QHBoxLayout()
        header.addWidget(menu_button)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(close_button)
        self._layout.addLayout(header)

    def _build_resize_row(self) -> None:
        resize_row = QHBoxLayout()
        resize_row.addStretch()
        resize_row.addWidget(QSizeGrip(self), alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addLayout(resize_row)

    def _build_shared_input(self) -> None:
        self._input.setPlaceholderText(_ZONE_TITLES[ZONE_PHRASE])
        self._input.textChanged.connect(self._on_input_text_changed)
        self._input.installEventFilter(self)
        apply_mono_font(self._input)
        font = self._input.font()
        grow_qfont(font, delta=_INPUT_FONT_DELTA)
        self._input.setFont(font)
        self._input.setStyleSheet(_INPUT_STYLE)
        self._input.setMinimumHeight(self._input.fontMetrics().height() + 22)
        self._layout.addWidget(self._input)

    def _center_on_screen(self) -> None:
        center_widget_on_available_screen(self)

    def _delete_item(self, snippet: SnippetItem) -> None:
        reply = message_box.question(
            self,
            "Confirm Delete",
            f"Delete '{snippet.value}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes or self.db_manager is None:
            return
        self.db_manager.delete_item(snippet.item_id)
        self._reload_zone(snippet.zone, self._panels[snippet.zone])

    def _edit_all(self, zone: str) -> None:
        if self.db_manager is None:
            return
        items = self.db_manager.list_items(zone)
        dialog = TextInputDialog(
            self,
            title=f"Edit {_ZONE_TITLES[zone].lower()}",
            description="One item per line. Symbols and colors use `value | hint`.",
            initial_text=serialize_items(items, zone),
            min_height=400,
        )
        apply_mono_font(dialog.text_edit)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parsed = parse_bulk_lines(dialog.get_text() or "", zone)
        unique_items, duplicates = filter_new_snippet_items(zone, parsed, [])
        if duplicates:
            self._warn_duplicates(zone, duplicates)
        self.db_manager.replace_zone_items(zone, unique_items)
        self._reload_zone(zone, self._panels[zone])

    def _edit_item(self, snippet: SnippetItem) -> None:
        dialog = ItemEditDialog(
            self,
            title=f"Edit {_ZONE_TITLES[snippet.zone].lower()}",
            zone=snippet.zone,
            initial_value=snippet.value,
            initial_hint=snippet.hint,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted or self.db_manager is None:
            return
        value, hint = dialog.values()
        if not value:
            return
        if self.db_manager.has_item_value(snippet.zone, value, exclude_id=snippet.item_id):
            self._warn_duplicate(snippet.zone, value)
            return
        self.db_manager.update_item(snippet.item_id, value, hint)
        self._reload_zone(snippet.zone, self._panels[snippet.zone])

    def _end_drag(self) -> None:
        self._dragging = False

    def _fill_header_menu(self) -> None:
        menu = self._header_menu
        menu.clear()
        for zone, title in _ZONE_ADD_TITLES.items():
            action = add_emoji_action(menu, title, "➕")  # noqa: RUF001
            action.triggered.connect(lambda _checked=False, chosen=zone: self._add_item(chosen))
        menu.addSeparator()
        mode, descending = self._shared_zone_sort()
        add_sort_menu_actions(menu, mode=mode, descending=descending, on_sort=self._sort_all_zones)

    def _handle_title_drag(self, watched: QObject, event: QEvent) -> bool:
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._start_drag(event.globalPosition().toPoint())
            return True
        if (
            event.type() == QEvent.Type.MouseMove
            and isinstance(event, QMouseEvent)
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._move_drag(event.globalPosition().toPoint())
            return True
        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._end_drag()
            return True
        return super().eventFilter(watched, event)

    def _init_database(self) -> None:
        self._app_config = h.dev.config_load(get_config_path_str())
        raw = str(self._app_config.get("sqlite_snippets") or "").strip()
        configured = Path(raw) if raw else Path("snippets.db")
        self.db_manager = init_tracker_database(
            self,
            configured,
            "snippets",
            Path(__file__).parent / "recover.sql",
            database_manager.DatabaseManager,
            has_required_tables=lambda dm: dm.table_exists("items"),
            missing_table_label="items table",
        )
        if self.db_manager is not None:
            ensure_seed_emojis(self.db_manager)

    def _mark_used(self, item_id: int) -> None:
        if self.db_manager is not None:
            self.db_manager.mark_used(item_id)

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _on_ai_emoji_finished(self) -> None:
        self._ai_request_in_progress = False
        self._update_ai_pick_button()

    def _on_input_text_changed(self, text: str) -> None:
        if self._syncing_input:
            return
        self._zone_input_text[self._active_zone] = text
        self._active_panel().set_filter_query(text)
        self._refresh_input_match()
        self._update_ai_pick_button()

    def _paste_item(self, snippet: SnippetItem) -> None:
        self._saved_clipboard = clone_clipboard_mime()
        self.hide()
        paste_text_then_restore_clipboard(
            snippet.value,
            self._saved_clipboard,
            on_finished=lambda: self._mark_used(snippet.item_id),
        )

    def _refresh_ai_candidates(self) -> None:
        existing = [item.value for item in self.db_manager.list_items(ZONE_EMOJI)] if self.db_manager else []
        self._emoji.refresh_ai_candidates(existing)

    def _refresh_input_match(self) -> None:
        text = self._input.text()
        for zone, panel in self._panels.items():
            panel.set_input_match(text if zone == self._active_zone else "")

    def _reload_zone(self, zone: str, panel: ZonePanel) -> None:
        if self.db_manager is None:
            return
        zone_sort = self.db_manager.get_zone_sort(zone)
        items = sort_items(self.db_manager.list_items(zone), zone_sort.mode, descending=zone_sort.descending)
        panel.set_items(items)
        panel.set_sort_state(zone_sort)

    def _set_input_text(self, text: str) -> None:
        self._syncing_input = True
        self._input.setText(text)
        self._syncing_input = False
        self._refresh_input_match()
        self._update_ai_pick_button()

    def _shared_zone_sort(self) -> tuple[str | None, bool]:
        if self.db_manager is None:
            return None, False
        sorts = [self.db_manager.get_zone_sort(zone) for zone in ZONES]
        first = sorts[0]
        if all(item.mode == first.mode and item.descending == first.descending for item in sorts):
            return first.mode, first.descending
        return None, False

    def _show_ai_emoji_candidates(self, emojis: list[str]) -> None:
        existing = [item.value for item in self.db_manager.list_items(ZONE_EMOJI)] if self.db_manager else []
        self._emoji.set_ai_candidates(emojis, existing_values=existing)

    def _show_current_value_in_input(self) -> None:
        snippet = self._active_panel().current_snippet()
        if snippet is None:
            return
        self._set_input_text(snippet.value)
        self._input.selectAll()

    def _sort_all_zones(self, mode: str) -> None:
        if self.db_manager is None:
            return
        current_mode, current_descending = self._shared_zone_sort()
        descending = not current_descending if current_mode == mode else False
        sort_mode: SortMode = mode if mode in {SORT_USED, SORT_ADDED, SORT_ALPHA} else SORT_ALPHA
        for zone, panel in self._panels.items():
            self.db_manager.set_zone_sort(zone, sort_mode, descending=descending)
            self._reload_zone(zone, panel)

    def _sort_zone(self, zone: str, mode: str) -> None:
        if self.db_manager is None:
            return
        current = self.db_manager.get_zone_sort(zone)
        descending = not current.descending if current.mode == mode else False
        sort_mode: SortMode = mode if mode in {SORT_USED, SORT_ADDED, SORT_ALPHA} else SORT_ALPHA
        self.db_manager.set_zone_sort(zone, sort_mode, descending=descending)
        self._reload_zone(zone, self._panels[zone])

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()

    def _suggest_emoji_with_ai(self) -> None:
        query = self._input.text().strip()
        if not query or self._ai_request_in_progress:
            return
        if self._active_zone != ZONE_EMOJI:
            self._activate_zone(ZONE_EMOJI, select_item=False)
            self._set_input_text(query)
            self._zone_input_text[ZONE_EMOJI] = query
            self._emoji.set_filter_query(query)
        self._ai_request_in_progress = True
        self._update_ai_pick_button()
        request_snippets_emoji_suggestions(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            query=query,
            on_emojis=self._show_ai_emoji_candidates,
            on_finished=self._on_ai_emoji_finished,
        )

    def _update_ai_pick_button(self) -> None:
        has_text = bool(self._input.text().strip())
        self._emoji.set_ai_pick_visible(visible=has_text)
        self._emoji.set_ai_pick_enabled(enabled=has_text and not self._ai_request_in_progress)

    def _warn_duplicate(self, zone: str, value: str) -> None:
        kind = _ZONE_KIND.get(zone, "item")
        message_box.warning(self, "Already exists", f"This {kind} already exists: {value}")

    def _warn_duplicates(self, zone: str, values: list[str]) -> None:
        kind = _ZONE_KIND.get(zone, "item")
        preview = ", ".join(values[:_DUPLICATE_PREVIEW_LIMIT])
        if len(values) > _DUPLICATE_PREVIEW_LIMIT:
            preview += ", …"
        plural = "s" if len(values) != 1 else ""
        message_box.warning(self, "Already exists", f"Skipped duplicate {kind}{plural}: {preview}")
