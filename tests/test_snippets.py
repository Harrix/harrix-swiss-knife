"""Tests for Quick paste snippets seed, sort, parse, and registration."""

# ruff: noqa: RUF001

from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtCore import QEvent, QRect, Qt
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QStyle, QStyleOptionViewItem, QToolButton

from harrix_swiss_knife.actions.apps.snippets import OnSnippets
from harrix_swiss_knife.actions.common.quick_launcher_registry import iter_menu_structure
from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase
from harrix_swiss_knife.apps.snippets.constants import (
    SORT_ADDED,
    SORT_ALPHA,
    SORT_USED,
    ZONE_COLOR,
    ZONE_EMOJI,
    ZONE_PHRASE,
    ZONE_SYMBOL,
)
from harrix_swiss_knife.apps.snippets.database_manager import DatabaseManager, SnippetItem
from harrix_swiss_knife.apps.snippets.dialog import SnippetsDialog
from harrix_swiss_knife.apps.snippets.parse import (
    display_text,
    hint_tooltip,
    item_matches_search,
    parse_bulk_lines,
    parse_value_hint_line,
)
from harrix_swiss_knife.apps.snippets.seed import (
    SEED_EMOJIS_BASE,
    SEED_PHRASES,
    build_recover_sql,
    ensure_seed_emojis,
    extract_phrase_emojis,
    seed_emojis,
)
from harrix_swiss_knife.apps.snippets.sort import dash_length_rank, sort_items
from harrix_swiss_knife.apps.snippets.zone_panel import (
    _LIST_SELECTION_STYLE,
    _SELECTION_BG,
    _SELECTION_OUTLINE,
    HighlightItemDelegate,
    IconItemDelegate,
    ZonePanel,
    chip_border_color,
    color_hex_label,
)
from harrix_swiss_knife.menu_structure import get_menu_structure
from harrix_swiss_knife.qt_app_font import MONO_FONT_FAMILY

_ROOT = Path(__file__).resolve().parents[1]
_RECOVER_SQL = _ROOT / "src" / "harrix_swiss_knife" / "apps" / "snippets" / "recover.sql"
_EXAMPLE_CONFIG = _ROOT / "config" / "config.example.json"


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def _item(
    item_id: int,
    value: str,
    *,
    created_at: str = "2026-01-01T00:00:00+00:00",
    last_used_at: str | None = None,
) -> SnippetItem:
    return SnippetItem(
        item_id=item_id,
        zone="phrase",
        value=value,
        hint="",
        created_at=created_at,
        last_used_at=last_used_at,
        sort_index=item_id,
    )


def test_extract_phrase_emojis_includes_commit_prefixes() -> None:
    emojis = extract_phrase_emojis(SEED_PHRASES)
    assert "➕" in emojis
    assert "🐞" in emojis
    assert "📜" in emojis


def test_seed_emojis_merges_phrase_extras_without_duplicates() -> None:
    merged = seed_emojis()
    assert merged.count("🔍") == 1
    assert merged.count("📚") == 1
    for extra in ("➕", "☕", "🚀", "✨", "📜", "🏃", "🍔", "🤖", "🧮", "👃"):
        assert extra in merged
    for base in SEED_EMOJIS_BASE:
        assert base in merged


def test_sort_items_used_puts_unused_last_alphabetically() -> None:
    items = [
        _item(1, "Beta", last_used_at="2026-08-20T10:00:00+00:00"),
        _item(2, "Alpha"),
        _item(3, "Gamma", last_used_at="2026-08-25T10:00:00+00:00"),
        _item(4, "Zed"),
    ]
    ordered = [item.value for item in sort_items(items, SORT_USED, descending=False)]
    assert ordered == ["Gamma", "Beta", "Alpha", "Zed"]
    reversed_used = [item.value for item in sort_items(items, SORT_USED, descending=True)]
    assert reversed_used[:2] == ["Beta", "Gamma"]
    assert reversed_used[2:] == ["Alpha", "Zed"]


def test_sort_items_added_and_alpha() -> None:
    items = [
        _item(1, "Beta", created_at="2026-01-02T00:00:00+00:00"),
        _item(2, "Alpha", created_at="2026-01-03T00:00:00+00:00"),
        _item(3, "Gamma", created_at="2026-01-01T00:00:00+00:00"),
    ]
    assert [item.value for item in sort_items(items, SORT_ADDED, descending=False)] == ["Alpha", "Beta", "Gamma"]
    assert [item.value for item in sort_items(items, SORT_ADDED, descending=True)] == ["Gamma", "Beta", "Alpha"]
    assert [item.value for item in sort_items(items, SORT_ALPHA, descending=False)] == ["Alpha", "Beta", "Gamma"]
    assert [item.value for item in sort_items(items, SORT_ALPHA, descending=True)] == ["Gamma", "Beta", "Alpha"]


def test_sort_items_pins_symbol_dashes_first_by_length() -> None:
    items = [
        SnippetItem(
            item_id=1,
            zone=ZONE_SYMBOL,
            value="©",
            hint="copyright",
            created_at="2026-01-01T00:00:00+00:00",
            last_used_at=None,
            sort_index=0,
        ),
        SnippetItem(
            item_id=2,
            zone=ZONE_SYMBOL,
            value="—",
            hint="em dash",
            created_at="2026-01-01T00:00:00+00:00",
            last_used_at=None,
            sort_index=1,
        ),
        SnippetItem(
            item_id=3,
            zone=ZONE_SYMBOL,
            value="-",
            hint="hyphen",
            created_at="2026-01-01T00:00:00+00:00",
            last_used_at=None,
            sort_index=2,
        ),
        SnippetItem(
            item_id=4,
            zone=ZONE_SYMBOL,
            value="–",
            hint="en dash",
            created_at="2026-01-01T00:00:00+00:00",
            last_used_at=None,
            sort_index=3,
        ),
        SnippetItem(
            item_id=5,
            zone=ZONE_SYMBOL,
            value="−",
            hint="minus",
            created_at="2026-01-01T00:00:00+00:00",
            last_used_at=None,
            sort_index=4,
        ),
    ]
    assert dash_length_rank("-") == 0
    assert dash_length_rank("©") is None
    ordered = [item.value for item in sort_items(items, SORT_ALPHA, descending=False)]
    assert ordered[:4] == ["-", "−", "–", "—"]
    assert ordered[4:] == ["©"]


def test_item_matches_search_ignores_case_and_layout() -> None:
    assert item_matches_search("🐞 Fix ruff check issues", "", "FIX")
    assert item_matches_search("Quick paste", "", "зфыеу")
    assert item_matches_search("#ffffff", "white color in icons", "white")
    assert not item_matches_search("Add", "", "zzzz")


def test_parse_value_hint_line_and_bulk_lines() -> None:
    assert parse_value_hint_line("— | Век живи — век учись. | Тире") == (
        "—",
        "Век живи — век учись. | Тире",
    )
    assert parse_value_hint_line("#ffffff: white color in icons") == ("#ffffff", "white color in icons")
    assert parse_bulk_lines("➕ Add\n\n🐞 Fix\n", "phrase") == [("➕ Add", ""), ("🐞 Fix", "")]
    assert parse_bulk_lines("© | Знак копирайта\n", ZONE_SYMBOL) == [("©", "Знак копирайта")]
    assert parse_bulk_lines("#de2b26: logo\n", ZONE_COLOR) == [("#de2b26", "logo")]


def test_display_text_adds_hint_brackets() -> None:
    assert display_text("—", "Век живи — век учись. | Тире", ZONE_SYMBOL) == ("— [Век живи — век учись. | Тире]")


def test_hint_tooltip_strips_wrapping_brackets() -> None:
    assert hint_tooltip("Век живи — век учись. | Тире") == "Век живи — век учись. | Тире"
    assert hint_tooltip("[Тире]") == "Тире"
    assert hint_tooltip("  [Короткое тире]  ") == "Короткое тире"
    assert hint_tooltip("", "—") == "—"


def test_color_hex_label_strips_brackets() -> None:
    assert color_hex_label("#ffffff") == "#ffffff"
    assert color_hex_label("  [#de2b26]  ") == "#de2b26"
    assert color_hex_label("[#122a3a]") == "#122a3a"


def test_chip_border_color_is_darker() -> None:
    fill = QColor("#ffffff")
    border = chip_border_color(fill)
    assert border.lightness() < fill.lightness()


def test_recover_sql_matches_builder_and_creates_seed(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    assert _RECOVER_SQL.is_file()
    assert _RECOVER_SQL.read_text(encoding="utf-8") == build_recover_sql()
    db_path = tmp_path / "snippets.db"
    assert QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(_RECOVER_SQL))
    manager = DatabaseManager(str(db_path))
    try:
        assert manager.table_exists("items")
        assert manager.table_exists("zone_sort")
        phrases = manager.list_items("phrase")
        emojis = manager.list_items("emoji")
        symbols = manager.list_items("symbol")
        colors = manager.list_items("color")
        assert [item.value for item in phrases] == list(SEED_PHRASES)
        assert [item.value for item in emojis] == seed_emojis()
        assert [item.value for item in symbols[:4]] == ["-", "−", "–", "—"]
        assert "дефис" in symbols[0].hint
        assert "Тире" in symbols[3].hint
        assert colors[0].value == "#ffffff"
        assert colors[-1].value == "#66442b"
        assert ensure_seed_emojis(manager) == 0
    finally:
        manager.close()


def test_ensure_seed_emojis_inserts_missing(qapp: QApplication, tmp_path: Path) -> None:  # noqa: ARG001
    db_path = tmp_path / "snippets.db"
    assert QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(_RECOVER_SQL))
    manager = DatabaseManager(str(db_path))
    try:
        first = manager.list_items("emoji")[0]
        assert manager.delete_item(first.item_id)
        assert ensure_seed_emojis(manager) == 1
        assert first.value in {item.value for item in manager.list_items("emoji")}
        assert ensure_seed_emojis(manager) == 0
    finally:
        manager.close()


def test_emoji_zone_items_have_icon_without_caption(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_EMOJI, title="Emoji")
    panel.set_items(
        [
            SnippetItem(
                item_id=1,
                zone=ZONE_EMOJI,
                value="😀",
                hint="",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    item = panel._list.item(0)
    assert item is not None
    assert item.text() == ""
    assert not item.icon().isNull()
    assert panel._list.font().family() == MONO_FONT_FAMILY
    panel.close()


def test_list_highlight_is_flat_without_inverted_text(qapp: QApplication) -> None:
    assert qapp is not None
    assert _SELECTION_BG == "#e9e9e9"
    assert _SELECTION_OUTLINE == "#b0b0b0"
    assert "item:hover" in _LIST_SELECTION_STYLE
    assert "border: none" in _LIST_SELECTION_STYLE
    assert "#6a6a6a" not in _LIST_SELECTION_STYLE
    emoji = ZonePanel(zone=ZONE_EMOJI, title="Emoji")
    assert isinstance(emoji._list.itemDelegate(), IconItemDelegate)
    phrase = ZonePanel(zone=ZONE_PHRASE, title="Phrases")
    highlight = phrase._list.palette().color(QPalette.ColorRole.Highlight)
    assert highlight.name() == "#e9e9e9"
    text = phrase._list.palette().color(QPalette.ColorRole.Text)
    highlighted_text = phrase._list.palette().color(QPalette.ColorRole.HighlightedText)
    assert highlighted_text == text
    emoji.close()
    phrase.close()


def test_symbol_zone_items_are_icon_buttons_with_hint_tooltip(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_SYMBOL, title="Add symbol", show_add=True)
    panel.set_items(
        [
            SnippetItem(
                item_id=1,
                zone=ZONE_SYMBOL,
                value="—",
                hint="Век живи — век учись. | Тире",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    item = panel._list.item(0)
    assert item is not None
    assert item.text() == ""
    assert not item.icon().isNull()
    assert item.toolTip() == "Век живи — век учись. | Тире"
    assert "[" not in item.toolTip()
    assert "]" not in item.toolTip()
    panel.close()


def test_color_zone_items_have_no_bracket_text(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_COLOR, title="Add color", show_add=True)
    panel.set_items(
        [
            SnippetItem(
                item_id=1,
                zone=ZONE_COLOR,
                value="#ffffff",
                hint="white color in icons",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    item = panel._list.item(0)
    assert item is not None
    assert item.text() == ""
    assert "[" not in item.text()
    assert "]" not in item.text()
    panel.close()


def test_highlight_item_delegate_paints_text(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_PHRASE, title="Phrases")
    panel.set_items(
        [
            SnippetItem(
                item_id=1,
                zone=ZONE_PHRASE,
                value="hello",
                hint="",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    item = panel._list.item(0)
    assert item is not None
    pixmap = QPixmap(240, 32)
    pixmap.fill(Qt.GlobalColor.white)
    painter = QPainter(pixmap)
    option = QStyleOptionViewItem()
    option.rect = QRect(0, 0, 240, 32)
    option.widget = panel._list
    option.text = "hello"
    option.displayAlignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    option.palette = panel._list.palette()
    option.state = QStyle.StateFlag.State_Enabled
    HighlightItemDelegate(panel._list).paint(painter, option, panel._list.indexFromItem(item))
    painter.end()
    panel.set_input_match("hello")
    assert panel.item_matches_input(panel._items[0])
    panel.set_input_match("")
    assert not panel.item_matches_input(panel._items[0])
    panel.close()


def test_zone_panel_add_button_emits_add_requested(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_EMOJI, title="Add emoji", show_add=True)
    requested: list[bool] = []
    panel.add_requested.connect(lambda: requested.append(True))
    add_button = next(button for button in panel.findChildren(QToolButton) if button.toolTip() == "Add emoji")
    assert add_button.text() == ""
    assert add_button.autoRaise()
    add_button.click()
    assert requested == [True]
    panel.close()


def test_phrase_zone_clear_filter_empties_search(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_PHRASE, title="Add phrase", show_add=True)
    panel.set_filter_query("old query")
    assert panel.filter_query() == "old query"
    panel.clear_filter()
    assert panel.filter_query() == ""
    panel.close()


def test_on_snippets_is_quick_launcher_action() -> None:
    assert OnSnippets.quick_launcher is True
    assert OnSnippets.title == "Quick paste"
    assert OnSnippets in list(iter_menu_structure(get_menu_structure()))


def test_phrase_filter_arrows_select_visible(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_PHRASE, title="Add phrase", show_add=True)
    panel.set_items([_item(1, "Alpha"), _item(2, "Alpine"), _item(3, "Beta")])
    panel.set_filter_query("Al")
    assert panel._list.item(2) is not None
    assert panel._list.item(2).isHidden()
    assert panel.move_visible(1)
    assert panel.current_snippet() is not None
    assert panel.current_snippet().value == "Alpha"
    assert panel.filter_query() == "Al"
    assert panel._list.item(1) is not None
    assert not panel._list.item(1).isHidden()
    assert panel.move_visible(1)
    assert panel.current_snippet() is not None
    assert panel.current_snippet().value == "Alpine"
    panel.close()


def test_shared_input_arrows_select_visible_and_fill_field(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert qapp is not None
    monkeypatch.setattr(SnippetsDialog, "_init_database", lambda _dialog: None)
    dialog = SnippetsDialog()
    dialog._phrases.set_items([_item(1, "Alpha"), _item(2, "Alpine"), _item(3, "Beta")])
    dialog.show()
    QApplication.processEvents()
    dialog._activate_zone(ZONE_PHRASE, select_item=False)
    dialog._input.setText("Al")
    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
    assert QApplication.sendEvent(dialog._input, event)
    assert dialog._phrases.current_snippet() is not None
    assert dialog._phrases.current_snippet().value == "Alpha"
    assert dialog._input.text() == "Alpha"
    assert dialog._phrases.item_matches_input(dialog._phrases.current_snippet())
    assert QApplication.sendEvent(dialog._input, event)
    assert dialog._phrases.current_snippet() is not None
    assert dialog._phrases.current_snippet().value == "Alpine"
    assert dialog._input.text() == "Alpine"
    assert dialog._phrases.item_matches_input(dialog._phrases.current_snippet())
    dialog.close()


def test_phrase_enter_without_selection_activates_first(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_PHRASE, title="Add phrase", show_add=True)
    activated: list[SnippetItem] = []
    panel.item_activated.connect(activated.append)
    panel.set_items([_item(1, "Alpha"), _item(2, "Beta")])
    panel.activate_current_or_first()
    assert [item.value for item in activated] == ["Alpha"]
    panel.close()


def test_emoji_prepare_keyboard_focus_restores_remembered(qapp: QApplication) -> None:
    assert qapp is not None
    panel = ZonePanel(zone=ZONE_EMOJI, title="Add emoji", show_add=True)
    panel.set_items(
        [
            SnippetItem(
                item_id=1,
                zone=ZONE_EMOJI,
                value="😀",
                hint="",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
            SnippetItem(
                item_id=2,
                zone=ZONE_EMOJI,
                value="🐞",
                hint="",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=1,
            ),
        ],
    )
    panel.prepare_keyboard_focus()
    assert panel.current_snippet() is not None
    assert panel.current_snippet().value == "😀"
    panel.select_row(1)
    panel._list.clearSelection()
    panel._list.setCurrentRow(-1)
    panel.prepare_keyboard_focus()
    assert panel.current_snippet() is not None
    assert panel.current_snippet().value == "🐞"
    panel.close()


def test_snippets_tab_cycles_shared_input_emoji_symbols_colors(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert qapp is not None
    monkeypatch.setattr(SnippetsDialog, "_init_database", lambda _dialog: None)
    dialog = SnippetsDialog()
    dialog._phrases.set_items([_item(1, "Alpha")])
    dialog._emoji.set_items(
        [
            SnippetItem(
                item_id=10,
                zone=ZONE_EMOJI,
                value="😀",
                hint="",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    dialog._symbols.set_items(
        [
            SnippetItem(
                item_id=20,
                zone=ZONE_SYMBOL,
                value="—",
                hint="em dash",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    dialog._colors.set_items(
        [
            SnippetItem(
                item_id=30,
                zone=ZONE_COLOR,
                value="#ffffff",
                hint="white",
                created_at="2026-01-01T00:00:00+00:00",
                last_used_at=None,
                sort_index=0,
            ),
        ],
    )
    dialog.show()
    QApplication.processEvents()
    dialog._activate_zone(ZONE_PHRASE, select_item=False)
    QApplication.processEvents()
    assert dialog._input.hasFocus()
    assert dialog._input.placeholderText() == "Phrases"
    assert dialog._input.placeholderText() != "Filter and search…"
    assert dialog._input.text() == ""
    assert "padding" in dialog._input.styleSheet()
    assert dialog._input.minimumHeight() >= dialog._input.fontMetrics().height() + 22
    dialog.focusNextPrevChild(True)  # noqa: FBT003
    QApplication.processEvents()
    assert dialog._input.hasFocus()
    assert dialog._input.text() == "😀"
    assert dialog._emoji.current_snippet() is not None
    assert dialog._emoji.item_matches_input(dialog._emoji.current_snippet())
    assert not dialog._phrases.item_matches_input(dialog._phrases._items[0] if dialog._phrases._items else None)
    dialog.focusNextPrevChild(True)  # noqa: FBT003
    QApplication.processEvents()
    assert dialog._input.hasFocus()
    assert dialog._input.text() == "—"
    assert dialog._symbols.item_matches_input(dialog._symbols.current_snippet())
    dialog.focusNextPrevChild(True)  # noqa: FBT003
    QApplication.processEvents()
    assert dialog._input.hasFocus()
    assert dialog._input.text() == "#ffffff"
    assert dialog._colors.item_matches_input(dialog._colors.current_snippet())
    dialog.focusNextPrevChild(True)  # noqa: FBT003
    QApplication.processEvents()
    assert dialog._input.hasFocus()
    assert dialog._input.placeholderText() == "Phrases"
    dialog.close()


def test_example_config_binds_ctrl_shift_f3() -> None:
    data = json.loads(_EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    assert data["sqlite_snippets"].endswith("snippets.db")
    matching = [entry for entry in data["hotkeys"] if entry.get("action") == "OnSnippets"]
    assert matching
    assert "Ctrl+Shift+F3" in matching[0]["hotkeys"]
